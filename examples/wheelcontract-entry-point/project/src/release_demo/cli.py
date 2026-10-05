import argparse


def main(argv=None):
    parser = argparse.ArgumentParser(prog="release-demo")
    parser.add_argument("--version", action="version", version="release-demo 1.0.0")
    parser.parse_args(argv)
    print("hello from the installed wheel")
    return 0
