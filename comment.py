#!/usr/bin/env python2.7
import os
import sys
import requests

COMMENT_TEMPLATE = """Hi

Thanks for submitting this job advert.

%s

Thanks

Pythonjobs
"""

def add_comment(comment):
    if "GH_TOKEN" in os.environ and "TRAVIS_PULL_REQUEST" in os.environ:
        token = os.environ['GH_TOKEN']
        pr_num = os.environ["TRAVIS_PULL_REQUEST"]
        url = "https://api.github.com/repos/pythonjobs/jobs/issues/%s/comments" % pr_num
        req = requests.post(
            url, json={"body": COMMENT_TEMPLATE % comment},
            headers={"Authorization": "token %s" % token}
        )
        print(req.text)
        req.raise_for_status()


if __name__ == '__main__':
    add_comment(sys.stdin.read().strip())