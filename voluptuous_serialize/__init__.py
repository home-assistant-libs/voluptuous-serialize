"""Module to convert voluptuous schemas to dictionaries."""

from __future__ import annotations

from collections.abc import Mapping
from enum import Enum
from typing import Any, Callable, Final

import voluptuous as vol

TYPES_MAP: Final[dict[type, str]] = {
    int: "integer",
    str: "string",
    float: "float",
    bool: "boolean",
}


class UnsupportedType(Enum):
    """Singleton type for use with not set sentinel values."""

    _singleton = 0


UNSUPPORTED = UnsupportedType._singleton  # noqa: SLF001


def convert(
    schema: Any,
    *,
    custom_serializer: (
        Callable[[Any], dict[str, Any] | list[dict[str, Any]] | UnsupportedType] | None
    ) = None,
) -> dict[str, Any] | list[dict[str, Any]]:
    """Convert a voluptuous schema to a json serializable object."""
    # pylint: disable=too-many-return-statements,too-many-branches
    base_required = False  # vol.Schema default

    if isinstance(schema, vol.Schema):
        base_required = schema.required
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

            pval = convert(value, custom_serializer=custom_serializer)
            if isinstance(pval, list):
                # nested Mapping schemas are not supported
                raise ValueError(f"Unable to convert nested mapping schema: {value}")
            pval["name"] = pkey
            if description is not None:
                pval["description"] = description

            if isinstance(key, (vol.Required, vol.Optional)):
                pval["required"] = isinstance(key, vol.Required)

                # for backward compatibility
                pval[key.__class__.__name__.lower()] = True

                if not isinstance(key.default, vol.Undefined):
                    pval["default"] = key.default()
            else:
                pval["required"] = base_required

            val.append(pval)

        return val

    if isinstance(schema, vol.All):
        val = {}
        for validator in schema.validators:
            pval = convert(validator, custom_serializer=custom_serializer)
            if isinstance(pval, list):
                # Mapping schemas in vol.All are not supported
                raise ValueError(
                    f"Unable to convert `voluptuous.All` subschema: {validator}"
                )
            val.update(pval)
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
            "options": [(item, item) for item in schema.container],  # type: ignore[attr-defined]
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
            if isinstance(result, list):
                # Mapping schemas in vol.Any are not supported
                raise ValueError(
                    f"Unable to convert `voluptuous.Any` subschema: {schema}"
                )
            result["allow_none"] = True
            return result

    if isinstance(schema, vol.Coerce):
        schema = schema.type

    if isinstance(schema, type):
        if schema in TYPES_MAP:
            return {"type": TYPES_MAP[schema]}
        if issubclass(schema, Enum):
            return {
                "type": "select",
                "options": [(item.value, item.value) for item in schema],
            }

    if isinstance(schema, (str, int, float, bool)):
        return {"type": "constant", "value": schema}

    raise ValueError(f"Unable to convert schema: {schema}")
