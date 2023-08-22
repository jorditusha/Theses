import requests
import os
from github import Github
import csv

from find_diagrams_main import get_access_token


def download_diagrams(file_name):
    TOKEN = get_access_token()
    with open(file_name, "r", encoding="utf-8") as files:
        f = csv.reader(files)
        next(f)
        client = Github(login_or_token=TOKEN.token)
        for row in f:
            try:
                root = "drawio_files"
                if not os.path.exists(root):
                    os.mkdir(root)
                """
                Reference to download file binary
                https://github.com/<username>/<repo_name>/blob/<branch>/<path_to_the_file_from_root_dir>
                """
                repo = client.get_repo(row[1].replace("https://github.com/", ""))
                r = requests.get("{}/blob/{}/{}".format(row[1], repo.default_branch, row[11])).json()
                directory = "{}_{}".format(repo.owner.name, repo.name)
                directory = os.path.join(root, directory)
                filename = row[11].split("/")[-1]
                print(directory)
                if not os.path.exists(directory):
                    os.mkdir(directory)
                print(os.path.join(directory, filename))
                with open(os.path.join(directory, filename), "w", encoding="utf-8") as fil:
                    fil.write("".join(r["payload"]["blob"]["rawLines"]))
            except Exception as e:
                print("Repo excluded for this reason :", e)
