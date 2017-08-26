#!/usr/bin/env python
from __future__ import print_function
import argparse
import json
from subprocess import Popen, PIPE
from datetime import datetime

log_file_name = 'rundeck-cleanup.log'
log_file_mode = 'a+'
parser = argparse.ArgumentParser(description='input number of days')
parser.add_argument('--remove_older_than', required=True)
args = parser.parse_args()
f = open(log_file_name, log_file_mode)
guard = 100


def get_projects():
    p = Popen(['rd projects list'], shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    output, error = p.communicate()
    if p.returncode == 0:
        output = output.split("\n", 1)[1].strip().split('\n')
        return list(output)
    else:
        f.write(str(datetime.now()) + ' Execution deletion failed: ' + error)


def delete_executions(project_names_list):
    no_errors = True
    for project_name in project_names_list:
        for i in xrange(guard):
            cmd = ('rd executions deletebulk --older {} --project {} -y'.format(args.remove_older_than, project_name))
            p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
            p.wait()
            output, error = p.communicate()
            if p.returncode != 0:
                f.write(str(datetime.now()) + ' Execution deletion failed for {} - '.format(project_name) + error + '\n')
                no_errors = False
                break
            if output == 'No executions found to delete':
                break
    return no_errors


try:
    projects = get_projects()
    if type(projects) is list:
        x = delete_executions(projects)
        if x:
            print(json.dumps({'status': 'success'}))
        else:
            print(json.dumps({'status': 'one or more projects failed to have their executions deleted, check logs'}))
    else:
        print(json.dumps({'status': 'error', 'message': 'Could not retrieve project list'}))
        f.write(str(datetime.now()) + ' Could not retrieve project list' + '\n')
except Exception as ex:
    print(json.dumps({'status': 'error', 'message': 'execution deletion failed, Exception Error, check logs'}))
    f.write(str(datetime.now()) + ' Execution deletion failed: ' + str(ex) + '\n')
finally:
    f.close()
