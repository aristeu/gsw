#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.  See http://www.gnu.org/copyleft/gpl.html for
# the full text of the license.

import os
import sys
import glob
import getopt
import importlib
import configparser
import gitlab

def print_objects(arg, f):
    f.write("List of objects:\n")
    dirname = os.path.dirname(arg)
    basename = os.path.basename(arg.replace('-run','').replace(".py",""))
    results = glob.glob("%s/%s-*" % (dirname, basename))

    for match in results:
        name = os.path.basename(match).replace('.py', '')
        name = name.split('-')[1:]
        name = '-'.join(name)
        if name == 'run':
            continue
        f.write("\t%s\n" % name)

def usage(f):
    f.write("%s [--config=<file>|-c <file>][--help|-h] <object>...\n\n" % sys.argv[0])
    f.write("\t--config|-c <file>\t\tUse <file> as configuration file instead of default (~/.gsw)\n")
    f.write("\n")
    f.write("--help|-h\t\tthis message\n")

short_options = "c:h"
long_options = ["config=", "help"]

def main(cmd, argv):
    config_file = "~/.config/gsw/config"

    try:
        opts, args = getopt.getopt(sys.argv[1:], short_options, long_options)
    except getopt.GetoptError as err:
        print(err)
        usage(sys.stderr)
        sys.exit(2)

    for option,value in opts:
        if option == '--config' or option == '-c':
            config_file = value
        elif option == '--help' or option == '-h':
            usage(sys.stdout)
            sys.exit(0)
        else:
            sys.stderr.write("Unknown option: %s\n" % option)
            usage(sys.stderr)
            sys.exit(2)

    basename = os.path.basename(cmd.replace('-run.py',''))
    config = configparser.ConfigParser()
    config.read(os.path.expanduser(config_file))

    if 'gitlab' not in config:
        sys.stderr.write("'gitlab' section not found in the config file. Please create it\n")
        sys.exit(2)
    if 'url' not in config['gitlab'] or 'token' not in config['gitlab']:
        sys.stderr.write("'gitlab' section in the config file isn't complete: 'url' and 'token' are mandatory\n")
        sys.exit(2)
    url = config['gitlab']['url']
    token = config['gitlab']['token']

    try:
        glab = gitlab.Gitlab(url, private_token=token, per_page=500)
    except Exception as err:
        raise Exception("Unable to connect to gitlab (%s)" % str(err))

    if len(args) < 1:
        print_objects(cmd, sys.stdout)
        return 0

    mod = importlib.import_module('%s.%s-%s' % (basename, basename, args[0]))
    return mod.gsw_module_main(config, glab, args)

if __name__ == '__main__':
    sys.exit(main(sys.argv[0], sys.argv[1:]))
