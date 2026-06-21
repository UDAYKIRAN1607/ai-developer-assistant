from github import Github, GithubException
from backend.config import config

# ── GitHub Client ────────────────────────────────────────────────

def get_github_client():
    if not config.GITHUB_TOKEN:
        raise ValueError("GITHUB_TOKEN is not set in .env")
    return Github(config.GITHUB_TOKEN)

# ── Fetch Issues ─────────────────────────────────────────────────

def get_repo_issues(repo_name: str, state: str = "open", limit: int = 10) -> dict:
    """
    Fetch issues from a GitHub repo.
    repo_name: "owner/repo" format
    state: "open" | "closed" | "all"
    """
    try:
        g = get_github_client()
        repo = g.get_repo(repo_name)
        issues = repo.get_issues(state=state)

        issue_list = []
        for issue in issues[:limit]:
            # Skip pull requests (GitHub API returns PRs as issues too)
            if issue.pull_request:
                continue
            issue_list.append({
                "number": issue.number,
                "title": issue.title,
                "state": issue.state,
                "author": issue.user.login,
                "labels": [label.name for label in issue.labels],
                "created_at": issue.created_at.strftime("%Y-%m-%d"),
                "url": issue.html_url,
                "body_preview": (issue.body or "")[:200]
            })

        return {
            "repo": repo_name,
            "total_fetched": len(issue_list),
            "state_filter": state,
            "issues": issue_list
        }

    except GithubException as e:
        return {"error": f"GitHub API error: {e.data.get('message', str(e))}"}
    except ValueError as e:
        return {"error": str(e)}

# ── Fetch Pull Requests ──────────────────────────────────────────

def get_repo_pull_requests(repo_name: str, state: str = "open", limit: int = 10) -> dict:
    """
    Fetch pull requests from a GitHub repo.
    """
    try:
        g = get_github_client()
        repo = g.get_repo(repo_name)
        pulls = repo.get_pulls(state=state)

        pr_list = []
        for pr in pulls[:limit]:
            pr_list.append({
                "number": pr.number,
                "title": pr.title,
                "state": pr.state,
                "author": pr.user.login,
                "base_branch": pr.base.ref,
                "head_branch": pr.head.ref,
                "created_at": pr.created_at.strftime("%Y-%m-%d"),
                "url": pr.html_url,
                "body_preview": (pr.body or "")[:200]
            })

        return {
            "repo": repo_name,
            "total_fetched": len(pr_list),
            "state_filter": state,
            "pull_requests": pr_list
        }

    except GithubException as e:
        return {"error": f"GitHub API error: {e.data.get('message', str(e))}"}
    except ValueError as e:
        return {"error": str(e)}

# ── Fetch Repo Summary ───────────────────────────────────────────

def get_repo_summary(repo_name: str) -> dict:
    """
    Fetch general repo metadata and stats.
    """
    try:
        g = get_github_client()
        repo = g.get_repo(repo_name)

        return {
            "name": repo.name,
            "full_name": repo.full_name,
            "description": repo.description,
            "language": repo.language,
            "stars": repo.stargazers_count,
            "forks": repo.forks_count,
            "open_issues": repo.open_issues_count,
            "default_branch": repo.default_branch,
            "created_at": repo.created_at.strftime("%Y-%m-%d"),
            "updated_at": repo.updated_at.strftime("%Y-%m-%d"),
            "url": repo.html_url
        }

    except GithubException as e:
        return {"error": f"GitHub API error: {e.data.get('message', str(e))}"}
    except ValueError as e:
        return {"error": str(e)}