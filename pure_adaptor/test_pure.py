from pure import versioned_pure_interface

environment = 'local_pure_test'
pure = versioned_pure_interface('v59')

pure_api = pure.API(
    'https://riswebtest.st-andrews.ac.uk/ws/api/59/',
    'f39e70b7-c2b2-48a2-8175-92ccc6978128'
)


datasets = pure_api.list_all_datasets()

# adaptor_state = AdaptorStateStore(environment)
# Retrieve details of last run of this adaptor
# datasets_modified_after = adaptor_state.latest_date()
# Get all datasets from the API that have changed since the last run

# Information about title of dataset and associated files required.

# Process all datasets:
# - Download dataset files
# - Push all files and metadata to s3
# - Make a create or update message
# - Push message to stream

# Get the most recent of the changed datasets and create highwater mark
# from that.

datasets.sort(key=lambda ds: ds.modified_date, reverse=True)
print(datasets[0].modified_date)


# state_store = AdaptorStateStore(environment)

# hashr = DatasetHasher()
# for ds in datasets:
#    ds_info = state_store.get_dataset_info(ds.uuid)
#    watched_fields = ds_info.get('dataset_watched_fields')

#    if ds.files:
#        ds.download_files()
#        ds.file_checksums = hashr.file_checksums(ds)
#        ds_info = dataset_for_state_store(ds)
#        state_store.put_dataset_info(ds_info)"""
