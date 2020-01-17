# -*- encoding: utf-8 -*-
import glob

import pytest

from lib import ttbjson

file_list = glob.glob('tests/files/valid/**/*')


def test_load_dump_files():
    for file in file_list:
        with open(file, 'rb') as f:
            bjson_obj = ttbjson.TwoTribesBinaryJSON.load_from_bytes(f.read())
            dump = bjson_obj.dump_to_bytes()
        print(f'{file} DONE')


def test_load_dump():
    bjson_obj = ttbjson.TwoTribesBinaryJSON('ABCDEF', 0x11223344, {
        'test': [1, 2, 3, 4],
        '1': {
            '2': '3',
            '4': [],
            '5': 1111
        }
    })
    real_result = (
        # heaeder
        b'ABCDEF\x00'
        # version
        b'\x44\x33\x22\x11'
        # compress
        b'\x00'
        # data length
        b'\x30\x00\x00\x00'
        # data
        b'\x84\xdd\xce\xdd\xc5\x84\xdd\xcd\xdd\xc5\xdd\xcc\xdd\xd3\xdd\xcb\xdd\xc5\xa4\xa2\xd3\xdd\xca\xdd\xc5\xce\xce\xce\xce\x82\xd3\xdd\x8b\x9a\x8c\x8b\xdd\xc5\xa4\xce\xd3\xcd\xd3\xcc\xd3\xcb\xa2\x82'
        # checksum
        b'\xdc\xc9\xd1\x9b'
    )
    result = bjson_obj.dump_to_bytes()
    assert result == real_result
    assert bjson_obj == ttbjson.TwoTribesBinaryJSON.load_from_bytes(bytearray(result))

    with pytest.raises(TypeError, match=r'^data must be bytes or bytearray$'):
        _ = ttbjson.TwoTribesBinaryJSON.load_from_bytes('11111')
