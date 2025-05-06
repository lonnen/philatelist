import argparse
import csv
import json
import os
import sys

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

    api = GitHubAPI(token)

    repositories = []
    has_next_page = True
    end_cursor = None
    RESULTS_PER_PAGE = 100

    query = """
    query UserRepositories($username: String!, $perPage: Int!, $cursor: String) {
      user(login: $username) {
        repositories(first: $perPage, after: $cursor, privacy: PUBLIC, orderBy: {field: UPDATED_AT, direction: DESC}) {
          totalCount
          pageInfo {
            hasNextPage
            endCursor
          }
          nodes {
            name
            description
            updatedAt
            createdAt
            licenseInfo {
              name
            }
          }
        }
      }
    }
    """

    while has_next_page:
        variables = {
            "username": username,
            "perPage": RESULTS_PER_PAGE,
            "cursor": end_cursor,
        }

        try:
            if verbose:
                print(f"Fetching first {RESULTS_PER_PAGE} repositories")
            response = api.query(query, variables)

            if response.get("errors"):
                error_messages = ", ".join([e["message"] for e in response["errors"]])
                raise Exception(error_messages)

            user_data = response["data"]["user"]

            if not user_data:
                raise Exception(f"User '{username}' not found")

            repo_data = user_data["repositories"]
            nodes = repo_data["nodes"]
            page_info = repo_data["pageInfo"]
            total_count = repo_data["totalCount"]

            repositories.extend(nodes)

            if len(repositories) == total_count or not page_info["hasNextPage"]:
                has_next_page = False
                if verbose:
                    print(f"Fetched all {len(repositories)} repositories")
            else:
                end_cursor = page_info["endCursor"]
                if verbose:
                    print(
                        f"Fetched {len(repositories)} of {total_count} repositories..."
                    )

        except Exception as e:
            print(f"Error fetching repositories: {str(e)}")
            sys.exit(1)

    return repositories


if __name__ == "__main__":
    try:
        repositories = main()
        print(f"Total repositories: {len(repositories)}")
        print("Repository Information:")

        # CSV
        for r in repositories:
            if isinstance(r['licenseInfo'], dict):
                r["license"] = r["licenseInfo"]["name"]
            else:
                r["license"] = None
            del r["licenseInfo"]
        fieldnames = ['name', 'description', 'updatedAt', 'createdAt', 'license']
        writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(repositories)

        # JSON output
        #print(json.dumps(repositories, indent=2))

        # Formatted Text
        # for i, repo in enumerate(repositories, 1):
        #     print(f"{i}. {repo['name']}")
        #     description = repo.get("description") or "(No description)"
        #     print(f"   Description: {description}")
        #     print(f"   License: {license})
        #     print(f"   Last Updated: {updatedAt})
        #     print(f"   Created: {createdAt})
        #     print()

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
