"""Test cases for voluptuous-serialize library."""

from __future__ import annotations

import re
from enum import Enum
from typing import Any

import pytest
import voluptuous as vol

from voluptuous_serialize import UNSUPPORTED, UnsupportedType, convert


def test_int_schema() -> None:
    for value in int, vol.Coerce(int):
        assert convert(vol.Schema(value)) == {"type": "integer"}


def test_str_schema() -> None:
    for value in str, vol.Coerce(str):
        assert convert(vol.Schema(value)) == {"type": "string"}


def test_float_schema() -> None:
    for value in float, vol.Coerce(float):
        assert convert(vol.Schema(value)) == {"type": "float"}


def test_bool_schema() -> None:
    for value in bool, vol.Coerce(bool):
        assert convert(vol.Schema(value)) == {"type": "boolean"}


def test_integer_clamp() -> None:
    assert convert(
        vol.Schema(vol.All(vol.Coerce(int), vol.Clamp(min=100, max=1000)))
    ) == {
        "type": "integer",
        "valueMin": 100,
        "valueMax": 1000,
    }


def test_length() -> None:
    assert convert(
        vol.Schema(vol.All(vol.Coerce(str), vol.Length(min=100, max=1000)))
    ) == {
        "type": "string",
        "lengthMin": 100,
        "lengthMax": 1000,
    }


def test_datetime() -> None:
    assert convert(vol.Schema(vol.Datetime())) == {
        "type": "datetime",
        "format": "%Y-%m-%dT%H:%M:%S.%fZ",
    }


def test_in() -> None:
    assert convert(vol.Schema(vol.In(["beer", "wine"]))) == {
        "type": "select",
        "options": [
            ("beer", "beer"),
            ("wine", "wine"),
        ],
    }


def test_in_dict() -> None:
    assert convert(
        vol.Schema(
            vol.In({"en_US": "American English", "zh_CN": "Chinese (Simplified)"})
        )
    ) == {
        "type": "select",
        "options": [
            ("en_US", "American English"),
            ("zh_CN", "Chinese (Simplified)"),
        ],
    }


@pytest.mark.parametrize("base_required", [True, False])
def test_dict(base_required: bool) -> None:
    assert [
        {
            "name": "name",
            "type": "string",
            "lengthMin": 5,
            "required": True,
        },
        {
            "name": "age",
            "type": "integer",
            "valueMin": 18,
            "required": base_required,
        },
        {
            "name": "hobby",
            "type": "string",
            "default": "not specified",
            "required": False,
            "optional": True,
        },
    ] == convert(
        vol.Schema(
            {
                vol.Required("name"): vol.All(str, vol.Length(min=5)),
                "age": vol.All(vol.Coerce(int), vol.Range(min=18)),
                vol.Optional("hobby", default="not specified"): str,
            },
            required=base_required,
        )
    )


def test_marker_description() -> None:
    assert convert(
        vol.Schema(
            {
                vol.Required("name", description="Description of name"): str,
            }
        )
    ) == [
        {
            "name": "name",
            "type": "string",
            "description": "Description of name",
            "required": True,
        }
    ]


def test_lower() -> None:
    assert convert(vol.Schema(vol.All(vol.Lower, str))) == {
        "type": "string",
        "lower": True,
    }


def test_upper() -> None:
    assert convert(vol.Schema(vol.All(vol.Upper, str))) == {
        "type": "string",
        "upper": True,
    }


def test_capitalize() -> None:
    assert convert(vol.Schema(vol.All(vol.Capitalize, str))) == {
        "type": "string",
        "capitalize": True,
    }


def test_title() -> None:
    assert convert(vol.Schema(vol.All(vol.Title, str))) == {
        "type": "string",
        "title": True,
    }


def test_strip() -> None:
    assert convert(vol.Schema(vol.All(vol.Strip, str))) == {
        "type": "string",
        "strip": True,
    }


def test_email() -> None:
    assert convert(vol.Schema(vol.All(vol.Email, str))) == {
        "type": "string",
        "format": "email",
    }


def test_url() -> None:
    assert convert(vol.Schema(vol.All(vol.Url, str))) == {
        "type": "string",
        "format": "url",
    }


def test_fqdnurl() -> None:
    assert convert(vol.Schema(vol.All(vol.FqdnUrl, str))) == {
        "type": "string",
        "format": "fqdnurl",
    }


def test_maybe() -> None:
    assert convert(vol.Schema(vol.Maybe(str))) == {
        "type": "string",
        "allow_none": True,
    }


def test_custom_serializer() -> None:
    def custem_serializer(schema: Any) -> dict[str, str] | UnsupportedType:
        if schema is str:
            return {"type": "a string!"}
        return UNSUPPORTED

    assert convert(
        vol.Schema(vol.All(vol.Upper, str)), custom_serializer=custem_serializer
    ) == {
        "type": "a string!",
        "upper": True,
    }


def test_constant() -> None:
    for value in True, False, "Hello", 1:
        assert {"type": "constant", "value": value} == convert(vol.Schema(value))


def test_enum() -> None:
    class TestEnum(Enum):
        ONE = "one"
        TWO = 2

    assert convert(vol.Schema(vol.Coerce(TestEnum))) == {
        "type": "select",
        "options": [
            ("one", "one"),
            (2, 2),
        ],
    }


class UnsupportedClass:
    pass


@pytest.mark.parametrize(
    "unsupported_schema",
    [
        None,
        object,
        list,
        set,
        frozenset,
        tuple,
        UnsupportedClass,
        [],
        vol.IsFalse(),
        vol.IsTrue(),
        vol.Boolean(),
        vol.Any(1, 2, 3, msg="Expected 1 2 or 3"),
        vol.Any("true", "false", vol.All(vol.Any(int, bool), vol.Coerce(bool))),
        vol.Union(
            {"type": "a", "a_val": "1"},
            {"type": "b", "b_val": "2"},
            discriminant=lambda val, alt: filter(
                lambda v: v["type"] == val["type"], alt
            ),
        ),
        vol.Match(r"^0x[A-F0-9]+$"),
        vol.Replace("hello", "goodbye"),
        vol.IsFile(),
        vol.IsDir(),
        vol.PathExists(),
        vol.NotIn(["beer", "wine"]),
        vol.Contains(1),
        vol.ExactSequence([str, int, list, list]),
        vol.Unique(),
        vol.Equal(1),
        vol.Unordered([2, 1]),
        vol.Number(precision=6, scale=2),
        vol.SomeOf(min_valid=2, validators=[vol.Range(1, 5), vol.Any(float, int), 6.6]),
    ],
)
def test_unsupported_schema(unsupported_schema: Any) -> None:
    with pytest.raises(
        ValueError,
        # the full error message is matched to make sure
        # the outer schema raised instead of some sub-part
        match=re.escape(f"Unable to convert schema: {unsupported_schema}"),
    ):
        convert(vol.Schema(unsupported_schema))


@pytest.mark.parametrize(
    "unsupported_schema",
    [
        vol.All({"a": int}),
        vol.All(
            vol.Schema({vol.Required("a"): int}),
        ),
        {
            "name": str,
            "position": {
                "lat": float,
                "lon": float,
            },
        },
    ],
)
def test_unsupported_subschema(unsupported_schema: Any) -> None:
    with pytest.raises(
        ValueError,
        match=r"^Unable to convert .*schema:",
    ):
        convert(vol.Schema(unsupported_schema))
