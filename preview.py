#!/usr/bin/env python2.7
import os
import time
import sys
import subprocess

from selenium import webdriver

TEMPLATE_DIR = os.path.abspath(os.path.dirname(__file__))
SCREENSHOT_REPO = os.path.join(os.path.dirname(TEMPLATE_DIR), "screenshots")
SCREENSHOT_FILE =  os.path.join(SCREENSHOT_REPO, "screenshot.png")

def check_out():
    if 'GH_TOKEN' not in os.environ:
        sys.exit("No GH_TOKEN found")
    gh_token = os.environ['GH_TOKEN']
    os.mkdir(SCREENSHOT_REPO)
    repo_url = 'https://%s@github.com/pythonjobs/screenshots.git' % gh_token
    subprocess.check_call(['git', 'clone', '--depth=1', repo_url, SCREENSHOT_REPO], cwd=SCREENSHOT_REPO)


def commit_changes(pr_num):
    subprocess.check_call(['git', 'add', SCREENSHOT_FILE], cwd=SCREENSHOT_REPO)
    subprocess.check_call(['git', 'commit', '--allow-empty', '-m', 'Screenshot for #%s' % pr_num], cwd=SCREENSHOT_REPO)
    return subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=SCREENSHOT_REPO).strip()


def get_preview(driver, filename, pull_request_num):
    basename, ext = os.path.splitext(filename)
    url = "http://localhost:8080/jobs/%s.html" % basename
    driver.get(url)
    while driver.execute_script("return document.readyState") != "complete":
        time.sleep(0.5)
    png = driver.get_screenshot_as_png()
    with open(SCREENSHOT_FILE, "wb") as fh:
        fh.write(png)
    return commit_changes(pull_request_num)


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
    subprocess.check_call(['git', 'push', 'origin', 'master'], cwd=SCREENSHOT_REPO)

    link_template = '![Job listing preview](https://raw.githubusercontent.com/pythonjobs/screenshots/%s/screenshot.png)'
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
    check_out()
    pull_request_num = os.environ.get('TRAVIS_PULL_REQUEST', 'false')
    if pull_request_num  == 'false':
        sys.exit("Not creating pull-request screenshot, as can't get PR number")
    get_file_previews(pull_request_num)