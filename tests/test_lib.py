import voluptuous as vol

from voluptuous_serialize import convert


def test_int_schema():
    for value in int, vol.Coerce(int):
        assert {'type': 'integer'} == convert(vol.Schema(value))


def test_str_schema():
    for value in str, vol.Coerce(str):
        assert {'type': 'string'} == convert(vol.Schema(value))


def test_float_schema():
    for value in float, vol.Coerce(float):
        assert {'type': 'float'} == convert(vol.Schema(value))


def test_bool_schema():
    for value in bool, vol.Coerce(bool):
        assert {'type': 'boolean'} == convert(vol.Schema(value))


def test_integer_clamp():
    assert {
        'type': 'integer',
        'valueMin': 100,
        'valueMax': 1000,
    } == convert(vol.Schema(
            vol.All(vol.Coerce(int),
                    vol.Clamp(min=100, max=1000))))


def test_length():
    assert {
        'type': 'string',
        'lengthMin': 100,
        'lengthMax': 1000,
    } == convert(vol.Schema(
            vol.All(vol.Coerce(str),
                    vol.Length(min=100, max=1000))))


def test_datetime():
    assert {
        'type': 'datetime',
        'format': '%Y-%m-%dT%H:%M:%S.%fZ',
    } == convert(vol.Schema(vol.Datetime()))


def test_in():
    assert {
        'type': 'select',
        'options': [
            ('beer', 'beer'),
            ('wine', 'wine'),
        ],
    } == convert(vol.Schema(vol.In(['beer', 'wine'])))


def test_in_dict():
    assert {
        'type': 'select',
        'options': [
            ('en_US', 'American English'),
            ('zh_CN', 'Chinese (Simplified)'),
        ],
    } == convert(vol.Schema(vol.In(
        {'en_US': 'American English', 'zh_CN': 'Chinese (Simplified)'})))


def test_dict():
    assert [
        {
            'name': 'name',
            'type': 'string',
            'lengthMin': 5,
            'required': True,
        },
        {
            'name': 'age',
            'type': 'integer',
            'valueMin': 18,
            'required': True,
        },
        {
            'name': 'hobby',
            'type': 'string',
            'default': 'not specified',
            'optional': True,
        }
     ] == convert(vol.Schema({
            vol.Required('name'): vol.All(str, vol.Length(min=5)),
            vol.Required('age'): vol.All(vol.Coerce(int), vol.Range(min=18)),
            vol.Optional('hobby', default='not specified'): str
        }))


def test_marker_description():
    assert [{
        'name': 'name',
        'type': 'string',
        'description': 'Description of name',
        'required': True,
    }] == convert(vol.Schema({
        vol.Required('name', description='Description of name'): str,
    }))


def test_lower():
    assert {
        'type': 'string',
        'lower': True,
    } == convert(vol.Schema(vol.All(vol.Lower, str)))


def test_upper():
    assert {
        'type': 'string',
        'upper': True,
    } == convert(vol.Schema(vol.All(vol.Upper, str)))


def test_capitalize():
    assert {
        'type': 'string',
        'capitalize': True,
    } == convert(vol.Schema(vol.All(vol.Capitalize, str)))


def test_title():
    assert {
        'type': 'string',
        'title': True,
    } == convert(vol.Schema(vol.All(vol.Title, str)))


def test_strip():
    assert {
        'type': 'string',
        'strip': True,
    } == convert(vol.Schema(vol.All(vol.Strip, str)))


def test_email():
    assert {
        'type': 'string',
        'format': 'email',
    } == convert(vol.Schema(vol.All(vol.Email, str)))


def test_url():
    assert {
        'type': 'string',
        'format': 'url',
    } == convert(vol.Schema(vol.All(vol.Url, str)))


def test_fqdnurl():
    assert {
        'type': 'string',
        'format': 'fqdnurl',
    } == convert(vol.Schema(vol.All(vol.FqdnUrl, str)))
