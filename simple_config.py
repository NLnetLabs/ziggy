#!/usr/bin/env python3
#
# Copyright (c) 2019 NLnet Labs
# Licensed under a 3-clause BSD license, see LICENSE in the
# distribution
#
# Main module that will execute the checks for all Avro files
# it can find in the directory specified on the command line.
# Will spawn the specified number of threads, which defaults
# to a single thread if no thread count is specified.

import os
import os.path
import sys
import datetime
import json

config = None

def load_config(cfgfile):
    global config

    try:
        config_fd = open(cfgfile, 'r')
        config = json.load(config_fd)
        config_fd.close()
    except Exception as e:
        raise Exception('Failed to load configuration from {} ({})'.format(cfgfile, e))

def get_config_item(item, default_value = None):
    global config

    if item not in config:
        if default_value is None:
            raise Exception("Could not find mandatory item '{}' in the configuration".format(item))

        return default_value

    return config[item]

def get_path_item(item):
    raw_path = get_config_item(item)

    return os.path.expanduser(raw_path)
