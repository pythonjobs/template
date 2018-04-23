#!/usr/bin/env python2.7
import sys
import shutil
import os
import subprocess
import tempfile
from fin.contextlog import Log

def main():
    with Log("Identifying paths") as l:
        commit = os.environ.get("TRAVIS_COMMIT", "manual")
        temp_dir = tempfile.mkdtemp()
        l.output("Temp dir: %s" % temp_dir)
        working_dir = os.path.join(temp_dir, 'build')
        checkout_dir = os.path.join(temp_dir, 'checkout')
        template_dir = os.path.abspath(os.path.dirname(__file__))
        hyde_root = os.path.join(template_dir, 'hyde')
        build_dir = os.path.join(hyde_root, 'deploy')
    gh_token = os.environ['GH_TOKEN']

    with Log("Checking out pythonjobs.github.io"):
        os.mkdir(checkout_dir)
        repo_url = 'https://%s@github.com/pythonjobs/pythonjobs.github.io.git' % gh_token
        subprocess.check_call(['git', 'clone', repo_url, checkout_dir], cwd=checkout_dir)

    with Log("Setting up working dir"):
        with Log("Copy in built site"):
            shutil.copytree(build_dir, working_dir)
        with Log("Move in .git"):
            os.rename(os.path.join(checkout_dir, '.git'),
                      os.path.join(working_dir, '.git'))
    with Log("Committing"):
        with Log("Adding any new files"):
            subprocess.check_call(['git', 'add', '-A'], cwd=working_dir)
        with Log("Setting up git variables"):
            subprocess.check_call(['git', 'config', 'user.email', 'stestagg@gmail.com'], cwd=working_dir)
            subprocess.check_call(['git', 'config', 'user.name', 'Travis Job'], cwd=working_dir)
        with Log("Committing"):
            subprocess.check_call(['git', 'commit', '-a',
                                   '-m', 'Site deploy for %s' % commit],
                                   cwd=working_dir)
        with Log("Pushing"):
            subprocess.check_call(['git', 'push', 'origin', 'master'], cwd=working_dir)


if __name__ == "__main__":
    # using sys.argv like this is ugly
    sys.exit(main(*sys.argv[1:]))
