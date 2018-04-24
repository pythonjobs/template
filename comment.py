#!/usr/bin/env python2.7
import os
import sys
import requests

from fin.contextlog import Log


COMMENT_TEMPLATE = """Hi

Thanks for submitting this job advert.

%s

Thanks

Pythonjobs
"""

def add_comment(comment):
    with Log("PR comment"):
        if "GH_TOKEN" not in os.environ:
            Log.output("No GH_TOKEN found")
            return
        if "TRAVIS_PULL_REQUEST" not in os.environ:
            Log.output("No TRAVIS_PULL_REQUEST found")
            return
        token = os.environ['GH_TOKEN']
        pr_num = os.environ["TRAVIS_PULL_REQUEST"]
        url = "https://api.github.com/repos/pythonjobs/jobs/issues/%s/comments" % pr_num
        with Log("Submitting request"):
            req = requests.post(
                url, json={"body": COMMENT_TEMPLATE % comment},
                headers={"Authorization": "token %s" % token}
            )
            print(req.text)
            req.raise_for_status()


if __name__ == '__main__':
    add_comment(sys.stdin.read().strip())