#!/usr/bin/env python3
"""
🎯 FIN-tasks CI/CD Monitor
Real-time CI pipeline status with fancy progress indicators!
"""

import json
import os
import sys
import time
from datetime import datetime

import requests

# GitHub API configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # Optional: for higher rate limits
REPO_OWNER = "spencerbutler"
REPO_NAME = "FIN-tasks"
BRANCH = "feature/task-editing"


# ANSI color codes for fancy output
class Colors:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"
    END = "\033[0m"


# Status emojis
STATUS_EMOJIS = {
    "COMPLETED": {"SUCCESS": "✅", "FAILURE": "❌", "NEUTRAL": "⚪"},
    "IN_PROGRESS": "🔄",
    "QUEUED": "⏳",
    "REQUESTED": "📋",
    "WAITING": "⏸️",
    "PENDING": "🟡",
}

# Job status mapping
JOB_STATUS = {
    "success": f"{Colors.GREEN}✅ SUCCESS{Colors.END}",
    "failure": f"{Colors.RED}❌ FAILED{Colors.END}",
    "in_progress": f"{Colors.BLUE}🔄 RUNNING{Colors.END}",
    "queued": f"{Colors.YELLOW}⏳ QUEUED{Colors.END}",
    "neutral": f"{Colors.CYAN}⚪ NEUTRAL{Colors.END}",
    "skipped": f"{Colors.MAGENTA}⏭️ SKIPPED{Colors.END}",
}


def clear_screen():
    """Clear terminal screen"""
    os.system("clear" if os.name == "posix" else "cls")


def format_duration(started_at, completed_at=None):
    """Format duration between timestamps"""
    if not started_at:
        return "N/A"

    start = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
    end = (
        datetime.fromisoformat(completed_at.replace("Z", "+00:00"))
        if completed_at
        else datetime.now()
    )

    duration = end - start
    total_seconds = int(duration.total_seconds())

    if total_seconds < 60:
        return f"{total_seconds}s"
    elif total_seconds < 3600:
        return f"{total_seconds // 60}m {total_seconds % 60}s"
    else:
        return f"{total_seconds // 3600}h {(total_seconds % 3600) // 60}m"


def get_workflow_runs():
    """Fetch latest workflow runs from GitHub API"""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/runs"
    params = {"branch": BRANCH, "per_page": 5}  # Get last 5 runs
    headers = {"Accept": "application/vnd.github.v3+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"

    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()["workflow_runs"]
    except requests.RequestException as e:
        print(f"{Colors.RED}❌ Error fetching workflow runs: {e}{Colors.END}")
        return []


def get_workflow_jobs(run_id):
    """Fetch jobs for a specific workflow run"""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/runs/{run_id}/jobs"
    headers = {"Accept": "application/vnd.github.v3+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()["jobs"]
    except requests.RequestException as e:
        print(f"{Colors.RED}❌ Error fetching workflow jobs: {e}{Colors.END}")
        return []


def display_header():
    """Display fancy header"""
    print(f"""
{Colors.CYAN}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════╗
║                     🚀 FIN-tasks CI/CD Monitor                    ║
║                     Real-time Pipeline Status                      ║
╚══════════════════════════════════════════════════════════════╝{Colors.END}
""")


def display_workflow_status(workflow_runs):
    """Display workflow run status"""
    if not workflow_runs:
        print(
            f"{Colors.YELLOW}⏳ No workflow runs found for branch '{BRANCH}'{Colors.END}"
        )
        return None

    latest_run = workflow_runs[0]
    run_id = latest_run["id"]
    status = latest_run["status"]
    conclusion = latest_run.get("conclusion", "unknown")
    created_at = latest_run["created_at"]
    updated_at = latest_run["updated_at"]

    # Status emoji and color
    if status == "completed":
        if conclusion == "success":
            status_display = f"{Colors.GREEN}✅ SUCCESS{Colors.END}"
        elif conclusion == "failure":
            status_display = f"{Colors.RED}❌ FAILURE{Colors.END}"
        else:
            status_display = f"{Colors.YELLOW}⚠️ {conclusion.upper()}{Colors.END}"
    elif status == "in_progress":
        status_display = f"{Colors.BLUE}🔄 IN PROGRESS{Colors.END}"
    else:
        status_display = f"{Colors.YELLOW}⏳ {status.upper()}{Colors.END}"

    print(f"""
{Colors.BOLD}Latest Workflow Run:{Colors.END}
├── Run ID: {Colors.CYAN}{run_id}{Colors.END}
├── Branch: {Colors.CYAN}{BRANCH}{Colors.END}
├── Status: {status_display}
├── Started: {Colors.WHITE}{created_at}{Colors.END}
└── Updated: {Colors.WHITE}{updated_at}{Colors.END}
""")

    return run_id, status, conclusion


def display_job_status(jobs):
    """Display detailed job status"""
    if not jobs:
        print(f"{Colors.YELLOW}📋 No jobs found{Colors.END}")
        return

    print(f"{Colors.BOLD}Job Status:{Colors.END}")

    for job in jobs:
        name = job["name"]
        status = job["status"]
        conclusion = job.get("conclusion", "unknown")
        started_at = job.get("started_at")
        completed_at = job.get("completed_at")

        # Format job status
        if status == "completed":
            job_status = JOB_STATUS.get(
                conclusion, f"{Colors.CYAN}❓ {conclusion.upper()}{Colors.END}"
            )
        else:
            job_status = JOB_STATUS.get(
                status, f"{Colors.YELLOW}❓ {status.upper()}{Colors.END}"
            )

        # Duration
        duration = format_duration(started_at, completed_at)

        print(f"├── {Colors.WHITE}{name}{Colors.END}: {job_status} ({duration})")


def main():
    """Main monitoring loop"""
    print(
        f"{Colors.MAGENTA}🎯 Starting CI/CD Monitor... Press Ctrl+C to exit{Colors.END}"
    )
    print(f"{Colors.CYAN}📊 Monitoring branch: {BRANCH}{Colors.END}")
    print(f"{Colors.CYAN}🏠 Repository: {REPO_OWNER}/{REPO_NAME}{Colors.END}")

    last_status = None

    try:
        while True:
            clear_screen()
            display_header()

            workflow_runs = get_workflow_runs()
            result = display_workflow_status(workflow_runs)

            if result:
                run_id, status, conclusion = result
                jobs = get_workflow_jobs(run_id)
                display_job_status(jobs)

                # Check if status changed
                current_status = f"{status}:{conclusion}"
                if last_status != current_status and last_status is not None:
                    print(
                        f"\n{Colors.GREEN}🔄 Status changed: {last_status} → {current_status}{Colors.END}"
                    )
                last_status = current_status

                # Exit if workflow completed
                if status == "completed":
                    print(
                        f"\n{Colors.GREEN}🎉 Workflow completed! Final status: {conclusion.upper()}{Colors.END}"
                    )
                    if conclusion == "success":
                        print(
                            f"{Colors.GREEN}✅ All checks passed! Ready for merge.{Colors.END}"
                        )
                    else:
                        print(
                            f"{Colors.RED}❌ Some checks failed. Check the details above.{Colors.END}"
                        )
                    break

            print(
                f"\n{Colors.CYAN}🔄 Refreshing in 10 seconds... (Ctrl+C to exit){Colors.END}"
            )
            time.sleep(10)

    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}👋 Monitoring stopped by user{Colors.END}")


if __name__ == "__main__":
    main()
