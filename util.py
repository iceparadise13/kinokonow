import json


def iterate_lines(f):
    while 1:
        line = f.readline()
        if not line:
            break
        yield line


def iterate_json(f):
    for it in iterate_lines(f):
        yield json.loads(it)
