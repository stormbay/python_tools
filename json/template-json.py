import sys, os.path
import re
import json




if __name__ == "__main__":

#    print(json.dumps(['foo', {'bar': ('baz', None, 1.0, 2)}], indent=4))

    fd = open("config.json", 'r')
    data = json.load(fd)
    print(data[0]['32-bit'])
    print(data[0]['toolchain_prefix'])
    print(data[0]['toolchain_path'])
    print(data[1]['32-bit'])
    print(data[1]['toolchain_prefix'])
    print(data[1]['toolchain_path'])
    fd.close()

