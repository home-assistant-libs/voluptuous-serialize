# Voluptuous Serialize

Convert Voluptuous schemas to json serializable objects.

```python
import voluptuous as vol
from voluptuous_serialize import convert

schema = vol.Schema(
    {
        vol.Required("name"): vol.All(str, vol.Length(min=5)),
        vol.Required("age"): vol.All(vol.Coerce(int), vol.Range(min=18)),
        vol.Optional("hobby", default="not specified"): str,
    }
)
result = convert(schema)
```

becomes

_(dictionaries become lists to guarantee order of properties)_

```json
[
  {
    "name": "name",
    "type": "string",
    "lengthMin": 5,
    "required": true,
  },
  {
    "name": "age",
    "type": "integer",
    "valueMin": 18,
    "required": true,
  },
  {
    "name": "hobby",
    "type": "string",
    "default": "not specified",
    "required": false,
    "optional": true,  // This is deprecated. Please use "required" key instead.
  }
]
```

See the tests for more examples.

## Custom serializer

You can pass a custom serializer to be able to process custom validators. If the serializer returns `UNSUPPORTED`, it will return to normal processing.

```python
from typing import Any
from voluptuous_serialize import UNSUPPORTED, UnsupportedType, convert

def custom_convert(value: Any) -> dict[str, str] | UnsupportedType:
    if value is my_custom_validator:
        return {'type': 'custom_validator'}
        
    return UNSUPPORTED

convert(value, custom_serializer=custom_convert)
```
