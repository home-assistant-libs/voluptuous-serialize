from collections import OrderedDict
import voluptuous as vol
import voluptuous_serialize

s = vol.Schema(vol.Object({
    vol.Required('person', description="a person object"): {
        vol.Required('name', description="the name of the person"): vol.All(str, vol.Length(min=5)),
        vol.Optional('age', description="the age of the person"): vol.All(vol.Coerce(int), vol.Range(min=18)),
        vol.Optional('hobby', description="the hobby of the person"): str
    }
}))

print(voluptuous_serialize.proto(s))
