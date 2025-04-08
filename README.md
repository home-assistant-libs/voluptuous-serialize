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

## Proto File Generation

[Protocol Buffers](https://developers.google.com/protocol-buffers/docs/proto) are a powerful tool
to describe structured data. In addition to the undocument json serialization it is useful to add
a proto serialization which can be used in many other contexts such as API client generation or
docs generation.

You can try it out via 

```python
python3 example.py > sample.proto
```

> A prerequisite is to install []() and [`protoc`](). This is an example install command for mac:
> ```shell
> brew install protobuf
> go install github.com/pseudomuto/protoc-gen-doc/cmd/protoc-gen-doc@latest
> ```

And then generate the docs via
```shell
protoc --doc_out=./docs --doc_opt=html,docs.html sample.proto
protoc --doc_out=./docs --doc_opt=markdown,docs.md sample.proto
```

Check out the docs in the [`/docs`](/docs) directory.
