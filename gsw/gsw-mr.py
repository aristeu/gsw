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
from output import formatted_output

def is_filtered(filter_list, item):
    for f in filter_list:
        if f in item:
            return True
    return False

# list ######

fields = ['id', 'iid', 'project_id', 'title', 'description', 'state', 'created_at', 'updated_at', 'merged_by', 'username', 'name', 'state', 'locked', 'avatar_url', 'web_url', 'merge_user', 'merged_at', 'closed_by', 'closed_at', 'target_branch', 'source_branch', 'user_notes_count', 'upvotes', 'downvotes', 'author', 'assignees', 'assignee', 'reviewers', 'source_project_id', 'target_project_id', 'labels', 'draft', 'work_in_progress', 'milestone', 'merge_when_pipeline_succeeds', 'merge_status', 'detailed_merge_status', 'sha', 'merge_commit_sha', 'squash_commit_sha', 'discussion_locked', 'should_remove_source_branch', 'force_remove_source_branch', 'prepared_at', 'allow_collaboration', 'allow_maintainer_to_push', 'reference', 'references', 'web_url', 'time_stats', 'squash', 'squash_on_merge', 'task_completion_status', 'has_conflicts', 'blocking_discussions_resolved', 'approvals_before_merge' ]

soft_fields = [ 'project' ]

default_fields = [ 'project', 'iid', 'author', 'title', 'blocking_discussions_resolved', 'labels' ]

def op_list(glab, opts, args):
    lines = []

    options = { 'state': "opened" }

    group = None
    for option,value in opts:
        if option == '-a' or option == '--author':
            options['author_username'] = value
            if 'scope' not in options:
                options['scope'] = "all"
        if option == '-g' or option == '--group':
            group = value

    # cache projects if it's in the list
    project_map = {}
    if 'project' in default_fields:
        for p in glab.projects.list():
            project_map[p.id] = p.name

    if group:
        g = glab.groups.get(group)
        results = g.mergerequests.list()
    else:
        results = glab.mergerequests.list(**options)

    for i in results:
        first = True
        line = []
        for f in default_fields:
            if f == 'author':
                line.append("%s" % str(i.attributes[f]['username']))
            elif f == 'labels':
                labels = []
                filtered_out = [ "OK", "Subsystem", "JIRA::InProgress", "readyForQA", "CodeChanged" ]
                for c in i.attributes[f]:
                    if not is_filtered(filtered_out, c):
                        labels.append(c)
                line.append("%s" % ', '.join(labels))
            elif f == 'project':
                project = glab.projects.get(i.project_id)
                line.append("%s" % project.name)
            else:
                line.append("%s" % str(i.attributes[f]))
        lines.append(line)

    formatted_output(lines)

    return 0

def op_list_usage(f):
    f.write("%s list [-a <author> | -g <group>] [-f <fields>] [-h|--help]\n\n")
    f.write("-h|--help\t\tthis message\n")
# list ######

MODULE_NAME = "mr"
MODULE_OPERATIONS = { "list": op_list }
MODULE_OPERATION_USAGE = { "list": op_list_usage }
MODULE_OPERATION_SHORT_OPTIONS = { "list": "f:a:g:" }
MODULE_OPERATION_LONG_OPTIONS = { "list": ["fields=", "author=", "group="] }
MODULE_OPERATION_REQUIRED_ARGS = { "list": 0 }

def list_operations(f):
    for op in MODULE_OPERATIONS:
        f.write("\t%s\n" % op)

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
        sys.stderr.write("%s\n" % err)
        MODULE_OPERATION_USAGE[operation](sys.stderr)
        sys.exit(2)
    for o,v in opts:
        if o == "-h" or o == "--help":
            MODULE_OPERATION_USAGE[operation](sys.stdout)
            sys.exit(0)
    if len(args) < MODULE_OPERATION_REQUIRED_ARGS[operation]:
        sys.stderr.write("Not enough arguments\n")
        MODULE_OPERATION_USAGE[operation](sys.stderr)
        sys.exit(2)

    return MODULE_OPERATIONS[operation](glab, opts, args)

