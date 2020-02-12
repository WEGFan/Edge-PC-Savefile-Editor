# -*- encoding: utf-8 -*-
import glob
import pathlib

import pytest

from lib import ttbjson

file_list = glob.glob('tests/files/valid/**/*', recursive=True)


def test_detect_header():
    for file in file_list:
        if not pathlib.Path(file).is_file():
            continue
        with open(file, 'rb') as f:
            data = f.read()
        real_header = data[:data.find(b'\x00')].decode()
        guess_header = ttbjson.detect_header_by_json_filepath(file + '.json')
        assert real_header == guess_header
        print(f'{file} DONE')

    assert ttbjson.detect_header_by_json_filepath('1111.json') == 'BJSON'

    with pytest.raises(TypeError, match=r'^path must be str$'):
        ttbjson.detect_header_by_json_filepath(b'test.json')
    with pytest.raises(TypeError, match=r'^file extension must be json$'):
        ttbjson.detect_header_by_json_filepath('test')
