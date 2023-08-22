import csv
import datetime

from github import Github, GithubIntegration
from langdetect import detect


def get_access_token():
    # Replace with your GitHub App's ID
    APP_ID = "370145"
    # Replace with the installation ID for your GitHub App
    INSTALLATION_ID = "40297914"
    # Replace with the path to your GitHub App's private key file
    PRIVATE_KEY_FILE = "scrap-al.2023-08-02.private-key.pem"
    with open(PRIVATE_KEY_FILE, "r") as f:
        PRIVATE_KEY = f.read()
    integration = GithubIntegration(APP_ID, PRIVATE_KEY)
    return integration.get_access_token(INSTALLATION_ID)


def extract_data(file_name_sink):
    TOKEN = get_access_token()
    i = 0
    j = 0
    headers = ['Name', 'URL', 'Description', 'Stars', 'Forks', 'DiagramCommits', 'RepoTotalCommits',
               'RepoContributorCount', 'DiagramContributorCount', 'Watchers', 'Pulls', 'DiagramFilePath',
               'DiagramCommitDates', 'RepoCreationDate', 'RepoTotalCommitDates']
    client = Github(login_or_token=TOKEN.token)
    query = "filename:.drawio"
    codes = client.search_code(query=query, sort='indexed', order='desc')
    try:
        for c in codes:
            try:
                r = c.repository
                if detect(str(r.description)) != 'en':
                    # or r.fork or r.forks_count <= 1 or r.stargazers_count <= 1
                    # or r.get_contributors().totalCount <= 1):
                    j = j + 1
                    continue
                a = set()
                # fileNameContents = ";".join([element.name for element in r.get_contents("/")])
                message_content = []
                comments_content = []
                commit_dates = []
                repo_total_commit_dates = []

                # list repo total commits and timestamp
                for commit in r.get_commits(sha=r.default_branch):
                    repo_total_commit_dates.append(commit.commit.author.date.strftime('%Y-%m-%d %H:%M:%S'))

                # list drawio commit dates
                for commit in r.get_commits(sha=r.default_branch, path=c.path):
                    # message_content.append(commit.commit.message.replace('\n', ' '))
                    commit_dates.append(commit.commit.author.date.strftime('%Y-%m-%d %H:%M:%S'))
                    # for com in commit.get_comments():
                    #     comments_content.append(com.body.replace('\n', ' '))
                    if commit.author:
                        a.add(commit.author.id)
                fileChangesCommits = ";".join(message_content)
                fileChangesComments = ";".join(comments_content)
                with open(file_name_sink, 'a', newline='',
                          encoding='utf-8-sig') as csv_file:
                    writer = csv.writer(csv_file, delimiter=',')
                    if i == 0:
                        writer.writerow(headers)
                    writer.writerow([r.name, r.html_url, r.description, r.stargazers_count, r.forks_count,
                                     r.get_commits(sha=r.default_branch, path=c.path).totalCount,
                                     r.get_commits().totalCount,
                                     r.get_contributors().totalCount, len(a),
                                     r.get_watchers().totalCount, r.get_pulls().totalCount, c.path, commit_dates,
                                     r.created_at.strftime('%Y-%m-%d %H:%M:%S'), repo_total_commit_dates])
                print(client.get_rate_limit())
                i += 1
            except Exception as e:
                """
                   Check if token has expired or its near the end to refresh it
                """
                if TOKEN.expires_at < datetime.datetime.now() or client.get_rate_limit().core.remaining < 400:
                    client = Github(login_or_token=get_access_token().token)
                print("Some repos excluded because of the reason: {}".format(str(e)))
    except Exception as e:
        print("Unexpected")
    print(j)
