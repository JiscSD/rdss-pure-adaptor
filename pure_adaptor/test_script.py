from pure import versioned_pure_interface
from adaptor.messages import MetadataCreate
import json
import sys
import os
import logging

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

api_url = 'https://riswebtest.st-andrews.ac.uk/ws/api/59/'
api_key = 'f39e70b7-c2b2-48a2-8175-92ccc6978128'

pure = versioned_pure_interface('v59')
pure_api = pure.API(api_url, api_key)

datasets = pure_api.list_all_datasets()

message_creator = MetadataCreate('local_test_script')

out_dir = '/home/fmcc/pure_datasets/'
for ds in datasets:
    f_path = os.path.join(out_dir, '{}.json'.format(ds.uuid))
    with open(f_path, 'w') as json_out:
        json_out.write(json.dumps(ds.original_metadata, indent=2))
    # ds.download_files()
    # message = message_creator.generate(ds.rdss_canonical_metadata)
    # message.as_json
