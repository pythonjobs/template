#!/usr/bin/env python2.7
import re
import sys
import shutil
import os
import os.path
import subprocess

import click as click
import yaml
from fin.contextlog import Log

ROOT = os.path.dirname(__file__)



COMMENT_TEMPLATE = """Unfortunately, there is an issue that is preventing us
from validating or publishing your ad:

%s

If you'd like some help correcting this, or think the error is not valid, please reply to this comment.
"""


def report_error(msg):
    with Log("Error Found"):
        with Log("Commenting on PR"):
            proc = subprocess.Popen([
                sys.executable,
                os.path.join(ROOT, "comment.py")
            ], stdin=subprocess.PIPE)
            proc.communicate(COMMENT_TEMPLATE % msg)
        raise AssertionError(msg)


def validate(fullpath):
    """Validate the formatting of the given jobs file.

    The contents of the file will be validated later; this is just checking
    that the file will parse.

    """
    data = open(fullpath, 'r').read()
    path = os.path.basename(fullpath)

    try:
        data = data.decode('utf8')
    except UnicodeDecodeError:
        report_error("file %s contains some invalid characters.  All text must be valid utf-8" % path)

    chunks = re.split(r'^---[ \t]*$', data, flags=re.M)
    if len(chunks) < 3:
        report_error("%s: should be YAML and Markdown, prefixed by --- lines. Please check the example" % path)
    if len(chunks[0].strip()) != 0:
        report_error("%s: data before initial ---" % path)

    try:
        yaml.safe_load(chunks[1])
    except Exception as e:
        report_error("%s: This file doesn't seem to have a valid yaml header:\n ```%s\n```" % (path, e))


def main(jobs_dir):
    with Log("Identifying paths"):
        jobs_root = os.path.abspath(jobs_dir)
        template_dir = os.path.abspath(os.path.dirname(__file__))
        hyde_root = os.path.join(template_dir, 'hyde')
        jobs_source = os.path.join(jobs_root, 'jobs')
        jobs_dest = os.path.join(hyde_root, 'content', 'jobs')

    with Log("Checking for unexpected files"):
        unexpected_files = set()
        with Log(jobs_root) as l:
            for filename in os.listdir(jobs_root):
                if filename.endswith('.html') or filename.endswith('.md'):
                    if filename not in {"README.md", "jobtemplate.html"}:
                        unexpected_files.add((filename, jobs_root))

        with Log(jobs_source) as l:
            for filename in os.listdir(jobs_source):
                if not filename.endswith(".html"):
                    unexpected_files.add((filename, jobs_source))
        if unexpected_files:
            file_descs = ["%s (%s)" % i for i in unexpected_files]
            report_error("""
All job files must be added under the jobs/ directory, and must end in '.html'.
I found the following files that do not match this:

 * %s
            """ % ("\n * ".join(file_descs)))

    with Log("Copy in jobs") as l:
        for job_file in os.listdir(jobs_source):
            with Log('Copying %s' % job_file):
                src_path = '%s/%s' % (jobs_source, job_file) # This is safer than join()
                dest_path = '%s/%s' % (jobs_dest, job_file)
                validate(src_path)
                shutil.copyfile(src_path, dest_path)

    with Log("Building & Validating Site"):
        subprocess.check_call(['hyde', '-x', '-s', hyde_root, 'gen', '-r'])

@click.command()
@click.argument("jobs_dir")
def command(jobs_dir):
    sys.exit(main(jobs_dir))

if __name__ == "__main__":
    command()
