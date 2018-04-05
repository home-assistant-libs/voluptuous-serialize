"""Module to convert voluptuous schemas to dictionaries."""
import collections

import voluptuous as vol


def convert(schema):
    """Convert a voluptuous schema to a dictionary."""
    if isinstance(schema, vol.Schema):
        schema = schema.schema

    if isinstance(schema, collections.Mapping):
        val = []

        for key, value in schema.items():
            description = None
            if isinstance(key, vol.Marker):
                pkey = key.schema
                description = key.description
            else:
                pkey = key

            pval = convert(value)
            if isinstance(pval, list):
                pval = {'list': pval}
            pval['name'] = pkey
            if description is not None:
                pval['description'] = description

            if isinstance(key, (vol.Required, vol.Optional)):
                pval[key.__class__.__name__.lower()] = True

                if key.default is not vol.UNDEFINED and not isinstance(key.default, vol.Undefined):
                    pval['default'] = key.default()

            val.append(pval)

        return val

    if isinstance(schema, vol.All):
        val = {}
        for validator in schema.validators:
            converted = convert(validator)
            if isinstance(converted, list):
                data = {'list': converted}
            else:
                data = converted

            val.update(data)
        return val

    elif isinstance(schema, (vol.Clamp, vol.Range)):
        val = {}
        if schema.min is not None:
            val['valueMin'] = schema.min
        if schema.max is not None:
            val['valueMax'] = schema.max
        return val

    elif isinstance(schema, vol.Length):
        val = {}
        if schema.min is not None:
            val['lengthMin'] = schema.min
        if schema.max is not None:
            val['lengthMax'] = schema.max
        return val

    elif isinstance(schema, vol.Datetime):
        return {
            'type': 'datetime',
            'format': schema.format,
        }

    elif isinstance(schema, vol.In):
        return {
            'type': 'select',
            'options': list(schema.container)
        }

    elif isinstance(schema, vol.Coerce):
        schema = schema.type

    return {'type': schema.__class__.__name__}
