#!/usr/bin/env python3
"""
Planka Integration using Bearer Token
For SSO/OIDC authenticated Planka instances
"""

import os
import json
import sys
import requests
from pathlib import Path
from typing import Optional


class PlankaTokenIntegration:
    """Integration with Planka using Bearer token + cookies authentication"""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize Planka integration with config file"""
        if config_path is None:
            config_path = Path(__file__).parent / "planka_token_config.json"

        self.config = self._load_config(config_path)
        self.base_url = self.config['planka_url'].rstrip('/')

        # Need BOTH Authorization header AND cookies for OIDC Planka
        self.headers = {
            'Authorization': f'Bearer {self.config["access_token"]}',
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:146.0) Gecko/20100101 Firefox/146.0',
            'Accept': '*/*',
            'Referer': f'{self.base_url}/'
        }

        # Build cookies dict
        self.cookies = {
            'accessToken': self.config['access_token'],
        }
        if 'http_only_token' in self.config:
            self.cookies['httpOnlyToken'] = self.config['http_only_token']
        if 'access_token_version' in self.config:
            self.cookies['accessTokenVersion'] = self.config['access_token_version']

        self._verify_auth()

    def _load_config(self, config_path: str) -> dict:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)

            required_fields = ['planka_url', 'access_token', 'project_id', 'board_id', 'list_id']
            missing = [f for f in required_fields if f not in config]

            if missing:
                raise ValueError(f"Missing required config fields: {missing}")

            return config
        except FileNotFoundError:
            print(f"Error: Config file not found at {config_path}")
            print("Please run: python get_planka_token.py")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in config file: {e}")
            sys.exit(1)

    def _verify_auth(self):
        """Verify authentication works"""
        try:
            response = requests.get(
                f"{self.base_url}/api/projects",
                headers=self.headers,
                cookies=self.cookies,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()

            # Check if response is wrapped in an "items" key
            if isinstance(data, dict) and 'items' in data:
                projects = data['items']
            elif isinstance(data, list):
                projects = data
            else:
                projects = []

            print(f"✓ Authenticated (found {len(projects)} project(s))")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                print("✗ Authentication failed. Your token may have expired.")
                print("Please run: python get_planka_token.py")
            else:
                print(f"✗ HTTP Error: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"✗ Error verifying authentication: {e}")
            sys.exit(1)

    def _create_task_list(self, card_id: str, name: str = "Tasks") -> str:
        """
        Create a task list on a card

        Args:
            card_id: ID of the card
            name: Name of the task list

        Returns:
            Task list ID if successful, None otherwise
        """
        try:
            task_list_data = {
                "name": name,
                "showOnFrontOfCard": True,
                "position": 65536
            }

            response = requests.post(
                f"{self.base_url}/api/cards/{card_id}/task-lists",
                headers=self.headers,
                cookies=self.cookies,
                json=task_list_data,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            task_list = data.get('item', data) if isinstance(data, dict) else data
            return task_list.get('id')

        except Exception as e:
            print(f"      Debug (task list): {e}")
            return None

    def _add_task_to_list(self, task_list_id: str, task_name: str, position: int = 0) -> bool:
        """
        Add a task to a task list

        Args:
            task_list_id: ID of the task list
            task_name: Name of the task
            position: Position of the task

        Returns:
            True if successful, False otherwise
        """
        try:
            task_data = {
                "name": task_name,
                "position": position
            }

            response = requests.post(
                f"{self.base_url}/api/task-lists/{task_list_id}/tasks",
                headers=self.headers,
                cookies=self.cookies,
                json=task_data,
                timeout=10
            )
            response.raise_for_status()
            return True

        except Exception as e:
            print(f"      Debug (task): {e}")
            return False

    def create_card(self, name: str, description: str = "", card_type: str = "project", tasks: list = None) -> bool:
        """
        Create a card in the configured list

        Args:
            name: Card title
            description: Card description
            card_type: Card type ("project" or "story"). Default "project" allows marking as complete.
            tasks: List of task dicts with 'name' and optional 'description' keys

        Returns:
            True if successful, False otherwise
        """
        if tasks is None:
            tasks = []
        try:
            # Validate card type
            if card_type not in ["project", "story"]:
                print(f"✗ Invalid card type '{card_type}'. Must be 'project' or 'story'")
                return False

            # Create card (type must be "story" or "project")
            card_data = {
                "position": 0,  # Add to top of list
                "name": name,
                "type": card_type  # "project" allows marking complete, "story" is for tasks
            }

            # Add description if provided
            if description:
                card_data["description"] = description

            response = requests.post(
                f"{self.base_url}/api/lists/{self.config['list_id']}/cards",
                headers=self.headers,
                cookies=self.cookies,
                json=card_data,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()

            # Extract card from response (wrapped in 'item')
            card = data.get('item', data) if isinstance(data, dict) else data
            card_id = card.get('id')

            print(f"✓ Created Planka card: '{name}' (type: {card_type})")
            if description:
                print(f"  Description: {description[:50]}..." if len(description) > 50 else f"  Description: {description}")

            # Add tasks if provided
            if tasks and card_id:
                print(f"  Adding {len(tasks)} task(s)...")
                for i, task in enumerate(tasks, 1):
                    task_name = task.get('name') if isinstance(task, dict) else str(task)
                    task_created = self._add_task_to_card(card_id, task_name)
                    if task_created:
                        print(f"    ✓ Task {i}: {task_name}")
                    else:
                        print(f"    ✗ Failed to add task: {task_name}")

            return True

        except requests.exceptions.HTTPError as e:
            print(f"✗ HTTP Error creating card: {e}")
            if e.response:
                print(f"Response: {e.response.text}")
            return False
        except Exception as e:
            print(f"✗ Error creating card: {e}")
            return False


def main():
    """Main entry point for CLI usage"""
    if len(sys.argv) < 2:
        print("Usage: python planka_token_integration.py <task_name> [description] [type]")
        print()
        print("Arguments:")
        print("  task_name    - Card title (required)")
        print("  description  - Card description (optional)")
        print("  type         - Card type: 'project' or 'story' (optional, default: 'project')")
        print()
        print("Card types:")
        print("  project - Can be marked as complete (recommended for tasks)")
        print("  story   - General story/task card")
        print()
        print("Examples:")
        print("  python planka_token_integration.py 'Fix bug'")
        print("  python planka_token_integration.py 'Fix bug' 'Fixed the pressure sensor'")
        print("  python planka_token_integration.py 'Research task' 'Look into options' story")
        sys.exit(1)

    task_name = sys.argv[1]
    description = sys.argv[2] if len(sys.argv) > 2 else ""
    card_type = sys.argv[3] if len(sys.argv) > 3 else "project"

    integration = PlankaTokenIntegration()
    success = integration.create_card(task_name, description, card_type)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
