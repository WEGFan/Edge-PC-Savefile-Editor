# -*- encoding: utf-8 -*-
import glob

import pytest

from lib import ttbjson


def test_invalid_checksum():
    file_list = glob.glob('tests/files/invalid/checksum_*')
    for file in file_list:
        with open(file, 'rb') as f:
            with pytest.raises(ttbjson.LoadFileError, match=r'^checksum incorrect, read \d+, actual \d+$'):
                bjson_obj = ttbjson.TwoTribesBinaryJSON.load_from_bytes(f.read())
        print(f'{file} DONE')


def test_invalid_decompress():
    file_list = glob.glob('tests/files/invalid/decompress_*')
    for file in file_list:
        with open(file, 'rb') as f:
            with pytest.raises(ttbjson.LoadFileError, match=r'^decompress error: .*$'):
                bjson_obj = ttbjson.TwoTribesBinaryJSON.load_from_bytes(f.read())
        print(f'{file} DONE')


def test_invalid_json():
    file_list = glob.glob('tests/files/invalid/json_*')
    for file in file_list:
        with open(file, 'rb') as f:
            with pytest.raises(ttbjson.LoadFileError, match=r'^json parse error: .*$'):
                bjson_obj = ttbjson.TwoTribesBinaryJSON.load_from_bytes(f.read())
        print(f'{file} DONE')


def test_invalid_header():
    file_list = glob.glob('tests/files/invalid/header_*')
    for file in file_list:
        with open(file, 'rb') as f:
            with pytest.raises(ttbjson.LoadFileError, match=r'^invalid file header$'):
                bjson_obj = ttbjson.TwoTribesBinaryJSON.load_from_bytes(f.read())
        print(f'{file} DONE')


def test_invalid_metadata():
    file_list = glob.glob('tests/files/invalid/metadata_*')
    for file in file_list:
        with open(file, 'rb') as f:
            with pytest.raises(ttbjson.LoadFileError, match=r'^invalid file metadata$'):
                bjson_obj = ttbjson.TwoTribesBinaryJSON.load_from_bytes(f.read())
        print(f'{file} DONE')
