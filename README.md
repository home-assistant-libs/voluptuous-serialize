### This is an experiment. Not production ready. Do not use.

# Voluptuous JSON (experiment)

This is an experiment to see if it is possible to easily convert voluptuous schemas to JSON.

Goal would be to create a set of Polymer components that can consume this data and generate a form that matches the expected data.

```python
vol.Schema({
    vol.Required('name'): vol.All(str, vol.Length(min=5)),
    vol.Required('age'): vol.All(vol.Coerce(int), vol.Range(min=18)),
    vol.Optional('hobby', default='not specified'): str
})
```

becomes

```json
{
  "name": {
    "type": "string",
    "length-min": 5,
    "required": true,
  },
  "age": {
    "type": "integer",
    "value-min": 18,
    "required": true,
  },
  "hobby": {
    "type": "string",
    "default": "not specified",
    "optional": true,
  }
}
```

See the tests for more examples.
