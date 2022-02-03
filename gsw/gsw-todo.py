# -*- coding: utf-8 -*-
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.  See http://www.gnu.org/copyleft/gpl.html for
# the full text of the license.

import getopt
import sys
import gitlab

"""
Parameters:
Attribute   Type        Required    Description
action      string      no          The action to be filtered. Can be assigned, mentioned, build_failed, marked, approval_required, unmergeable, directly_addressed or merge_train_removed.
author_id   integer     no          The ID of an author
project_id  integer     no          The ID of a project
group_id    integer     no          The ID of a group
state       string      no          The state of the to do. Can be either pending or done
type        string      no          The type of to-do item. Can be either Issue, MergeRequest, DesignManagement::Design or AlertManagement::Alert

"""
all_fields = ["id", "project_id", "project", "target_iid", "target_type", "target_state", "body", "target_title", "labels", "target_url"]
direct_fields = [ "id", "target_type", "target_url", "body", "labels" ]
def get_field(todo, field):
    # only MergeRequest supported for now
    if todo.target_type is not "MergeRequest":
        return None

    if field in direct_fields:
        return todo.__getattr__(field)
    elif field == "project_id":
        return todo.project['id']
    elif field == "project":
        return todo.project['name']
    elif field == "target_iid":
        return todo.target['iid']
    elif field == "target_title":
        return todo.target['title']
    elif field == "target_state":
        return todo.target['state']
    return None

# list ######
def op_list(glab, opts, args):
    fields = [ "id", "target_state", "project", "target_type", "target_iid", "target_title" ]

    for option,value in opts:
        if option == '--fields' or option == '-f':
            fields = []
            for o in value.split(','):
                if o not in all_fields:
                    sys.stderr.write("Unknown field: %s\n" % o)
                    op_list_usage(sys.stderr)
                    return 2
                fields.append(o)
        else:
            sys.stderr.write("Unknown option: %s\n" % option)
            usage(sys.stderr)
            sys.exit(2)

    max_size = {}
    todos = glab.todos.list()

    if sys.stdout.isatty():
        for todo in todos:
            for field in fields:
                field_value = get_field(todo, field)
                if field not in max_size:
                    max_size[field] = len(str(field_value))
                else:
                    if len(str(field_value)) > max_size[field]:
                        max_size[field] = len(str(field_value))

        for todo in todos:
            output = []
            output_format = ""
            for field in fields:
                output.append(str(get_field(todo, field)))
                output_format += "{: <%i}\t" % max_size[field]
            print(output_format.format(*output))

        return 0

    for todo in todos:
        output = []
        for field in fields:
            output.append(str(get_field(todo, field)))
        print('\t'.join(output))

    return 0

def op_list_usage(f):
    f.write("%s list [-f <fields>] [-h|--help]\n\n")
    f.write("-f <fields>\t\tspecify which fields to show\n")
    f.write("-h|--help\t\tthis message\n\n")
    f.write("Available fields: %s\n" % ', '.join(all_fields))
# list ######

MODULE_NAME = "todo"
MODULE_OPERATIONS = { "list": op_list }
MODULE_OPERATION_USAGE = { "list": op_list_usage }
MODULE_OPERATION_SHORT_OPTIONS = { "list": "f:" }
MODULE_OPERATION_LONG_OPTIONS = { "list": ["fields="] }

def list_operations(f):
    for op in MODULE_OPERATIONS:
        f.write("\t%s\n" % op)

def usage(f):
    f.write("fixme\n")

def gsw_module_main(config, glab, argv):
    if len(argv) < 2:
        print("%s <operation>" % MODULE_NAME)
        print("Available operations:")
        list_operations(sys.stdout)
        sys.exit(0)
    if argv[1] not in MODULE_OPERATIONS:
        sys.stderr.write("Invalid operation: %s\n" % argv[1])
        sys.stderr.write("Available operations:\n")
        list_operations(sys.stderr)
        sys.exit(2)

    operation = argv[1]
    short_options = MODULE_OPERATION_SHORT_OPTIONS[operation]
    long_options = MODULE_OPERATION_LONG_OPTIONS[operation]
    short_options += "h"
    long_options.append("help")

    try:
        opts, args = getopt.getopt(argv[2:], short_options, long_options)
    except getopt.GetoptError as err:
        print(err)
        MODULE_OPERATION_USAGE[operation](sys.stderr)
        sys.exit(2)
    for o,v in opts:
        if o == "-h" or o == "--help":
            MODULE_OPERATION_USAGE[operation](sys.stdout)
            sys.exit(0)
    return MODULE_OPERATIONS[operation](glab, opts, args)

