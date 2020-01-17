# -*- encoding: utf-8 -*-
import pytest

from lib import ttbjson


def test_constructor():
    bjson_obj = ttbjson.TwoTribesBinaryJSON()

    assert bjson_obj.header == 'BJSON'
    assert bjson_obj.version == 1
    assert bjson_obj.data is None

    with pytest.raises(TypeError, match=r'^header must be str$'):
        bjson_obj.header = b'test'
    with pytest.raises(TypeError, match=r'^version must be int$'):
        bjson_obj.version = 'test'
