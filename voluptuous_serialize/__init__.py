"""Module to convert voluptuous schemas to dictionaries."""

from collections.abc import Mapping
from enum import Enum

import voluptuous as vol


TYPES_MAP = {
    int: "integer",
    str: "string",
    float: "float",
    bool: "boolean",
}

PROTO_TYPES_MAP = {
    "integer": "int32",
    "string": "string",
    "float": "float",
    "boolean": "bool"
}

UNSUPPORTED = object()


def convert(schema, *, custom_serializer=None):
    """Convert a voluptuous schema to a dictionary."""
    # pylint: disable=too-many-return-statements,too-many-branches
    if isinstance(schema, vol.Schema):
        schema = schema.schema

    if custom_serializer:
        val = custom_serializer(schema)
        if val is not UNSUPPORTED:
            return val

    if isinstance(schema, Mapping):
        val = []

        for key, value in schema.items():
            description = None
            if isinstance(key, vol.Marker):
                pkey = key.schema
                description = key.description
            else:
                pkey = key

            if not isinstance(pkey, str):
                if len(schema) != 1:
                    raise ValueError(
                        'Unable to convert schema: {}'.format(schema)
                    )
                return {
                    'type': 'mapping',
                    'key': convert(key),
                    'value': convert(value)
                }

            pval = convert(value, custom_serializer=custom_serializer)
            if isinstance(pval, list):
                pval = {'type': 'dictionary', 'dictionary': pval}
            pval['name'] = pkey
            if description is not None:
                pval["description"] = description

            if isinstance(key, (vol.Required, vol.Optional)):
                pval[key.__class__.__name__.lower()] = True

                if key.default is not vol.UNDEFINED:
                    pval["default"] = key.default()

            val.append(pval)

        return val

    if isinstance(schema, vol.All):
        val = {}
        for validator in schema.validators:
            val.update(convert(validator, custom_serializer=custom_serializer))
        return val

    if isinstance(schema, (vol.Clamp, vol.Range)):
        val = {}
        if schema.min is not None:
            val["valueMin"] = schema.min
        if schema.max is not None:
            val["valueMax"] = schema.max
        return val

    if isinstance(schema, vol.Length):
        val = {}
        if schema.min is not None:
            val["lengthMin"] = schema.min
        if schema.max is not None:
            val["lengthMax"] = schema.max
        return val

    if isinstance(schema, vol.Datetime):
        return {
            "type": "datetime",
            "format": schema.format,
        }

    if isinstance(schema, vol.In):
        if isinstance(schema.container, Mapping):
            return {
                "type": "select",
                "options": list(schema.container.items()),
            }
        return {
            "type": "select",
            "options": [(item, item) for item in schema.container],
        }

    if schema in (vol.Lower, vol.Upper, vol.Capitalize, vol.Title, vol.Strip):
        return {
            schema.__name__.lower(): True,
        }

    if schema in (vol.Email, vol.Url, vol.FqdnUrl):
        return {
            "format": schema.__name__.lower(),
        }

    # vol.Maybe
    if isinstance(schema, vol.Any):
        if len(schema.validators) == 2 and schema.validators[0] is None:
            result = convert(schema.validators[1], custom_serializer=custom_serializer)
            result["allow_none"] = True
            return result

    if isinstance(schema, vol.Coerce):
        schema = schema.type

    if schema in TYPES_MAP:
        return {"type": TYPES_MAP[schema]}

    if isinstance(schema, (str, int, float, bool)):
        return {"type": "constant", "value": schema}

    if issubclass(schema, Enum):
        return {
            "type": "select",
            "options": [(item.value, item.value) for item in schema],
        }

    raise ValueError("Unable to convert schema: {}".format(schema))


class Message:
    def __init__(self, entries, name):
        self.entries = entries
        self.name = name

    def __repr__(self):
        return """message {} {{
  {}
}}""".format(
            self.name,
            "  \n  ".join([str(entry) for entry in self.entries])
        )


class Entry:
    def __init__(self, entry, i=1):
        self.type = entry['type']
        self.name = entry['name']
        self.type = self.name if self.type == 'dictionary' else self.type
        self.description = entry.get('description', '')
        self.required = entry.get('required', False)
        self.i = i

    def __repr__(self):
        return "{}{} {} = {};{}".format(
            "required " if self.required else "optional ",
            PROTO_TYPES_MAP.get(self.type, self.type),
            self.name,
            self.i,
            " // {}".format(self.description) if self.description else ""
        )


def proto_convert(_list, name, i=1):
    entries = []
    ret = ""
    for entry in _list:
        entries.append(Entry(entry, i))
        i+=1
        if entry['type'] == 'dictionary':
            ret += str(proto_convert(entry['dictionary'], entry['name'], i)) + "\n"
    return ret + str(Message(entries, name)) + "\n"


def proto(schema, *, custom_serializer=None):
    _list = convert(schema, custom_serializer=custom_serializer)
    return """syntax = "proto2";

package sample;

""" + proto_convert(_list, "root")
