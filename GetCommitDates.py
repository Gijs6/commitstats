import os
import subprocess
from collections import defaultdict
from datetime import datetime, timedelta

def get_commit_dates(project_folders_list, repos_to_name):
    """
    project_folders_list: list of folders with projects/repos in them
    repos_to_name: all the repos the name of which should not be 'Other' (because I can't easily check if a repo is e.g. public or private on gh)
    """
    all_commits_count = defaultdict(lambda: {"value": 0, "repos": {}})

    email = subprocess.check_output(["git", "config", "--get", "user.email"]).decode("utf-8").strip()
    print(f"Searching for commits by {email}")

    repos = []
    for base_dir in project_folders_list:
        for root, dirs, files in os.walk(base_dir):
            if '.git' in dirs:
                print(f"Repo with a .git dir found: {root}")
                repos.append(root)
    print(f"{len(repos)} repos found with a .git dir")
    for repo in repos:
        repo_name = os.path.basename(repo)
        if repo_name.lower() not in repos_to_name:
            repo_name = "Other"
        print(f"Getting log for {repo_name}")
        since_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        commit_data = subprocess.check_output(["git", "log", "--since", since_date, "--author", email, "--pretty=format:%ad", "--date=short"],cwd=repo).decode("utf-8").splitlines()
        print(f"{len(commit_data)} commits found for {repo_name}")
        for commit_date in commit_data:
            all_commits_count[str(commit_date)]["value"] += 1
            if repo_name not in all_commits_count[str(commit_date)]["repos"]:
                all_commits_count[str(commit_date)]["repos"][repo_name] = 0
            all_commits_count[str(commit_date)]["repos"][repo_name] += 1

    print(f"Done! {sum(all_commits_count.values())} commits found in {len(repos)} repos on {len(all_commits_count)} days!")
    return all_commits_count
