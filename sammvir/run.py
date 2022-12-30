import logging
import shlex
import shutil
import os
from pathlib import Path


def run_bbduk(r1_fastq: Path, r2_fastq: Path, output_dir: Path,
              adapters: Path, dry_run: bool = False):
    bbduk_dir = output_dir / 'bbduk'
    if not bbduk_dir.exists():
        bbduk_dir.mkdir()

    r1_base = r1_fastq.name.strip('.fastq.gz')
    r2_base = r2_fastq.name.strip('.fastq.gz')
    r1_fastq_trim_paired = bbduk_dir / f"{r1_base}.trim.paired.fastq.gz"
    r2_fastq_trim_paired = bbduk_dir / f"{r2_base}.trim.paired.fastq.gz"

    bbduk_command = [
        'bbduk.sh', f"in1={r1_fastq}", f"in2={r2_fastq}",
        f"out1={r1_fastq_trim_paired}", f"out2={r2_fastq_trim_paired}",
        f"ref={adapters}", "ktrim=r", "k=23", "mink=11", "hdist=1", "tpe",
        "tbo", "trimq=20"
    ]

    logging.info(f"BBDuk QC command: {shlex.join(bbduk_command)}")

    if not dry_run:
        os.system(shlex.join(bbduk_command))
        for out_file in [r1_fastq_trim_paired, r2_fastq_trim_paired]:
            if not out_file.exists():
                logging.error(
                    f"BBDuk QC file {out_file} failed to generate")
                exit(1)
    return r1_fastq_trim_paired, r2_fastq_trim_paired, shlex.join(bbduk_command)


def run_trimmomatic(r1_fastq: Path, r2_fastq: Path, output_dir: Path,
                    adapters: Path, dry_run: bool = False):

    trim_dir = output_dir / 'trimmomatic'
    if not trim_dir.exists():
        trim_dir.mkdir()

    r1_base = r1_fastq.name.strip('.fastq.gz')
    r2_base = r2_fastq.name.strip('.fastq.gz')
    r1_fastq_trim_paired = trim_dir / f"{r1_base}.trim.paired.fastq.gz"
    r2_fastq_trim_paired = trim_dir / f"{r2_base}.trim.paired.fastq.gz"
    r1_fastq_trim_unpaired = trim_dir / f"{r1_base}.trim.unpaired.fastq.gz"
    r2_fastq_trim_unpaired = trim_dir / f"{r2_base}.trim.unpaired.fastq.gz"

    trimmomatic_command = [
        'trimmomatic', 'PE', str(r1_fastq), str(r2_fastq),
        str(r1_fastq_trim_paired), str(r1_fastq_trim_unpaired),
        str(r2_fastq_trim_paired), str(r2_fastq_trim_unpaired),
        f"ILLUMINACLIP:{adapters}:2:30:10", "LEADING:3",
        "TRAILING:3",  "SLIDINGWINDOW:4:15", "MINLEN:36"
    ]

    logging.info(f"Trimmomatic command: {shlex.join(trimmomatic_command)}")

    if not dry_run:
        os.system(shlex.join(trimmomatic_command))
        for out_file in [r1_fastq_trim_paired, r1_fastq_trim_unpaired,
                         r2_fastq_trim_paired, r2_fastq_trim_unpaired]:
            if not out_file.exists():
                logging.error(
                    f"Trimmomatic file {out_file} failed to generate")
                exit(1)
    return r1_fastq_trim_paired, r2_fastq_trim_paired, shlex.join(trimmomatic_command)


def run_megahit(r1_fastq: Path, r2_fastq: Path, output_dir: Path,
                sample_name: str, dry_run: bool = False):

    megahit_dir = output_dir / "megahit"
    final_contigs = megahit_dir / f"{sample_name}.contigs.fa"
    print(f"\n\n\n{megahit_dir}")
    megahit_command = [
        "megahit", "-1", str(r1_fastq), "-2", str(r2_fastq), "-o",
        str(megahit_dir), "--out-prefix", sample_name
    ]

    logging.info(f"Megahit command: {shlex.join(megahit_command)}")
    if not dry_run:
        os.system(shlex.join(megahit_command))
        if not final_contigs.exists():
            logging.error(
                f"Megahit file {final_contigs} failed to generate")
            exit(1)

    return final_contigs, megahit_command



def call_samtools_consensus(sorted_bam: Path, output_dir: Path,
                            sample_name: str, dry_run: bool = False):
    "samtools consensus -f FASTA 955_contig_assembly.sorted.bam > 955.consensus.fasta"

    consensus_fasta = output_dir / f"{sample_name}.consensus.fasta"

    samtools_consensus_command = [
        'samtools', 'consensus', '-f', 'FASTA', '-m', 'simple', str(sorted_bam),
        '-o', str(consensus_fasta)
    ]

    logging.info(f"Samtools consensus command: {shlex.join(samtools_consensus_command)}")

    if not dry_run:
        os.system(shlex.join(samtools_consensus_command))
        if not consensus_fasta.exists():
            logging.error(
                f"Consensus file {consensus_fasta} failed to generate")
            exit(1)

    return consensus_fasta, samtools_consensus_command


    _
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
        '-a', '--adapters',
        help="File with Illumina adapters", type=Path,
        dest="adapters", required=True

    )
    parser.add_argument(
        '-s', '--sample-name',
        help="Name of sample", type=str,
        dest="sample_name", required=True
    )
    parser.add_argument(
        '--use-bbduk',
        help="Use BBDuk instead of Trimmomatic for read QC",
        action="store_true", required=False, default=False
    )
    parser.add_argument(
        '-o', '--output-dir',
        help="Directory for output and temp analysis files", type=Path,
        dest="output_dir", required=False, default=os.getcwd()
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
    parser.add_argument(
        '--force-run',
        help="Force overwriting existing files in the output directory",
        action="store_true", required=False, default=False
    )

    return parser.parse_args()


def run(*args, **kwargs):
    args = parse_args()
    logging.basicConfig(level=args.loglevel)

    # Confirm files exist
    file_exists(args.r1_fastq)
    file_exists(args.r2_fastq)

    if not args.output_dir.exists():
        args.output_dir.mkdir()

    tmp_dir = args.output_dir / 'tmp'

    if tmp_dir.exists():
        if args.force_run:
            logging.warning(f"Removing and recreating directory {tmp_dir}")
            shutil.rmtree(tmp_dir)
            tmp_dir.mkdir()
        else:
            logging.error(f"Output directory {tmp_dir} already exists. "
                          "Some down-stream software will fail. Specify "
                          "new output directory or use --force-run, which "
                          "will overwrite existing files.")
            exit(1)
    else:
        tmp_dir.mkdir()

    # Run QC on Reads with Trimmomatic or BBDuk
    if args.use_bbduk:
        r1_fq_trim, r2_fq_trim, trim_cmd = run_bbduk(
            args.r1_fastq, args.r2_fastq, tmp_dir, args.adapters,
            dry_run=args.dry_run)
    else:
        r1_fq_trim, r2_fq_trim, trim_cmd = run_trimmomatic(
            args.r1_fastq, args.r2_fastq, tmp_dir, args.adapters,
            dry_run=args.dry_run)

    # Run de novo assembly
    contigs, megahit_cmd = run_megahit(r1_fq_trim, r2_fq_trim, tmp_dir,
                                       args.sample_name, dry_run=args.dry_run)


if __name__ == '__main__':
    # This allows you to do "python run.py"
    run()
