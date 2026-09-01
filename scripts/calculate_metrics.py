#!/usr/bin/env python3
"""
Development Metrics Calculator

Analyzes git history and development artifacts to calculate:
- Time spent on each phase/feature
- Efficiency metrics vs traditional development
- Quality metrics and coverage analysis
- Cost analysis and ROI calculations

Usage:
    python scripts/calculate_metrics.py [--output-format json|markdown|console]
    python scripts/calculate_metrics.py --phase-analysis
    python scripts/calculate_metrics.py --cost-analysis
"""

import json
import re
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml


class DevelopmentMetricsCalculator:
    """Calculate development efficiency metrics from git history and artifacts."""

    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        self.project_start = datetime(2024, 12, 15)  # Approximate project start date

        # Industry standard rates (adjustable)
        self.rates = {
            "senior_engineer_daily": 288,  # $150k/year
            "ai_orchestrator_daily": 230,  # $120k/year
            "ai_api_costs_daily": 50,  # Estimated AI tooling costs
        }

        # Traditional team composition for similar projects
        self.traditional_team = {
            "pm": {"count": 1, "weeks": 24},
            "ux_designer": {"count": 1, "weeks": 20},
            "senior_engineer": {"count": 6, "weeks": 20},
            "qa_engineer": {"count": 2, "weeks": 16},
            "security_engineer": {"count": 1, "weeks": 12},
            "devops_engineer": {"count": 1, "weeks": 8},
            "technical_writer": {"count": 1, "weeks": 8},
        }

    def run_git_command(self, cmd: List[str]) -> str:
        """Execute git command and return output."""
        try:
            result = subprocess.run(
                ["git"] + cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"Git command failed: {' '.join(cmd)}")
            print(f"Error: {e.stderr}")
            return ""

    def parse_commit_time(self, commit_info: str) -> Optional[datetime]:
        """Parse commit date from git log output."""
        # Look for date in format: Date:   Mon Jan 20 14:30:45 2025 -0600
        date_match = re.search(r"Date:\s+(.+)", commit_info)
        if date_match:
            try:
                # Parse git date format
                date_str = date_match.group(1).strip()
                # Remove timezone and day name
                parts = date_str.split()
                if len(parts) >= 4:
                    # Convert "Mon Jan 20 14:30:45 2025" format
                    dt_str = f"{' '.join(parts[1:5])} {parts[-1]}"
                    return datetime.strptime(dt_str, "%b %d %H:%M:%S %Y")
            except ValueError:
                pass
        return None

    def analyze_git_history(self) -> Dict:
        """Analyze git commit history for time tracking."""
        # Get detailed commit information
        cmd = [
            "log",
            "--pretty=format:COMMIT_START%n%H%n%aN%n%aE%n%at%n%s%n%b%nCOMMIT_END",
            "--date=iso",
            "--since=2024-12-01",  # Project start date
        ]

        git_output = self.run_git_command(cmd)

        commits = []
        current_commit = {}

        for line in git_output.split("\n"):
            if line == "COMMIT_START":
                current_commit = {}
            elif line == "COMMIT_END":
                if current_commit:
                    commits.append(current_commit)
            elif "hash" not in current_commit:
                current_commit["hash"] = line
            elif "author" not in current_commit:
                current_commit["author"] = line
            elif "email" not in current_commit:
                current_commit["email"] = line
            elif "timestamp" not in current_commit:
                current_commit["timestamp"] = int(line)
                current_commit["datetime"] = datetime.fromtimestamp(int(line))
            elif "subject" not in current_commit:
                current_commit["subject"] = line
            else:
                current_commit["body"] = current_commit.get("body", "") + line + "\n"

        # Analyze commits by phase/feature
        phases = {
            "Phase 1: Spec & Architecture": [],
            "Phase 2: Design & Strategy": [],
            "Inline Task Editing": [],
            "Markdown Support": [],
            "Portability Architecture": [],
        }

        for commit in commits:
            subject = commit.get("subject", "").lower()
            body = commit.get("body", "").lower()

            # Categorize commits
            if any(
                keyword in subject or keyword in body
                for keyword in [
                    "spec",
                    "architecture",
                    "api",
                    "data model",
                    "requirements",
                ]
            ):
                phases["Phase 1: Spec & Architecture"].append(commit)
            elif any(
                keyword in subject or keyword in body
                for keyword in ["design", "strategy", "ui", "ux", "testing", "ci", "cd"]
            ):
                phases["Phase 2: Design & Strategy"].append(commit)
            elif any(
                keyword in subject or keyword in body
                for keyword in ["inline", "editing", "edit"]
            ):
                phases["Inline Task Editing"].append(commit)
            elif any(
                keyword in subject or keyword in body
                for keyword in ["markdown", "react-markdown"]
            ):
                phases["Markdown Support"].append(commit)
            elif any(
                keyword in subject or keyword in body
                for keyword in ["portability", "adr", "documentation", "readme"]
            ):
                phases["Portability Architecture"].append(commit)

        # Calculate time per phase (assuming 4 hours per commit on average)
        phase_metrics = {}
        for phase, commits_list in phases.items():
            commit_count = len(commits_list)
            estimated_hours = commit_count * 4  # Rough estimate

            if commits_list:
                start_date = min(c["datetime"] for c in commits_list)
                end_date = max(c["datetime"] for c in commits_list)
                calendar_days = (end_date - start_date).days + 1
            else:
                calendar_days = 0

            phase_metrics[phase] = {
                "commits": commit_count,
                "estimated_hours": estimated_hours,
                "calendar_days": calendar_days,
            }

        return phase_metrics

    def calculate_quality_metrics(self) -> Dict:
        """Calculate code quality metrics."""
        metrics = {}

        # Test coverage (from coverage reports)
        try:
            coverage_file = self.repo_path / "htmlcov" / "index.html"
            if coverage_file.exists():
                with open(coverage_file) as f:
                    content = f.read()
                    # Extract coverage percentage
                    coverage_match = re.search(r"(\d+)%", content)
                    if coverage_match:
                        metrics["test_coverage"] = int(coverage_match.group(1))
        except:
            pass

        # Count test files
        test_files = list(self.repo_path.glob("tests/**/*.py"))
        metrics["test_files"] = len(test_files)

        # Count source files
        src_files = list((self.repo_path / "src").glob("**/*.py")) + list(
            (self.repo_path / "frontend" / "src").glob("**/*.{ts,tsx}")
        )
        metrics["source_files"] = len(src_files)

        # Documentation files
        docs = list((self.repo_path / "docs").glob("**/*.md"))
        metrics["documentation_files"] = len(docs)

        return metrics

    def calculate_cost_analysis(self) -> Dict:
        """Calculate cost comparison between traditional and AI approaches."""
        # Get time metrics
        time_data = self.analyze_git_history()

        # Calculate AI-orchestrated costs
        total_ai_hours = sum(phase["estimated_hours"] for phase in time_data.values())
        total_calendar_days = max(
            (phase["calendar_days"] for phase in time_data.values()), default=0
        )

        ai_orchestrator_cost = total_calendar_days * self.rates["ai_orchestrator_daily"]
        ai_api_costs = total_calendar_days * self.rates["ai_api_costs_daily"]
        total_ai_cost = ai_orchestrator_cost + ai_api_costs

        # Calculate traditional development costs
        traditional_person_weeks = 0
        for role, details in self.traditional_team.items():
            traditional_person_weeks += details["count"] * (
                details["weeks"] / 5
            )  # Convert to person-weeks

        traditional_daily_cost = sum(
            details["count"] * self.rates["senior_engineer_daily"]
            for details in self.traditional_team.values()
        )

        # Assume 19-28 weeks traditional timeline
        traditional_cost_low = 19 * 5 * traditional_daily_cost  # 19 weeks
        traditional_cost_high = 28 * 5 * traditional_daily_cost  # 28 weeks

        return {
            "ai_orchestrated": {
                "total_cost": total_ai_cost,
                "orchestrator_cost": ai_orchestrator_cost,
                "api_costs": ai_api_costs,
                "hours": total_ai_hours,
                "days": total_calendar_days,
            },
            "traditional": {
                "cost_range": [traditional_cost_low, traditional_cost_high],
                "person_weeks": traditional_person_weeks,
                "daily_rate": traditional_daily_cost,
            },
            "efficiency": {
                "cost_savings_low": (
                    traditional_cost_low / total_ai_cost if total_ai_cost > 0 else 0
                ),
                "cost_savings_high": (
                    traditional_cost_high / total_ai_cost if total_ai_cost > 0 else 0
                ),
                "time_savings": (
                    133 / total_calendar_days if total_calendar_days > 0 else 0
                ),  # vs 133 working days
            },
        }

    def generate_report(self, output_format: str = "markdown") -> str:
        """Generate comprehensive metrics report."""
        time_data = self.analyze_git_history()
        quality_data = self.calculate_quality_metrics()
        cost_data = self.calculate_cost_analysis()

        if output_format == "json":
            return json.dumps(
                {
                    "time_analysis": time_data,
                    "quality_metrics": quality_data,
                    "cost_analysis": cost_data,
                    "generated_at": datetime.now().isoformat(),
                },
                indent=2,
            )

        elif output_format == "markdown":
            report = [
                f"# Development Metrics Report\n\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            ]

            # Time Analysis
            report.append("## Time Analysis by Phase\n")
            report.append("| Phase | Commits | Est. Hours | Calendar Days |")
            report.append("|-------|---------|------------|---------------|")
            for phase, data in time_data.items():
                report.append(
                    f"| {phase} | {data['commits']} | {data['estimated_hours']} | {data['calendar_days']} |"
                )
            report.append("")

            # Quality Metrics
            report.append("## Quality Metrics\n")
            for metric, value in quality_data.items():
                report.append(f"- **{metric.replace('_', ' ').title()}**: {value}")
            report.append("")

            # Cost Analysis
            report.append("## Cost Analysis\n")
            ai = cost_data["ai_orchestrated"]
            trad = cost_data["traditional"]
            eff = cost_data["efficiency"]

            report.append(f"### AI-Orchestrated Cost: ${ai['total_cost']:,.0f}")
            report.append(f"- Orchestrator: ${ai['orchestrator_cost']:,.0f}")
            report.append(f"- AI API/Tooling: ${ai['api_costs']:,.0f}")
            report.append(f"- Total Time: {ai['hours']} hours ({ai['days']} days)")
            report.append("")

            report.append(
                f"### Traditional Development Cost: ${trad['cost_range'][0]:,.0f} - ${trad['cost_range'][1]:,.0f}"
            )
            report.append(
                f"- Team Size: {sum(d['count'] for d in self.traditional_team.values())} people"
            )
            report.append(f"- Person-Weeks: {trad['person_weeks']:.0f}")
            report.append("")

            report.append("### Efficiency Gains")
            report.append(
                f"- **Cost Savings**: {eff['cost_savings_low']:.0f}x - {eff['cost_savings_high']:.0f}x"
            )
            report.append(f"- **Time Savings**: {eff['time_savings']:.1f}x faster")
            report.append(
                f"- **Resource Efficiency**: {trad['person_weeks']/ai['days']:.0f}x more efficient"
            )

            return "\n".join(report)

        else:  # console
            time_data = self.analyze_git_history()
            cost_data = self.calculate_cost_analysis()

            print("🕒 Development Time Analysis:")
            for phase, data in time_data.items():
                print(
                    f"  {phase}: {data['estimated_hours']} hours, {data['calendar_days']} days"
                )

            print("\n💰 Cost Analysis:")
            ai = cost_data["ai_orchestrated"]
            trad = cost_data["traditional"]
            eff = cost_data["efficiency"]

            print(f"  AI Cost: ${ai['total_cost']:,.0f} ({ai['days']} days)")
            print(
                f"  Traditional Cost: ${trad['cost_range'][0]:,.0f} - ${trad['cost_range'][1]:,.0f}"
            )
            print(
                f"  Cost Savings: {eff['cost_savings_low']:.0f}x - {eff['cost_savings_high']:.0f}x"
            )
            print(f"  Time Savings: {eff['time_savings']:.1f}x faster")

            return "Report printed to console"


def main():
    """Main entry point for metrics calculation."""
    import argparse

    parser = argparse.ArgumentParser(description="Calculate development metrics")
    parser.add_argument(
        "--output-format",
        choices=["json", "markdown", "console"],
        default="markdown",
        help="Output format",
    )
    parser.add_argument("--output-file", help="Output file (default: stdout)")
    parser.add_argument(
        "--phase-analysis", action="store_true", help="Detailed phase analysis"
    )
    parser.add_argument(
        "--cost-analysis", action="store_true", help="Focus on cost analysis"
    )

    args = parser.parse_args()

    calculator = DevelopmentMetricsCalculator()

    if args.phase_analysis:
        time_data = calculator.analyze_git_history()
        print("Phase Analysis:")
        for phase, data in time_data.items():
            print(f"  {phase}:")
            print(f"    Commits: {data['commits']}")
            print(f"    Est. Hours: {data['estimated_hours']}")
            print(f"    Calendar Days: {data['calendar_days']}")

    elif args.cost_analysis:
        cost_data = calculator.calculate_cost_analysis()
        print("Cost Analysis:")
        ai = cost_data["ai_orchestrated"]
        trad = cost_data["traditional"]
        eff = cost_data["efficiency"]

        print(f"AI Cost: ${ai['total_cost']:,.0f}")
        print(
            f"Traditional Cost: ${trad['cost_range'][0]:,.0f} - ${trad['cost_range'][1]:,.0f}"
        )
        print(
            f"Cost Savings: {eff['cost_savings_low']:.0f}x - {eff['cost_savings_high']:.0f}x"
        )

    else:
        report = calculator.generate_report(args.output_format)

        if args.output_file:
            with open(args.output_file, "w") as f:
                f.write(report)
            print(f"Report saved to {args.output_file}")
        else:
            print(report)


if __name__ == "__main__":
    main()
