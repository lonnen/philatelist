Philatelist
-----------

Fetch information about all repositories held by a single GitHub account and output it to std out. 

Usage:
```bash
    $ gh repo clone lonnen/philatelist
    $ uv venv .venv
    $ uv pip install requests
    $ GITHUB_TOKEN=$GITHUB_TOKEN python main.py -v $USERNAME
```

Replace `$GITHUB_TOKEN` and `$USERNAME` with your token and the username of interest, respectively.

The debugging info is also output to stdout so it's a bit unergonomic but copy the lines you need out of the terminal buffer. Leave out the `-v` flag to make this a bit easier.

There are multiple output formats in the program, but they are not wired up to a flag (yet! patches welcome). If you prefer things written out in text, or in json, or in csv, you may need to modify the program before running it by commenting out or uncommenting a few lines.