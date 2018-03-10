"""Module to convert voluptuous schemas to dictionaries."""
import collections

import voluptuous as vol


TYPES_MAP = {
    int: 'integer',
    str: 'string',
    float: 'float',
    bool: 'boolean',
}


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
            pval['name'] = pkey
            if description is not None:
                pval['description'] = description

            if isinstance(key, (vol.Required, vol.Optional)):
                pval[key.__class__.__name__.lower()] = True

                if key.default is not vol.UNDEFINED:
                    pval['default'] = key.default()

            val.append(pval)

        return val

    if isinstance(schema, vol.All):
        val = {}
        for validator in schema.validators:
            val.update(convert(validator))
        return val

    elif isinstance(schema, (vol.Clamp, vol.Range)):
        val = {}
        if schema.min is not None:
            val['value-min'] = schema.min
        if schema.max is not None:
            val['value-max'] = schema.max
        return val

    elif isinstance(schema, vol.Length):
        val = {}
        if schema.min is not None:
            val['length-min'] = schema.min
        if schema.max is not None:
            val['length-max'] = schema.max
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

    if schema in TYPES_MAP:
        return {'type': TYPES_MAP[schema]}

    raise ValueError('Unable to convert schema: {}'.format(schema))
