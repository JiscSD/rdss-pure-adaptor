import boto3
import os
import logging
import zipfile

class Bucket:
    """
    Abstraction over s3 bucket which specifies files segment with a given
    prefix.
    """

    def __init__(self, bucket_name, prefix, local_path, profile=None):
        """
        :param str bucket_name: which bucket to use
        :param str prefix: bucket prefix in a question
        :param str local_path: where to download bucket contents on local FS
        :param str profile: if provided specifies which AWS profile to use
                            otherwise default one from ENV is used
        """
        self.bucket_name = bucket_name
        self.prefix = prefix
        self.local_path = local_path
        self.profile = profile or None

        # last prefix path part or bucket name to used as a top level
        # folder under storage path
        self._top_path_part = self.prefix.split('/')[-1] or self.bucket_name

    def _get_bucket(self):
        session = boto3.Session(profile_name=self.profile)
        s3 = session.resource('s3')
        return s3.Bucket(self.bucket_name)

    def key_without_prefix(self, key):
        """ Strip prefix from key.

        :param str key:
        :rtype: str
        """
        if not self.prefix:
            return key
        return os.path.join(*key.split(self.prefix)[1:]).lstrip('/')

    def download_path(self, key):
        """ Download path on local FS for a given key

        :param str key: s3 key
        :rtype: string
        """
        return os.path.join(
            self.local_path,
            self._top_path_part,
            self.key_without_prefix(key)
        )

    def download(self, dry_run=False):
        """ Download bucket contents under specified prefix supplied in
        constructor.

        * will try to create target folder if missing,
        * won't attempt to clean it
        * will try to rewrite existing files if any

        :return:
        """
        bucket = self._get_bucket()
        objects = bucket.objects.filter(Prefix=self.prefix)

        if dry_run:
            logging.info('dry run, files to download:')

        for obj in objects:
            file_path = self.download_path(obj.key)

            # make sure folder exists for given file
            dir_path = os.path.dirname(file_path)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)

            if dry_run:
                logging.info('* {}'.format(obj.key))
                continue

            bucket.download_file(obj.key, file_path)

    def zip(self):
        """ Zip contents and return archive path

        :rtype: str
        """

        zip_file_path = '{}.zip'.format(
            os.path.join(self.local_path, self._top_path_part)
        )
        zipper = Zip(zip_file_path)

        # using store folder, either provided or generated
        # during download step,
        #
        # path is calculated as store path + most last part of
        # the path in s3://bucket/prefix url
        root = os.path.join(self.local_path, self._top_path_part)

        # files put in archive with relative path to the walking root
        for dir_path, _, files in os.walk(root):
            rel_dir_path = os.path.relpath(dir_path, root)

            for file_name in files:
                # double check that we don't add archive to itself
                data_path = os.path.join(dir_path, file_name)
                if data_path == zip_file_path:
                    continue

                arc_path = os.path.join(rel_dir_path, file_name)

                zipper.add(data_path, arc_path)

        return zip_file_path


class Zip:
    """
    Helper class to make zip file
    """

    def __init__(self, file_name):
        """
        :param str file_name: zip file path
        """
        self.file_name = file_name

    def add(self, path, arcname):
        """ Add file to existing zip

        :param str path: file path on FS
        :param str arcname: path in archive
        """
        with zipfile.ZipFile(self.file_name, 'a') as f:
            f.write(path, arcname=arcname)


class BucketUploader:

    def __init__(self, bucket_name, prefix, profile=None):
        """
        :param str bucket_name: which bucket to use
        :param str prefix: bucket prefix in a question
        :param str profile: if provided specifies which AWS profile to use
                            otherwise default one from ENV is used
        """
        self.bucket_name = bucket_name
        self.prefix = prefix.rstrip('/')
        self.profile = profile or None

    def _get_bucket(self):
        session = boto3.Session(profile_name=self.profile)
        s3 = session.resource('s3')
        return s3.Bucket(self.bucket_name)

    def upload(self, source_file):
        """ Upload file to a given bucket segment if it is empty

        :param str source_file: file path to upload
        """
        bucket = self._get_bucket()

        # upload
        key = os.path.join(self.prefix, os.path.basename(source_file))
        with open(source_file, 'rb') as data:
            bucket.upload_fileobj(data, key)