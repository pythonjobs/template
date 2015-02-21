#!/usr/bin/env python2.7
import sys
import shutil
import os
import subprocess
from fin.contextlog import Log


def main(jobs_dir):
    with Log("Identifying paths"):
        jobs_root = os.path.abspath(jobs_dir)
        template_dir = os.path.abspath(os.path.dirname(__file__))
        hyde_root = os.path.join(template_dir, 'hyde')
        jobs_source = os.path.join(jobs_root, 'jobs')
        jobs_dest = os.path.join(hyde_root, 'content', 'jobs')
        deploy_dir = os.path.join(hyde_root, 'deploy')
        jobs_meta_path = os.path.join(jobs_dest, 'meta.yaml')

    with Log("Copy in jobs") as l:
        for file in os.listdir(jobs_source):
            if not file.endswith(".html"):
                l.output("Skipping: %s" % file)
                continue
            with Log('Copying %s' % file):
                src_path = '%s/%s' % (jobs_source, file) # This is safer than join()
                dest_path = '%s/%s' % (jobs_dest, file)
                shutil.copyfile(src_path, dest_path)
    with Log("Building Site"):
        subprocess.check_call(['hyde', '-s', hyde_root, 'gen', '-r'])


if __name__ == "__main__":
    # using sys.argv like this is ugly
    sys.exit(main(*sys.argv[1:]))
