#!/usr/bin/env python3
#
# RouteViews to RIS dump converter
# Copyright (c) 2019 NLnet Labs
# See LICENSE (TL;DR: 3-clause BSD)
#
# Currently, the conversion reads all announced prefixes from the
# RouteViews dump and takes the last AS in the path for all paths 
# that:
# - Are valid;
# - End in an iBGP or eBGP hop
#
# Routes with incomplete paths (status ?) are ignored

import os
import sys
import bz2

def parse_routeviews_bzip2(name):
    try:
        rv_fd = bz2.open(name, 'r')

        prev_prefix = ""
        pfx_dict = dict()

        for line in rv_fd:
            line = line.decode('utf8')
            if not line.startswith('*'):
                continue

            line = line.strip('\n').strip('\r')

            fields = list(filter(None, line.split(' ')))

            if len(fields) < 8:
                print('Invalid line:')
                print('{}'.format(' '.join(fields)))
                continue

            prefix = fields[1]
            status = fields[-1]
            origin = fields[-2]

            if prefix != prev_prefix:
                # Output what we have
                for orig in pfx_dict.keys():
                    print('{}\t{}\t{}'.format(orig, prev_prefix, pfx_dict[orig]))

                prev_prefix = prefix
                pfx_dict = dict()

            if status == 'i' or status == 'e':
                orig_ct = pfx_dict.get(origin, 0)
                orig_ct += 1
                pfx_dict[origin] = orig_ct

        for orig in pfx_dict.keys():
            print('{}\t{}\t{}'.format(orig, prev_prefix, pfx_dict[orig]))
    except Exception as e:
        print('Failed to process {}:'.format(name))
        print(e)
        sys.exit(1)

def main():
    if len(sys.argv) != 2:
        print('Expected exactly one argument (name of RouteViews dump BZ2), got {} argument(s)'.format(len(sys.argv)))
        sys.exit(1)

    parse_routeviews_bzip2(sys.argv[1])

if __name__ == "__main__":
    main()
