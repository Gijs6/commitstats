import os
import subprocess
import re
from collections import defaultdict
from datetime import datetime, timedelta


def find_git_repos(folders):
    repos = []
    for folder in folders:
        for root, dirs, _ in os.walk(folder):
            if ".git" in dirs:
                repos.append(root)
    return repos


def should_ignore_file(file, ignored_extensions):
    return any(file.endswith(ext) for ext in ignored_extensions)


def parse_git_log(log_output, repo_name, ignored_exts, excluded_commits, result):
    current_date = None

    for line in log_output:
        if not line.strip():
            continue

        match = re.match(r"([a-f0-9]+) (\d{4}-\d{2}-\d{2})", line.strip())
        if match:
            commit, date = match.groups()
            if commit not in excluded_commits.get(repo_name, []):
                current_date = date
            else:
                current_date = None
            continue

        if current_date:
            parts = line.split("\t")
            if len(parts) < 3:
                continue

            try:
                added = int(parts[0]) if parts[0] != "-" else 0
                deleted = int(parts[1]) if parts[1] != "-" else 0
                file = parts[2]
            except ValueError:
                continue

            if not should_ignore_file(file, ignored_exts):
                changes = added + deleted
                result[current_date]["value"] += changes
                result[current_date]["repos"][repo_name] = (
                    result[current_date]["repos"].get(repo_name, 0) + changes
                )


def get_lines_changed_per_day(
    project_folders, mails, repos_to_name, file_extensions_to_ignore, excluded_commits
):
    result = defaultdict(lambda: {"value": 0, "repos": {}})
    print(f"Searching for changes by: {', '.join(mails)}")

    repos = find_git_repos(project_folders)
    print(f"{len(repos)} repos found with a .git dir")

    since = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
    ignored_exts = set(file_extensions_to_ignore)
    known_repos = set(name.lower() for name in repos_to_name)

    excluded_repos = []

    for repo in repos:
        try:
            url = subprocess.check_output(['git', 'remote', 'get-url', 'origin'], text=True, cwd=repo).strip()
            name = url.split('/')[-1]
            if name.endswith('.git'):
                name = name[:-4]
        except subprocess.CalledProcessError:
            name = os.path.basename(repo)

        if name.lower() not in known_repos:
            excluded_repos.append(name)
            repo_name = "Other"
        else:        
            repo_name = name

        print(f"Processing {repo_name}")

        for email in mails:
            try:
                log = (
                    subprocess.check_output(
                        [
                            "git",
                            "log",
                            "--since",
                            since,
                            "--author",
                            email,
                            "--numstat",
                            "--pretty=format:%h %ad",
                            "--date=short",
                        ],
                        cwd=repo,
                        stderr=subprocess.DEVNULL,
                    )
                    .decode("utf-8")
                    .splitlines()
                )

                parse_git_log(log, repo_name, ignored_exts, excluded_commits, result)

            except subprocess.CalledProcessError:
                print(f"Error processing repo {repo_name} for email {email}")
    print(f"Success! Repos that were excluded are {", ".join(excluded_repos)}")
    return result
