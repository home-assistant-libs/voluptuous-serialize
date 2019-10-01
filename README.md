# Voluptuous Serialize

Convert Voluptuous schemas to dictionaries so they can be serialized.

```python
from collections import OrderedDict

# Use OrderedDict instead of dict.
# Only starting Python 3.6+ are dictionaries ordered.
schema = OrderedDict()
schema[vol.Required('name')] = vol.All(str, vol.Length(min=5))
schema[vol.Required('age')] = vol.All(vol.Coerce(int), vol.Range(min=18))
schema[vol.Optional('hobby', default='not specified')] = str
schema = vol.Schema(schema)
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
    "optional": true,
  }
]
```

See the tests for more examples.

## Custom serializer

You can pass a custom serializer to be able to process custom validators. If the serializer returns `UNSUPPORTED`, it will return to normal processing.

```python

from voluptuous_serialize import UNSUPPORTED, convert

def custom_convert(value):
    if value is my_custom_validator:
        return {'type': 'custom_validator'}
        
    return UNSUPPORTED

convert(value, custom_serializer=custom_convert)
```
