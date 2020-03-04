# -*- coding: utf-8 -*-
import argparse
import json
import pathlib
import sys

from lib import ttbjson

__version__ = '1.0.0'


def main():
    parser = argparse.ArgumentParser(description='Encrypt and decrypt binary JSON savefiles from EDGE PC version.')
    parser.add_argument('files', nargs='*', help='the files to be encrypted or decrypted, output files are in the same folder with input files')
    parser.add_argument('-r', '--raw', action='store_true', help="don't parse and prettify decrypted JSONs")
    parser.add_argument('-v', '--version', action='version', version=f'Edge PC Savefile Editor v{__version__}')

    # for unit testing with distribution package
    # should exclude unit test module before release packaging
    try:
        import pytest
        parser.add_argument('-t', '--test', action='store_true', help='run unit tests')
    except ImportError as err:
        pass

    args = parser.parse_args()

    if args.__dict__.get('test'):
        # i don't know why running coverage report with distribution package will fail...
        pytest.main(['tests/', '-l', '-v', '-s'])
        return

    if not args.files:
        parser.print_help()
        return

    success_files = 0

    for file in args.files:
        path = pathlib.Path(file)
        try:
            if path.suffix == '.json':
                # encrypt
                with open(file, 'r', encoding='utf-8') as f:
                    bjson_obj = ttbjson.TwoTribesBinaryJSON(ttbjson.detect_header_by_json_filepath(file),
                                                            1,
                                                            json.loads(f.read()))
                with open(file.rstrip('.json'), 'wb') as f:
                    f.write(bjson_obj.dump_to_bytes())
            else:
                # decrypt
                with open(file, 'rb') as f:
                    bjson_obj = ttbjson.TwoTribesBinaryJSON.load_from_bytes(f.read())
                if args.raw:
                    with open(file + '.json', 'wb') as f:
                        f.write(bjson_obj.raw_data_string)
                else:
                    with open(file + '.json', 'w', encoding='utf-8') as f:
                        f.write(json.dumps(bjson_obj.data, indent=4, sort_keys=True))
            print(f'{file} - DONE')
            success_files += 1
        except OSError as err:
            print(f'{file} - FAILED: could not read/write file: {err}')
        except ttbjson.Error as err:
            print(f'{file} - FAILED: parse file error: {err}')
        except Exception as err:
            print(f'{file} - FAILED: [{type(err).__name__}] {err}')

    print()
    print(f'{success_files} of {len(args.files)} files DONE')
    if success_files != len(args.files):
        print('Some files failed to encrypt/decrypt. See above log for more details.')
        print('Press ENTER to exit the program.')
        input()


if __name__ == '__main__':
    try:
        main()
    except (EOFError, KeyboardInterrupt) as err:
        sys.exit()
