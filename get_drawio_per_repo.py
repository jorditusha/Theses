import datetime
import sys

from github import Github
import csv

from find_diagrams_main import get_access_token


def do_extensive_search(sink_file):
    TOKEN = get_access_token()
    csv.field_size_limit(int(sys.maxsize / 10000000000))
    with open(sink_file, 'r', encoding="utf-8") as f:
        rows = csv.reader(f)
        next(rows)
        username_repo_names = set()
        file_paths_processed = []
        repo_total_commits = {}
        for row in rows:
            url = row[1]
            username_repo_names.add(url.replace("https://github.com/", ""))
            file_paths_processed.append(url + "/" + row[11])
            repo_total_commits[url] = row[14]
        """
        Define github client
        """
        client = Github(login_or_token=TOKEN.token)
        final_file_name = ""
        for username_repo_name in username_repo_names:
            try:
                draw_io_s = client.search_code(query="repo:{} extension:drawio".format(username_repo_name))
                print(username_repo_name, draw_io_s.totalCount)
                for d in draw_io_s:
                    drawio_total_commit_dates = []
                    r = d.repository
                    file_path = d.path
                    file_absolute_path = r.html_url + "/" + file_path
                    """
                    Here check if file has already been processed
                    """
                    if file_absolute_path in file_paths_processed:
                        print("File already processed", file_path)
                        continue
                    """
                    Get contributor count by commit authors distinct value using set
                    """
                    authors = set()
                    for commit in r.get_commits(sha=r.default_branch, path=file_path):
                        if commit.author:
                            authors.add(commit.author.id)
                        """
                        Get drawio commit dates
                        """
                        drawio_total_commit_dates.append(commit.commit.author.date.strftime('%Y-%m-%d %H:%M:%S'))

                    """
                    write each row information to the file with append mode
                    """
                    final_file_name = "{}_final".format(sink_file)
                    with open(final_file_name, 'a', newline='',
                              encoding='utf-8-sig') as csv_file:
                        writer = csv.writer(csv_file, delimiter=',')
                        writer.writerow([r.name, r.html_url, r.description, r.stargazers_count, r.forks_count,
                                         r.get_commits(sha=r.default_branch, path=file_path).totalCount,
                                         r.get_commits().totalCount,
                                         r.get_contributors().totalCount, len(authors),
                                         r.get_watchers().totalCount, r.get_pulls().totalCount, file_path,
                                         drawio_total_commit_dates,
                                         r.created_at.strftime('%Y-%m-%d %H:%M:%S'), repo_total_commits[r.html_url]])
            except Exception as e:
                """
                Check if token has expired or its near the end to refresh it
                """
                if TOKEN.expires_at < datetime.datetime.now() or client.get_rate_limit().core.remaining < 400:
                    client = Github(login_or_token=get_access_token().token)

            print(client.get_rate_limit())
        return final_file_name
