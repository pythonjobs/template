#!/usr/bin/env python2.7
import sys
import shutil
import os
import subprocess
from fin.contextlog import CLog


def main(jobs_dir):
    with CLog("Identifying paths"):
        jobs_root = os.path.abspath(jobs_dir)
        template_dir = os.path.abspath(os.path.dirname(__file__))
        hyde_root = os.path.join(template_dir, 'hyde')
        jobs_source = os.path.join(jobs_root, 'jobs')
        jobs_dest = os.path.join(hyde_root, 'content', 'jobs')
        deploy_dir = os.path.join(hyde_root, 'deploy')
        jobs_meta_path = os.path.join(jobs_dest, 'meta.yaml')

    with CLog("Copy in jobs"):
        with CLog("Reading jobs yaml"):
            with open(jobs_meta_path, 'rb') as fh:
                yaml_file = fh.read()
        with CLog("Removing old dir"):
            shutil.rmtree(jobs_dest)
        with CLog("Copying in jobs files"):
            shutil.copytree(jobs_source, jobs_dest)
        with CLog("Replacing meta.yaml"):
            with open(jobs_meta_path, 'wb') as fh:
                fh.write(yaml_file)
    with CLog("Building Site"):
        subprocess.check_call(['hyde', '-s', hyde_root, 'gen'])


if __name__ == "__main__":
    # using sys.argv like this is ugly
    sys.exit(main(*sys.argv[1:]))
