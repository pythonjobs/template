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
        if "TRAVIS_PULL_REQUEST" not in os.environ or os.environ["TRAVIS_PULL_REQUEST"] == 'false':
            Log.output("No TRAVIS_PULL_REQUEST found, not commenting")
            return
        pr_num = os.environ["TRAVIS_PULL_REQUEST"]
        url = "https://i2xwshcjfa.execute-api.eu-west-1.amazonaws.com/live/pythonjobs-commentbot/prcomment"
        with Log("Submitting request"):
            req = requests.post(
                url, json={"pr": int(pr_num), "msg": comment},
            )
            print(req.text)
            req.raise_for_status()


if __name__ == '__main__':
    add_comment(sys.stdin.read().strip())