# -*- encoding: utf-8 -*-
import json
import pathlib
import re
import struct
import zlib
from typing import Union

from . import exceptions


def detect_header_by_json_filepath(path: str) -> bytes:
    if not isinstance(path, str):
        raise TypeError('path must be str')
    path = pathlib.Path(path)
    if path.suffix != '.json':
        raise TypeError('file extension must be json')

    original_filename = path.stem
    regex_header_map = {
        r'^savedata.*\.ttsav$': 'TTSAV',
        r'^local_savedata.*\.ttsav$': 'TTSAV',
        r'^heatmap.*\.bjson$': 'HMP',
        r'^heatmeta.*\.ttsav$': 'HMD',
        r'^leaderboard.*\.ttlead$': 'TTLEAD'
    }
    for regex, header in regex_header_map.items():
        if re.match(regex, original_filename):
            return header
    return 'BJSON'  # this is not used by the game, just for default header


def _calculate_checksum(header: str, data: bytes) -> int:
    return ~zlib.crc32(data + header.encode() + b'\x00') & 0xffffffff


def _bitwise_invert_bytes(s: bytes) -> bytes:
    return bytes(map(lambda x: ~x & 0xff, s))


def _decompress(s: bytes) -> bytes:
    result = bytearray()

    src_pos = 0

    result_length = struct.unpack_from('< i', s, offset=0)[0] >> 8

    flag_v15 = (s[src_pos] & 0xf) != 0  # bool
    src_pos += 4

    if result_length == 0:
        result_length = struct.unpack_from('< i', s, src_pos)
        src_pos = 8

    if result_length == 0:
        return b''

    bytes_left = result_length

    v14 = s[src_pos]  # int
    src_pos += 1
    v13 = 0  # int

    while bytes_left > 0:
        if (v14 & 0x80) != 0:
            v5 = s[src_pos]  # unsigned char
            loop_length = v5 >> 4  # int
            if flag_v15:
                if loop_length == 1:
                    v8 = s[src_pos] - (256 if s[src_pos] > 127 else 0)  # converts "unsigned char" to "char"
                    v5 = s[src_pos + 2]
                    loop_length = s[src_pos + 1] << 4
                    src_pos += 2
                    loop_length = (loop_length | ((v8 & 0xf) << 12) | (v5 >> 4)) + 273
                elif loop_length != 0:
                    loop_length += 1
                else:
                    src_pos += 1
                    v8 = v5 - (256 if v5 > 127 else 0)  # converts "unsigned char" to "char"
                    v5 = s[src_pos]
                    loop_length = (((v8 & 0xf) << 4) | (s[src_pos] >> 4)) + 17
            else:
                loop_length += 3
            v11 = (((v5 & 0xf) << 8) | s[src_pos + 1]) + 1  # int
            src_pos += 2
            loop_length = min(loop_length, bytes_left)
            loop_start = len(result) - v11
            # not using slice here because loop_start + loop_length > len(result) may appear
            for i in range(loop_length):
                result.append(result[loop_start + i])
            bytes_left -= loop_length
        else:
            result.append(s[src_pos])
            src_pos += 1
            bytes_left -= 1
        if bytes_left == 0:
            break
        v14 <<= 1
        v13 += 1
        if v13 >= 8:
            v14 = s[src_pos]
            src_pos += 1
            v13 = 0

    assert len(result) == result_length
    return bytes(result)


class TwoTribesBinaryJSON(object):
    __slots__ = ('_header', '_version', '_data', '_raw_data_string')

    def __init__(self, header: str = 'BJSON', version: int = 1, data: dict = None):
        self.header = header
        self.version = version
        self.data = data

    @property
    def header(self):
        return self._header

    @header.setter
    def header(self, value):
        if not isinstance(value, str):
            raise TypeError('header must be str')
        self._header = value

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, value):
        if not isinstance(value, int):
            raise TypeError('version must be int')
        self._version = value

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = value

    @property
    def raw_data_string(self):
        return self._raw_data_string

    @classmethod
    def load_from_bytes(cls, s: Union[bytes, bytearray]):
        if not isinstance(s, (bytes, bytearray)):
            raise TypeError('data must be bytes or bytearray')
        if isinstance(s, bytes):
            s = bytearray(s)

        header_length = s.find(b'\x00')
        if header_length == -1:
            raise exceptions.LoadFileError('invalid file header')

        try:
            header = s[:header_length].decode()
        except Exception as err:
            raise exceptions.LoadFileError('invalid file header')

        try:
            fmt = f'< x i ? i'
            offset = header_length
            (version, is_compressed, data_length) = struct.unpack_from(fmt, s, offset=offset)
            offset += struct.calcsize(fmt)
            fmt = f'< {data_length}s I'
            (data, checksum) = struct.unpack_from(fmt, s, offset=offset)
        except struct.error as err:
            raise exceptions.LoadFileError('invalid file metadata')

        real_checksum = _calculate_checksum(header, data)
        if checksum != real_checksum:
            raise exceptions.LoadFileError(f'checksum incorrect, read {checksum}, actual {real_checksum}')

        data = _bitwise_invert_bytes(data)
        if is_compressed:
            try:
                data = _decompress(data)
            except Exception as err:
                raise exceptions.LoadFileError(f'decompress error: {err}')

        obj = cls(header, version)
        obj._raw_data_string = data

        try:
            data_dict = json.loads(data)
        except Exception as err:
            raise exceptions.LoadFileError(f'json parse error: {err}')

        obj.data = data_dict
        return obj

    def dump_to_bytes(self) -> bytes:
        # TODO: implement dump with compressed

        data = json.dumps(self.data, separators=(',', ':'), sort_keys=True).encode()
        data = _bitwise_invert_bytes(data)
        data_length = len(data)
        checksum = _calculate_checksum(self.header, data)

        result = bytearray()
        result += self.header.encode() + b'\x00'
        result += struct.pack('< i ? i', self.version, False, data_length)
        result += data
        result += struct.pack('< I', checksum)
        return bytes(result)

    def __eq__(self, other):
        if isinstance(other, TwoTribesBinaryJSON):
            return (self._header, self._version, self._data) == (other._header, other._version, other._data)
        return NotImplemented
