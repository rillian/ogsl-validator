#!/usr/bin/env python3

'''Parse oracc global sign list in `asl` format.

The format consists of a set of records. Each begins with an `@sign`
line with the nominal sign name, and ends with `@end sign`.
In between is an `@ucode` line with the unicode codepoint,
and `@v` lines giving different readings.'''

import logging
import re

from logging import debug, info, warning, error

class OgslSign:
    def __init__(self, name=''):
        self.name = name
        self.lists = []
        self.sign = ''
        self.values = []
        self.fake = False


    def __str__(self):
        s = f'{self.name} {self.sign}'
        if self.lists:
            s += f' ({" ".join(self.lists)})'
        if self.values:
            s += f'  {" ".join(self.values)}'
        return s


def rest_of(line):
    '''Trip the first token off a line of text, returning the rest.'''
    _, rest = line.split(maxsplit=1)
    return rest


ucode_pattern = re.compile(r'x?([0-9a-fA-F]+)')


def ucode_to_char(code):
    '''Convert a ucode value from a hex representation to a string.'''
    debug(f'Checking {code} against {ucode_pattern}')
    match = re.match(ucode_pattern, code)
    debug(f'  {match}')
    if match:
        return chr(int(match[1], 16))
    else:
        return code


def parse_asl(fp):
    sign = None
    for line in fp.readlines():
        line = line.strip()
        if not line:
            continue
        debug(line)
        if line.startswith('@sign'):
            name = rest_of(line)
            sign = OgslSign(name)
        elif line.startswith('@end sign'):
            yield sign
        elif line.startswith('@end'):
            error(f'unrecognized @end: {line}')
        elif line.startswith('@ucode'):
            codes = rest_of(line).split('.')
            sign.sign = ''.join(map(ucode_to_char, codes))
        elif line.startswith('@v'):
            items = line.split(maxsplit=2)
            sign.values.append(items[1])
        elif line.startswith('@list'):
            citation = rest_of(line)
            sign.lists.append(citation.strip())
        elif line.startswith('@fake'):
            sign.fake = bool(rest_of(line))
        elif line.startswith('@uname'):
            continue
        elif line.startswith('@uphase'):
            continue
        elif line.startswith('@note'):
            continue
        elif line.startswith('@inote'):
            continue
        elif line.startswith('@form'):
            continue
        elif line.startswith('@lit'):
            continue
        elif line.startswith('@pname'):
            continue
        else:
            warning(f'unrecognized line: {line}')
                

if __name__ == '__main__':
    import argparse

    ap = argparse.ArgumentParser(description='Parse and validate a sign list database in asl format.')
    ap.add_argument('filename', help='asl sign list to verify')
    ap.add_argument('-v', '--verbose',
            help='more information about progress and status',
            action='store_true')
    ap.add_argument('--log', nargs='?', default='info',
            help='set level of logging output')
    args = ap.parse_args()

    log_level = logging.WARNING
    if args.verbose:
        log_level = logging.INFO
    if args.log:
        log_level = args.log.upper()
    logging.basicConfig(level=log_level)

    signs = []
    with open(args.filename) as f:
        for sign in parse_asl(f):
            signs.append(sign)
            if args.verbose:
                print(sign)

    print(f'Parsed {len(signs)} signs.')

    out_of_unicode = len([False for sign in signs if not sign.sign])
    if out_of_unicode:
        print(f'  {out_of_unicode} where out of Unicode.')

    no_values = len([False for sign in signs if not len(sign.values)])
    if no_values:
        print(f'  {no_values} have no phonetic values.')
