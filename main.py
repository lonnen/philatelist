import argparse
import os


def main():
    parser = argparse.ArgumentParser(
        description="collect a single user's commits from GitHub"
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

    if not args.token:
        print("WARNING: No GitHub Token. Rate limiting may occur.")
        print("Re-run with --help for more information")

    print(args.username)
    print(args.token)

if __name__ == "__main__":
    main()
