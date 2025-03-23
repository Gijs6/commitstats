import os
import subprocess
import re
from collections import defaultdict
from datetime import datetime, timedelta

def get_lines_changed_per_day(project_folders_list, repos_to_name, file_extensions_to_ignore, excluded_commits):
    """
    project_folders_list: list of folders with projects/repos in them
    repos_to_name: all the repos the name of which should not be 'Other'
    file_extensions_to_ignore: all the file extensions that do not count
    excluded_commits: dict where keys are repo names and values are lists of commit hashes to exclude
    """
    all_lines_count = defaultdict(lambda: {"value": 0, "repos": {}})

    email = subprocess.check_output(["git", "config", "--get", "user.email"]).decode("utf-8").strip()
    print(f"Searching for changes by {email}")

    repos = []
    for base_dir in project_folders_list:
        for root, dirs, files in os.walk(base_dir):
            if '.git' in dirs:
                repos.append(root)

    print(f"{len(repos)} repos found with a .git dir")

    since_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')

    for repo in repos:
        repo_name = os.path.basename(repo)
        if repo_name.lower() not in repos_to_name:
            repo_name = "Other"

        print(f"Processing {repo_name}")

        try:
            log_output = subprocess.check_output(["git", "log", "--since", since_date, "--author", email, "--numstat", "--pretty=format:%h %ad", "--date=short"], cwd=repo).decode("utf-8").splitlines()

            current_date = None
            for line in log_output:
                if line.strip() == "":
                    continue

                match = re.match(r'([a-f0-9]+) (\d{4}-\d{2}-\d{2})', line.strip())
                if match:
                    commit_hash, current_date = match.groups()
                    if repo_name in excluded_commits and commit_hash in excluded_commits[repo_name]:
                        current_date = None  # Ignore subsequent file changes for this commit
                    continue

                if current_date:
                    parts = line.split("\t")
                    if len(parts) >= 3:
                        try:
                            added = int(parts[0]) if parts[0] != '-' else 0
                            deleted = int(parts[1]) if parts[1] != '-' else 0
                            total_changes = added + deleted
                            file = parts[2] if parts[2] else None

                            if not any(ext in file for ext in file_extensions_to_ignore):
                                all_lines_count[current_date]["value"] += total_changes
                                if repo_name not in all_lines_count[current_date]["repos"]:
                                    all_lines_count[current_date]["repos"][repo_name] = 0
                                all_lines_count[current_date]["repos"][repo_name] += total_changes
                        except ValueError:
                            continue
        except subprocess.CalledProcessError:
            print(f"Error processing repo {repo_name}")

    return all_lines_count
