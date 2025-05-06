import argparse
import json
import os

import requests


class GitHubAPI:
    GITHUB_API_URL = "https://api.github.com/graphql"

    headers = {"Content-Type": "application/json", "User-Agent": "philatelist"}

    def __init__(self, token=None):
        self.token = token
        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}"

    def query(self, query, variables):
        """Query the GitHub GraphQL API"""

        response = requests.post(
            self.GITHUB_API_URL,
            headers=self.headers,
            json={"query": query, "variables": variables},
        )

        if response.status_code == 200:
            return response.json()

        try:
            error_message = json.dumps(response.json(), indent=2)
        except json.JSONDecodeError:
            error_message = response.text
        raise Exception(f"GitHub API status {response.status_code}: {error_message}")


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
    parser.add_argument("-v", "--verbose", action="store_true")

    args = parser.parse_args()

    username = args.username
    token = args.token
    verbose = args.verbose
    if verbose:
        print("Initialized with the following config:")
        print("    VERBOSE=TRUE")
        print(f"    USERNAME: {username}")
        print(f"    TOKEN: {token}")
    if not token:
        print("WARNING: No GitHub Token. Rate limiting may occur.")
        print("Re-run with --help for more information")
    
    api = GitHubAPI()
    return api.query({}, {})


if __name__ == "__main__":
    main()
