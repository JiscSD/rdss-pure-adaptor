from pure import versioned_pure_interface
import json
import jsonschema
import sys


def the_great_filter(json):

    def _dict_iter(item):
        new_dict = {}
        for key, value in item.items():
            val = _or(value)
            if val != '':
                new_dict[key] = val
        return new_dict

    def _list_iter(items):
        return [_or(i) for i in items]

    def _or(item):
        if type(item) == list:
            return _list_iter(item)
        if type(item) == dict:
            return _dict_iter(item)
        else:
            return item

    return _or(json)


def open_json(path):
    with open(path, 'r') as json_in:
        input_json = json.loads(json_in.read())
    return input_json


def main():

    pure = versioned_pure_interface('v59')
    dataset_json_file = sys.argv[1]
    schema_json_file = sys.argv[2]
    input_json = open_json(dataset_json_file)
    json_schema = open_json(schema_json_file)

    if type(input_json) == list:
        datasets = [pure.Dataset(p) for p in input_json]
    else:
        datasets = [pure.Dataset(input_json)]

    cdm_datasets = []
    for ds in datasets:
        filtered_json = the_great_filter(ds.rdss_canonical_metadata)
        jsonschema.validate(filtered_json, json_schema)
        cdm_datasets.append(filtered_json)

    with open('CDM_st_andrews.json', 'w') as json_out:
        json_out.write(json.dumps(cdm_datasets, indent=2))


if __name__ == '__main__':
    main()
