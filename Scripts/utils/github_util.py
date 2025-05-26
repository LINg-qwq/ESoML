import re
import requests
from bs4 import BeautifulSoup
from assets import web_config

from assets.web_config import headers, payload
from utils.web_util import get_page_content
from assets.regex_format import pull_format


PREFIX = "https://api.github.com"


def get_info_from_github_url(url):
    value_list = url.split("/")
    owner = value_list[3]
    repo = value_list[4]
    pull_number = value_list[6]
    return owner, repo, pull_number


def github_url_transfer(url):
    return str(url).replace("github.com", "api.github.com/repos")


def get_pr_fixed_issue(issue_url):
    api_url = github_url_transfer(issue_url)
    headers_for_issue = headers
    headers_for_issue['Accept'] = 'application/vnd.github.VERSION.raw+json'
    response = requests.request("GET", api_url, headers=headers_for_issue, data=payload)
    content = response.json()
    if 'html_url' in content.keys():
        html_url = content['html_url']
        html_content = get_page_content(html_url)
        if html_content != -1:
            soup = BeautifulSoup(html_content, 'html.parser')
            result_set = []
            for pr in soup.find_all(href=re.compile(pull_format)):
                # print(pr.get('href'))
                result_set.append(pr.get('href'))
            return list(set(result_set))
        print("Connection fail to "+str(issue_url))
    else:
        print("Issue not fixed by a PR in "+str(issue_url))


def get_pr(owner, repo, pull_number):
    url = f"{PREFIX}/repos/{owner}/{repo}/pulls/{pull_number}"
    response = requests.request("GET", url, headers=headers, data=payload)
    return response.json()


def get_pr_commits(owner, repo, pull_number):
    pr = get_pr(owner, repo, pull_number)
    commits_url = pr["_links"]["commits"]["href"]
    response = requests.request("GET", commits_url, headers=headers, data=payload)
    return response.json()


def get_commit_files(commit_api_url):
    response = requests.request("GET", commit_api_url, headers=headers, data=payload)
    response_json = response.json()
    return response_json["files"]


def get_files_changed_in_pr(owner, repo, pull_number):
    url = f"{PREFIX}/repos/{owner}/{repo}/pulls/{pull_number}/files"
    response_json = requests.request(
        "GET", url, headers=headers, data=payload
    ).json()
    return response_json


def get_file_changes(owner, repo, file_path):
    url = f"{PREFIX}/repos/{owner}/{repo}/commits?path={file_path}"
    response_json = requests.request(
        "GET", url, headers=headers, data=payload
    ).json()
    return response_json


def get_file_changes_with_branch(owner, repo, file_path, branch_sha):
    url = f"{PREFIX}/repos/{owner}/{repo}/commits?sha={branch_sha}&path={file_path}"
    response_json = requests.request(
        "GET", url, headers=headers, data=payload
    ).json()
    return response_json


def get_repo_content(owner, repo, path):
    url = f"{PREFIX}/repos/{owner}/{repo}/contents/{path}"
    # print(url)
    response = requests.request("GET", url, headers=headers, data=payload)
    return response.json()


def get_file_content_in_specific_commit(owner, repo, path, commit_sha):
    url = f"{PREFIX}/repos/{owner}/{repo}/contents/{path}?ref={commit_sha}"
    # print(url)
    response_json = requests.request("GET", url, headers=headers, data=payload).json()
    download_url = response_json["download_url"]
    raw_content = requests.request("GET", download_url, headers=headers, data=payload).content
    return raw_content


def get_raw_file_content(url):
    response = requests.get(url, headers=headers)
    return response.content
