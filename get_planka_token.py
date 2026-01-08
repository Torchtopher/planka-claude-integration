#!/usr/bin/env python3
"""
Helper script to set up Planka token authentication
Guides user through extracting token from browser
"""

import json
import sys
import requests
from pathlib import Path


def main():
    print("=" * 70)
    print("Planka Token Setup for SSO/OIDC Authentication")
    print("=" * 70)
    print()
    print("Since your Planka instance uses SSO, you'll need to extract your")
    print("authentication token from your browser after logging in.")
    print()
    print("STEP 1: Extract Authentication from Browser")
    print("-" * 70)
    print("You need to get the Cookie header from your browser while logged in.")
    print()
    print("Instructions:")
    print("1. Open https://planka.ncssm.edu in your browser")
    print("2. Log in via SSO if you haven't already")
    print("3. Open Developer Tools (F12)")
    print("4. Go to 'Network' tab")
    print("5. Refresh the page or click something in Planka")
    print("6. Click on any request to planka.ncssm.edu (like 'config' or 'projects')")
    print("7. Scroll to 'Request Headers' section")
    print("8. Find the 'Cookie' header and copy its FULL value")
    print()
    print("It should look like:")
    print("  httpOnlyToken=a491e2a0-...; accessToken=eyJhbGci...; accessTokenVersion=1")
    print()
    print("NOTE: You need the httpOnlyToken which can only be seen in Network tab,")
    print("      NOT from console/document.cookie!")
    print()
    print("-" * 70)

    cookie_input = input("\nPaste the full Cookie header value here: ").strip()

    if not cookie_input:
        print("✗ No cookie provided")
        sys.exit(1)
    # Parse cookies
    cookies = {}
    for cookie in cookie_input.split(';'):
        cookie = cookie.strip()
        if '=' in cookie:
            key, value = cookie.split('=', 1)
            cookies[key.strip()] = value.strip()

    # Extract required tokens
    access_token = cookies.get('accessToken')
    http_only_token = cookies.get('httpOnlyToken')
    access_token_version = cookies.get('accessTokenVersion')

    if not access_token:
        print("✗ Could not find 'accessToken' in cookie string")
        sys.exit(1)

    planka_url = "https://planka.ncssm.edu"

    print("\nVerifying authentication...")
    try:
        # Build headers with Bearer token
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:146.0) Gecko/20100101 Firefox/146.0',
            'Accept': '*/*',
            'Referer': f'{planka_url}/'
        }

        # Build cookies dict
        cookies = {
            'accessToken': access_token,
        }
        if http_only_token:
            cookies['httpOnlyToken'] = http_only_token
        if access_token_version:
            cookies['accessTokenVersion'] = access_token_version

        # Test authentication with projects endpoint
        response = requests.get(f"{planka_url}/api/projects", headers=headers, cookies=cookies, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Extract projects from response
        if isinstance(data, dict) and 'items' in data:
            projects = data['items']
        elif isinstance(data, list):
            projects = data
        else:
            projects = []

        print(f"✓ Authentication successful! Found {len(projects)} project(s)")

        if not projects:
            print("✗ No projects found")
            sys.exit(1)

        print("\nAvailable projects:")
        for i, project in enumerate(projects, 1):
            print(f"  {i}. {project['name']} (ID: {project['id']})")

        project_idx = int(input("\nSelect project number: ")) - 1
        if project_idx < 0 or project_idx >= len(projects):
            print("✗ Invalid selection")
            sys.exit(1)

        project = projects[project_idx]

        # Get full project details (includes boards)
        print(f"\nFetching boards for '{project['name']}'...")
        response = requests.get(
            f"{planka_url}/api/projects/{project['id']}",
            headers=headers,
            cookies=cookies,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        # Extract project item (might be wrapped)
        project_data = data.get('item', data) if isinstance(data, dict) else data

        # Get board IDs from project
        board_ids = project_data.get('boardIds', []) if isinstance(project_data, dict) else []

        # Get board objects from 'included' section
        boards = []
        if isinstance(data, dict) and 'included' in data:
            all_boards = [item for item in data['included'].get('boards', []).values()] if isinstance(data['included'].get('boards'), dict) else data['included'].get('boards', [])
            boards = all_boards

        # If boards is a dict, convert to list
        if isinstance(boards, dict):
            boards = list(boards.values())

        if not boards:
            print("✗ No boards found")
            print(f"Debug - project_data keys: {project_data.keys() if isinstance(project_data, dict) else 'not a dict'}")
            print(f"Debug - data keys: {data.keys() if isinstance(data, dict) else 'not a dict'}")
            sys.exit(1)

        print("\nAvailable boards:")
        for i, board in enumerate(boards, 1):
            board_name = board.get('name', 'Unknown') if isinstance(board, dict) else str(board)
            board_id = board.get('id', 'Unknown') if isinstance(board, dict) else str(board)
            print(f"  {i}. {board_name} (ID: {board_id})")

        board_idx = int(input("\nSelect board number: ")) - 1
        if board_idx < 0 or board_idx >= len(boards):
            print("✗ Invalid selection")
            sys.exit(1)

        board = boards[board_idx]

        # Get board details (includes lists)
        board_name = board.get('name', 'Unknown') if isinstance(board, dict) else 'Unknown'
        board_id = board.get('id') if isinstance(board, dict) else board

        print(f"\nFetching lists for board '{board_name}'...")
        response = requests.get(
            f"{planka_url}/api/boards/{board_id}",
            headers=headers,
            cookies=cookies,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        # Extract board item (might be wrapped)
        board_data = data.get('item', data) if isinstance(data, dict) else data

        # Get list objects from 'included' section
        lists = []
        if isinstance(data, dict) and 'included' in data:
            all_lists = [item for item in data['included'].get('lists', []).values()] if isinstance(data['included'].get('lists'), dict) else data['included'].get('lists', [])
            lists = all_lists

        # If lists is a dict, convert to list
        if isinstance(lists, dict):
            lists = list(lists.values())

        if not lists:
            print("✗ No lists found")
            print(f"Debug - board_data keys: {board_data.keys() if isinstance(board_data, dict) else 'not a dict'}")
            print(f"Debug - data keys: {data.keys() if isinstance(data, dict) else 'not a dict'}")
            sys.exit(1)

        print("\nAvailable lists:")
        for i, lst in enumerate(lists, 1):
            list_name = lst.get('name', 'Unknown') if isinstance(lst, dict) else str(lst)
            list_id = lst.get('id', 'Unknown') if isinstance(lst, dict) else str(lst)
            print(f"  {i}. {list_name} (ID: {list_id})")

        list_idx = int(input("\nSelect list number for completed tasks: ")) - 1
        if list_idx < 0 or list_idx >= len(lists):
            print("✗ Invalid selection")
            sys.exit(1)

        lst = lists[list_idx]

        # Save configuration
        config = {
            "planka_url": planka_url,
            "access_token": access_token,
            "project_id": project.get('id') if isinstance(project, dict) else project,
            "project_name": project.get('name', 'Unknown') if isinstance(project, dict) else 'Unknown',
            "board_id": board.get('id') if isinstance(board, dict) else board,
            "board_name": board.get('name', 'Unknown') if isinstance(board, dict) else 'Unknown',
            "list_id": lst.get('id') if isinstance(lst, dict) else lst,
            "list_name": lst.get('name', 'Unknown') if isinstance(lst, dict) else 'Unknown'
        }

        # Add optional cookie values
        if http_only_token:
            config["http_only_token"] = http_only_token
        if access_token_version:
            config["access_token_version"] = access_token_version

        config_path = Path(__file__).parent / "planka_token_config.json"
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

        print(f"\n✓ Configuration saved to {config_path}")
        print("\nYour Planka integration is ready!")
        print("\nTest it with:")
        print("  python planka_token_integration.py 'Test task'")

        print("\n" + "=" * 70)
        print("IMPORTANT: Token Security")
        print("=" * 70)
        print("• Your token is stored in planka_token_config.json")
        print("• Keep this file secure and don't commit it to git")
        print("• The token may expire - if it does, run this script again")
        print("=" * 70)

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            print("✗ Token is invalid or expired")
        else:
            print(f"✗ HTTP Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled.")
        sys.exit(1)
