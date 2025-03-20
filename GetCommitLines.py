import os
import subprocess
import re
from collections import defaultdict
from datetime import datetime, timedelta

def get_lines_changed_per_day(project_folders_list, repos_to_name, file_extentions_to_ignore):
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
            log_output = subprocess.check_output(["git", "log", "--since", since_date, "--author", email, "--numstat", "--pretty=format:%ad", "--date=short"], cwd=repo).decode("utf-8").splitlines()

            current_date = None
            for line in log_output:
                if line.strip() == "":
                    continue

                if bool(re.search(r'\d{4}-\d{2}-\d{2}', line.strip())):
                    current_date = line.strip()
                else:
                    parts = line.split("\t")
                    if len(parts) >= 2:
                        try:
                            added = int(parts[0]) if parts[0] != '-' else 0
                            deleted = int(parts[1]) if parts[1] != '-' else 0
                            total_changes = added + deleted

                            file = parts[2] if parts[2] else None

                            if current_date and not any(ext in file for ext in file_extentions_to_ignore):
                                all_lines_count[current_date]["value"] += total_changes
                                if repo_name not in all_lines_count[current_date]["repos"]:
                                    all_lines_count[current_date]["repos"][repo_name] = 0
                                all_lines_count[current_date]["repos"][repo_name] += total_changes
                        except ValueError:
                            continue

        except subprocess.CalledProcessError:
            print(f"Error processing repo {repo_name}")

    return all_lines_count
