"""
runserver.py

Starts the Labs at Yale Application server. Handles command-line argument
parsing, port validation, and checks for the existence of the database file
before launching the Flask app.
"""
import argparse
import os
import sys
from sys import stderr
from fellowship import app
# import ssl
# ssl._create_default_https_context = ssl._create_stdlib_context

DB_PATH = "labsatyale.sqlite"

def parse_arguments():
    """
    Parse command-line arguments for the server.

    Returns:
        argparse.Namespace: Parsed arguments including the server port.
    """
    parser = argparse.ArgumentParser(
        prog = 'runserver.py',
        description = 'The YUAG Search Application',
        allow_abbrev=False
    )

    parser.add_argument(
        "port",
        metavar="port",
        type=str,
        help= "the port at which the server should listen")

    args = parser.parse_args()
    try:
        port = int(args.port)
        if port <= 0:
            raise ValueError
    except ValueError:
        print("Port must be a positive integer", file=stderr)
        sys.exit(1)

    return args


def check_database():
    """

    Checks the database labsatyale.sqlite in the root directory and is accessible.

    """
    if not os.path.exists(DB_PATH):
        print(f"Database '{DB_PATH}' does not exist", file=stderr)
        sys.exit(1)
    if not os.access(DB_PATH, os.R_OK):
        print(f"Database '{DB_PATH}' not accessible", file=stderr)

def main():
    """
        Parses the arguments and run the server on the specified port
    """
    args = parse_arguments()
    check_database()
    try:
        app.run(host='0.0.0.0', port=args.port)
    except OSError as ex:
        print(ex, file=stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
