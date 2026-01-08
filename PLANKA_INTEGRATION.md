# Planka Integration Guide

This integration allows you to automatically create Planka cards from completed tasks when working with Claude.

## Setup (One-time)

Since your Planka instance (`https://planka.ncssm.edu`) uses SSO/OIDC authentication, you'll need to extract your authentication token from your browser.

### Step 1: Run the Setup Script

```bash
cd ~/24-25WaterCode
uv run python scripts/get_planka_token.py
```

### Step 2: Extract Your Token

Follow the script's instructions:

1. Open https://planka.ncssm.edu in your browser
2. Log in via SSO
3. Open Developer Tools (F12 or Right-click → Inspect)
4. Go to the **Application** or **Storage** tab
5. Look for **Local Storage** → `https://planka.ncssm.edu`
6. Find the `accessToken` entry and copy its value

**Alternative method (easier):**
1. In Developer Tools, go to **Console** tab
2. Type: `localStorage.getItem('accessToken')`
3. Press Enter and copy the token (without the quotes)

### Step 3: Complete Configuration

The script will:
- Verify your token
- Show your available projects, boards, and lists
- Let you select where to create cards
- Save the configuration to `planka_token_config.json`

## Usage

### Manual Card Creation

Create a card directly from the command line:

```bash
cd ~/24-25WaterCode
uv run python scripts/planka_token_integration.py "Task name" ["Description"] [type]
```

**Card Types:**
- `project` (default) - Can be marked as complete in Planka. **Recommended for completed tasks.**
- `story` - General story/task card. Use for ongoing work or notes.

**Examples:**

```bash
# Create a project card (default - can mark complete)
uv run python scripts/planka_token_integration.py "Fixed pressure sensor bug"

# Create a project card with description
uv run python scripts/planka_token_integration.py "Fixed pressure sensor bug" "Updated the calibration algorithm"

# Create a story card (for ongoing work)
uv run python scripts/planka_token_integration.py "Research new sensor options" "Investigating alternatives" story

# Create a project card you can mark complete later
uv run python scripts/planka_token_integration.py "Implemented dark mode" "Added theme toggle with persistence" project
```

### Shell Hook (for automation)

Use the shell wrapper (defaults to 'project' type):

```bash
./scripts/planka_hook.sh "Task name" "Optional description"
```

**Note:** The shell hook creates 'project' type cards by default, which can be marked as complete in Planka.

## Security Notes

⚠️ **Important:**
- Your authentication token is stored in `scripts/planka_token_config.json`
- This file is already added to `.gitignore` - **DO NOT commit it to git**
- The token may expire periodically (based on your SSO configuration)
- If you get authentication errors, run `get_planka_token.py` again to refresh your token

## Troubleshooting

### Token Expired
If you see `✗ Authentication failed. Your token may have expired`:
```bash
uv run python scripts/get_planka_token.py
```

### Wrong Project/Board/List
To change where cards are created:
```bash
uv run python scripts/get_planka_token.py
```
Select different options when prompted.

### Can't Find Token in Browser
- Make sure you're logged into Planka
- Try refreshing the page
- The token location may vary by browser:
  - **Chrome/Edge**: Application → Local Storage
  - **Firefox**: Storage → Local Storage
  - **Safari**: Storage → Local Storage

## Card Types Explained

Planka supports two types of cards:

### Project Cards (Default)
- ✅ **Can be marked as complete** with a checkbox
- Perfect for **completed tasks** and accomplishments
- Shows completion status in the UI
- **Recommended** for tracking finished work with Claude

### Story Cards
- General-purpose cards for ongoing work
- Use for research, notes, or work-in-progress items
- Cannot be marked complete (no checkbox)

**Best Practice:** Use `project` type (default) when creating cards for completed tasks so you can check them off later!

## How It Works

1. **Token Extraction**: You extract your SSO authentication token from the browser after logging in
2. **Token Storage**: The token is securely stored locally (never committed to git)
3. **API Calls**: The script uses Planka's REST API with Bearer token + cookies authentication
4. **Card Creation**: Cards are created in your configured project/board/list
5. **Card Type**: Default is `project` so cards can be marked complete

## Files

- `get_planka_token.py` - Interactive setup to extract and configure your token
- `planka_token_integration.py` - Main integration script using token auth
- `planka_hook.sh` - Shell wrapper for easy command-line usage
- `planka_token_config.json` - Your configuration (gitignored, created during setup)

## Known Limitations

- Tokens may expire based on your SSO provider's configuration
- You'll need to refresh the token periodically by running the setup script again
- This is a workaround due to Planka's limited OIDC/SSO API support (see [Issue #1294](https://github.com/plankanban/planka/issues/1294))
- Future versions of Planka may support API keys ([PR #1254](https://github.com/plankanban/planka/pull/1254))
