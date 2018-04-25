#!/usr/bin/env python2.7
import os
import time
import sys
import subprocess
import requests

from selenium import webdriver

TEMPLATE_DIR = os.path.abspath(os.path.dirname(__file__))


def upload_screenshot(data):
    url = "https://i2xwshcjfa.execute-api.eu-west-1.amazonaws.com/live/pythonjobs-commentbot/screenshots"
    req = requests.post(url, data, headers={"Content-Type": "image/png"})
    req.raise_for_status()
    return req.json()['body']


def get_preview(driver, filename, pull_request_num):
    basename, ext = os.path.splitext(filename)
    url = "http://localhost:8080/jobs/%s.html" % basename
    driver.get(url)
    while driver.execute_script("return document.readyState") != "complete":
        time.sleep(0.5)
    png = driver.get_screenshot_as_png()
    return upload_screenshot(png)


def get_file_previews(pull_request_num):
    preview_ids = []
    driver = webdriver.PhantomJS()
    hyde_root = os.path.join(TEMPLATE_DIR, 'hyde')
    server_proc = subprocess.Popen(['hyde', '-s', hyde_root, 'serve'])
    time.sleep(4)
    try:
        driver.set_window_size(800, 600)
        for filename in get_modified_files():
            image_id = get_preview(driver, filename, pull_request_num)
            preview_ids.append(image_id)
    finally:
        driver.close()
        server_proc.terminate()
        server_proc.wait()

    if not preview_ids:
        return

    link_template = '![Job listing preview](https://s3-eu-west-1.amazonaws.com/pythonjobs-screenshots/%s.png)'
    image_links = [link_template % preview_id for preview_id in preview_ids]

    message = """Here are some screenshots of what the live listing should look like:

%s
    """ % ("\n".join(image_links), )

    proc = subprocess.Popen([
        sys.executable,
        os.path.join(TEMPLATE_DIR, "comment.py")
    ], stdin=subprocess.PIPE)
    proc.communicate(message)


def get_modified_files():
    modified_files = subprocess.check_output(['git', 'diff', '--name-only', 'master'])
    for line in modified_files.split():
        if line.startswith("jobs/"):
            yield line[5:]


if __name__ == '__main__':
    pull_request_num = os.environ.get('TRAVIS_PULL_REQUEST', 'false')
    if pull_request_num  == 'false':
        sys.exit("Not creating pull-request screenshot, as can't get PR number")
    get_file_previews(pull_request_num)