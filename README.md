# Edge PC Savefile Editor

A tool that allows encrypting and decrypting binary JSON savefiles from PC version of the awesome game [EDGE](http://2trib.es/edge).  

## Installation

You need to install at least [Python 3.6](https://www.python.org/downloads/) to run this program.  
Or just download the [release](https://github.com/WEGFan/Edge-PC-Savefile-Editor/releases) for Windows so you don't need to install Python.  

## Usage

### Running with Python

```console
$ python savefile_editor.py
usage: savefile_editor.py [-h] [-r] [-v] [files [files ...]]

Encrypt and decrypt binary JSON savefiles from EDGE PC version.

positional arguments:
  files          the files to be encrypted or decrypted, output files are in
                 the same folder with input files

optional arguments:
  -h, --help     show this help message and exit
  -r, --raw      don't parse and prettify decrypted JSONs
  -v, --version  show program's version number and exit
```

### Running with Windows executable

The command line arguments are the same as above.  
You can also directly drag files onto the executable to quickly encrypt / decrypt them.

## Not working?

Feel free to [submit an issue](https://github.com/WEGFan/Edge-PC-Savefile-Editor/issues/new) if you encounter any problems.  
