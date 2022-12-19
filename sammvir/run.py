import logging


def parse_args():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-d', '--debug',
        help="Print lots of debugging statements",
        action="store_const", dest="loglevel", const=logging.DEBUG,
        default=logging.WARNING,
    )
    parser.add_argument(
        '-v', '--verbose',
        help="Be verbose",
        action="store_const", dest="loglevel", const=logging.INFO,
    )
    parser.add_argument(
        '-q', '--quiet',
        help="Be quiet: silence warnings",
        action="store_const", dest="loglevel", const=logging.ERROR,
    )

    return parser.parse_args()


def run(*args, **kwargs):
    args = parse_args()
    logging.basicConfig(level=args.loglevel)
    logging.warning("There is not yet any code to run")


if __name__ == '__main__':
    # This allows you to do "python run.py"
    run()
