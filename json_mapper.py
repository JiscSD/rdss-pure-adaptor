
class JSONMapper(object):

    _mappings = ()

    def _get_path(self, json_dict, path):
        value = json_dict
        for key in path:
            if value:
                if type(value) is list:
                    value = value[0]
                value = value.get(key, None)
            else:
                break
        return value

    def _map_value(self, json_dict, mapping):
        map_key, path = mapping
        value = self._get_path(json_dict, path)
        if value:
            return (map_key, value)
        else:
            return ()

    def remap(self, json_dict):
        key_value_pairs = (self._map_value(json_dict, mapping)
                for mapping in self._mappings)
        return dict(k_v for k_v in key_value_pairs if k_v)

class PersonMapper(JSONMapper):
    _mappings = (
            ('personUUID', ('person' , 'uuid')),
            ('personUUID', ('externalPerson' , 'uuid')),
            ('personGivenName', ('person', 'name', 'value')),
            #('personIdentifier', (' ',)),
            ('personRole', ('personRole' , 'value')),
            ('personCn', ('name', 'firstName')),
            ('personEntitlement', ('person', 'employmentType',)),
            #('personAffiliation', ( ,)),
            ('personSn', ('name', 'lastName')),
            ('personTelephoneNumber', ('person', 'phone')),
            ('personMail', ('person' , 'email')),
            ('personOu', ('organisationalUnits', 'name', 'value'))
            )
