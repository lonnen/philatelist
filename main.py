import argparse
import json
import os

import requests

GITHUB_API_URL = "https://api.github.com/graphql"

def main():
    parser = argparse.ArgumentParser(
        description="""collect a single user's commits from GitHub
        
        Because of aggressive rate limiting it is highly recommended that users provide
        a personal access token. The token should have read permissions for repo,
        org, gist, user, user:email, and project.
        """
    )
    parser.add_argument("username", help="GitHub username of interest")
    parser.add_argument(
        "token",
        nargs="?",
        const=os.environ.get("GITHUB_TOKEN"),
        default=os.environ.get("GITHUB_TOKEN"),
        help="""(optional) GitHub personal access token - see:
        https://docs.github.com/en/rest/authentication/authenticating-to-the-rest-api""",
    )

    args = parser.parse_args()

    username = args.username
    token = args.token
    if not token:
        print("WARNING: No GitHub Token. Rate limiting may occur.")
        print("Re-run with --help for more information")

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "philatelist"
    }

    if token:
        headers["Authorization"] = f"Bearer {token}"

    response = requests.post(
        GITHUB_API_URL,
        headers=headers,
        json={
            "query": "",
            "variables": ""
        }
    )

    if response.status_code == 200:
        return response.json()

    try:
        error_message = json.dumps(response.json(), indent=2)
    except json.JSONDecodeError:
        error_message = response.text
    raise Exception(f"GitHub API status {response.status_code}: {error_message}")

if __name__ == "__main__":
    main()
