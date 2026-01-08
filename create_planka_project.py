#!/usr/bin/env python3
"""
Helper script for creating Planka project cards with tasks
Used by Claude to create well-structured project cards
"""

import sys
from planka_token_integration import PlankaTokenIntegration


def create_project_with_tasks(project_name: str, description: str, tasks: list):
    """
    Create a project card with tasks

    Args:
        project_name: Name of the project
        description: Project description
        tasks: List of task names or dicts with 'name' keys

    Example tasks:
        ["Research options", "Implement feature", "Write tests"]
        or
        [{"name": "Research options"}, {"name": "Implement feature"}]
    """
    integration = PlankaTokenIntegration()

    # Ensure tasks are in the right format
    task_list = []
    for task in tasks:
        if isinstance(task, str):
            task_list.append({"name": task})
        else:
            task_list.append(task)

    success = integration.create_card(
        name=project_name,
        description=description,
        card_type="project",
        tasks=task_list
    )

    return success


if __name__ == "__main__":
    # Example usage
    if len(sys.argv) < 2:
        print("Usage: python create_planka_project.py <project_name>")
        print()
        print("This script is meant to be used programmatically.")
        print("For manual use, use planka_token_integration.py instead.")
        sys.exit(1)

    # Simple example
    project_name = sys.argv[1]
    description = sys.argv[2] if len(sys.argv) > 2 else ""

    # Example tasks
    example_tasks = [
        "Plan implementation approach",
        "Write code",
        "Test functionality",
        "Document changes"
    ]

    create_project_with_tasks(project_name, description, example_tasks)
