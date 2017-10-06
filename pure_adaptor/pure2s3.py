"""pure2s3:
    A script to pull a dataset by UUID from St. Andrews Pure Test API,
    transform the dataset metadata to the RDSS canonical format and
    push the resulting data and metadata to the test s3 bucket.
Usage:
    pure2s3 --api_key=<api_key> <dataset_uuid>
    pure2s3 --help

Options:
    -h --help     Show this screen.
    --api_url The base url endpoint for the PURE API.
    --api_version The PURE API version being targeted.
    --api_key The API key required for authentication with Pure.
    --upload_bucket The s3 bucket to which the metadata and dataset will
      be uploaded.
    --bucket_prefix A key prefix for the upload bucket.
"""
from docopt import docopt
from pure import versioned_pure_interface
from s3.s3_bucket import BucketUploader


def main():
    args = docopt(__doc__, version='pure2s3 0.1.0')

    uuid = args.get('<dataset_uuid>')

    api_url = args.get(
        '--api_url', 'https://riswebtest.st-andrews.ac.uk/ws/api/59/')
    api_version = args.get('--api_version', 'v59')
    api_key = args.get('--api_key')
    if not api_key:
        raise ValueError(
            'An API key is required to communicate with the PURE API')
    upload_bucket = args.get(
        '--upload_bucket', 'testdata.researchdata.alpha.jisc.ac.uk')
    bucket_prefix = args.get('--bucket_prefix', 'unsorted/pure_st_andrews')

    pure = versioned_pure_interface(api_version)
    pure_api = pure.API(api_url, api_key)
    upload_manager = BucketUploader(upload_bucket, bucket_prefix)

    dataset = pure_api.get_dataset(uuid)
    dataset.download_files()

    for file_path in dataset.local_files:
        upload_manager.upload_file(dataset.doi_upload_key, file_path)

    upload_manager.upload_json_obj(
        dataset.doi_upload_key,
        'original_pure{}_metadata.json'.format(api_version),
        dataset.original_metadata
    )
    upload_manager.upload_json_obj(
        dataset.doi_upload_key,
        'metadata.json',
        dataset.rdss_canonical_metadata
    )


if __name__ == '__main__':
    main()
