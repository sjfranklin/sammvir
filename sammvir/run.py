import logging
from pathlib import Path


def file_exists(my_file: Path, ignore: bool = False):
    if not my_file.exists():
        if not ignore:
            logging.error(f'File {my_file} does not exist')
            exit(1)
        else:
            logging.warning(f'File {my_file} does not exist')
            return False
    else:
        return True


def parse_args():
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-f', '--forward',
        help="R1 (forward) FASTQ file", type=Path,
        dest="r1_fastq", required=True

    )
    parser.add_argument(
        '-r', '--reverse',
        help="R2 (reverse) FASTQ file", type=Path,
        dest="r2_fastq", required=True

    )
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

    parser.add_argument(
        '--dry-run',
        help="Run in dry_run mode: print commands but do not execute",
        action="store_true", required=False, default=False
    )

    return parser.parse_args()


def run(*args, **kwargs):
    args = parse_args()
    logging.basicConfig(level=args.loglevel)

    # Confirm files exist
    file_exists(args.r1_fastq)
    file_exists(args.r2_fastq)


if __name__ == '__main__':
    # This allows you to do "python run.py"
    run()
