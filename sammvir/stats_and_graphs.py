import logging
import os
from pathlib import Path


def parse_stats_args():
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-c', '--aligned-contigs',
        help="BAM file of scaffolds aligned to a reference", type=Path,
        dest="aligned_contigs", required=True

    )
    parser.add_argument(
        '-a', '--aligned-reads',
        help="BAM file of reads aligned to the consensus", type=Path,
        dest="aligned_reads", required=True

    )
    parser.add_argument(
        '-s', '--sample-name',
        help="Name of sample", type=str,
        dest="sample_name", required=True
    )
    # parser.add_argument(
    #     '-o', '--output-dir',
    #     help="Directory for output and temp analysis files", type=Path,
    #     dest="output_dir", required=False, default=os.getcwd()
    # )
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
    # parser.add_argument(
    #     '--force-run',
    #     help="Force overwriting existing files in the output directory",
    #     action="store_true", required=False, default=False
    # )
    # parser.add_argument(
    #     '--threads', type=int,
    #     help="Set the number of threads available to use",
    #     required=False, default=None
    # )

    return parser.parse_args()


def run_stats(*args, **kwargs):
    args = parse_stats_args()

    log_format='%(levelname)s: %(filename)s: line %(lineno)d in %(funcName)s: \n\t%(message)s\n'
    logging.basicConfig(level=args.loglevel, format=log_format)


if __name__ == '__main__':
    # This allows you to do "python run.py"
    run_stats()
