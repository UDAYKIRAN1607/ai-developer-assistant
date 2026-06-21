from jira import JIRA, JIRAError
from backend.config import config

# ── JIRA Client ──────────────────────────────────────────────────

def get_jira_client():
    if not config.JIRA_URL or not config.JIRA_EMAIL or not config.JIRA_API_TOKEN:
        raise ValueError("JIRA_URL, JIRA_EMAIL, and JIRA_API_TOKEN must be set in .env")
    return JIRA(
        server=config.JIRA_URL,
        basic_auth=(config.JIRA_EMAIL, config.JIRA_API_TOKEN)
    )

# ── Fetch Issues ─────────────────────────────────────────────────

def get_project_issues(project_key: str, status: str = None, limit: int = 10) -> dict:
    """
    Fetch issues from a JIRA project.
    project_key: e.g. "DEV", "PROJ"
    status: "To Do" | "In Progress" | "Done" | None (all)
    """
    try:
        jira = get_jira_client()

        jql = f"project = {project_key}"
        if status:
            jql += f' AND status = "{status}"'
        jql += " ORDER BY created DESC"

        issues = jira.search_issues(jql, maxResults=limit)

        issue_list = []
        for issue in issues:
            issue_list.append({
                "key": issue.key,
                "summary": issue.fields.summary,
                "status": issue.fields.status.name,
                "priority": issue.fields.priority.name if issue.fields.priority else "None",
                "assignee": issue.fields.assignee.displayName if issue.fields.assignee else "Unassigned",
                "reporter": issue.fields.reporter.displayName if issue.fields.reporter else "Unknown",
                "issue_type": issue.fields.issuetype.name,
                "created": str(issue.fields.created)[:10],
                "url": f"{config.JIRA_URL}/browse/{issue.key}",
                "description_preview": (str(issue.fields.description or ""))[:200]
            })

        return {
            "project_key": project_key,
            "total_fetched": len(issue_list),
            "status_filter": status or "all",
            "issues": issue_list
        }

    except JIRAError as e:
        return {"error": f"JIRA API error: {e.text}"}
    except ValueError as e:
        return {"error": str(e)}

# ── Fetch Single Issue ───────────────────────────────────────────

def get_issue_detail(issue_key: str) -> dict:
    """
    Fetch full detail of a single JIRA issue.
    issue_key: e.g. "DEV-123"
    """
    try:
        jira = get_jira_client()
        issue = jira.issue(issue_key)

        # Fetch comments
        comments = []
        for comment in issue.fields.comment.comments[-3:]:  # last 3 comments
            comments.append({
                "author": comment.author.displayName,
                "body": str(comment.body)[:300],
                "created": str(comment.created)[:10]
            })

        return {
            "key": issue.key,
            "summary": issue.fields.summary,
            "status": issue.fields.status.name,
            "priority": issue.fields.priority.name if issue.fields.priority else "None",
            "assignee": issue.fields.assignee.displayName if issue.fields.assignee else "Unassigned",
            "reporter": issue.fields.reporter.displayName if issue.fields.reporter else "Unknown",
            "issue_type": issue.fields.issuetype.name,
            "created": str(issue.fields.created)[:10],
            "updated": str(issue.fields.updated)[:10],
            "description": str(issue.fields.description or "")[:500],
            "comments": comments,
            "url": f"{config.JIRA_URL}/browse/{issue.key}"
        }

    except JIRAError as e:
        return {"error": f"JIRA API error: {e.text}"}
    except ValueError as e:
        return {"error": str(e)}

# ── Fetch Project Summary ────────────────────────────────────────

def get_project_summary(project_key: str) -> dict:
    """
    Fetch counts of issues by status for a project.
    """
    try:
        jira = get_jira_client()

        statuses = ["To Do", "In Progress", "Done"]
        summary = {"project_key": project_key, "counts": {}}

        for status in statuses:
            jql = f'project = {project_key} AND status = "{status}"'
            count = jira.search_issues(jql, maxResults=0).total
            summary["counts"][status] = count

        total_jql = f"project = {project_key}"
        summary["total"] = jira.search_issues(total_jql, maxResults=0).total

        return summary

    except JIRAError as e:
        return {"error": f"JIRA API error: {e.text}"}
    except ValueError as e:
        return {"error": str(e)}