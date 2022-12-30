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


def align_contigs_to_ref(contigs: Path, reference: Path, align_dir: Path,
                         sample_name: str, dry_run: bool = False):

    sam_file = align_dir / f"{sample_name}.aligned.sam"
    # Note: this was tested on conda-installed bwa-mem2
    bwa_mem2_fa_command = [
        'bwa-mem2', 'mem', str(reference), str(contigs), '-o',
        str(sam_file)
    ]

    logging.info(f"bwa mem command: {shlex.join(bwa_mem2_fa_command)}")

    if not dry_run:
        os.system(shlex.join(bwa_mem2_fa_command))
        if not sam_file.exists():
            logging.error(
                f"Contig alignment file {sam_file} failed to generate")
            exit(1)

    return sam_file, bwa_mem2_fa_command


def sam_to_bam(sam_file: Path, reference: Path, dry_run: bool = False):

    bam_file = sam_file.with_suffix('.bam')

    sam_to_bam_command = [
        'samtools', 'view', '-bh', '-o', str(bam_file), str(sam_file),
        '-T', str(reference)
    ]

    logging.info(f"sam to bam command: {shlex.join(sam_to_bam_command)}")

    if not dry_run:
        os.system(shlex.join(sam_to_bam_command))
        if not bam_file.exists():
            logging.error(
                f"bam file {bam_file} failed to generate")
            exit(1)

    return bam_file, sam_to_bam_command


def sort_bam(unsorted_bam: Path, dry_run: bool = False):

    sorted_bam = unsorted_bam.with_suffix('.sorted.bam')

    sort_bam_command = [
        'samtools', 'sort', '-o', str(sorted_bam), str(unsorted_bam)
    ]

    logging.info(f"Sort bam command: {shlex.join(sort_bam_command)}")

    if not dry_run:
        os.system(shlex.join(sort_bam_command))
        if not sorted_bam.exists():
            logging.error(
                f"Sorted bam file {sorted_bam} failed to generate")
            exit(1)

    return sorted_bam, sort_bam_command

def samtools_index_bam(bam_file: Path, dry_run: bool = False):
    bam_index = bam_file.with_suffix('.bam.bai')

    samtools_index_command = [
        'samtools', 'index', str(bam_file)
    ]

    logging.info(f"Index bam command: {shlex.join(samtools_index_command)}")

    if not dry_run:
        os.system(shlex.join(samtools_index_command))
        if not bam_index.exists():
            logging.error(
                f"Indexed bam file {bam_index} failed to generate")
            exit(1)

    return bam_index, samtools_index_command

def align_reads_to_consensus(r1_fastq: Path, r2_fastq: Path, reference: Path,
                             align_dir: Path, sample_name: str,
                             dry_run: bool = False):

    sam_file = align_dir / f"{sample_name}.consensus.aligned.sam"
    # Note: this was tested on conda-installed bwa-mem2
    bwa_mem2_fq_command = [
        'bwa-mem2', 'mem', str(reference), '-o', str(sam_file), str(r1_fastq),
	 str(r2_fastq)
    ]

    logging.info(f"bwa mem command: {shlex.join(bwa_mem2_fq_command)}")

    if not dry_run:
        os.system(shlex.join(bwa_mem2_fq_command))
        if not sam_file.exists():
            logging.error(
                f"Read alignment file {sam_file} failed to generate")
            exit(1)

    return sam_file, bwa_mem2_fq_command


def call_samtools_consensus(sorted_bam: Path, output_dir: Path,
                            sample_name: str, dry_run: bool = False):

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

def bwa_index_fasta(fasta: Path, dry_run: bool = False):
    if str(fasta).endswith('.fasta'):
        fasta_index = fasta.with_suffix('.fasta.pac')
        logging.info(f"FASTA index {fasta_index}")
    elif str(fasta).endswith('.fa'):
        fasta_index = fasta.with_suffix('.fa.pac')
        logging.info(f"FASTA index {fasta_index}")
    else:
        logging.error(f"unrecognized extension on fasta {fasta}")

    bwa_index_fasta_command =[
        'bwa-mem2', 'index', str(fasta)
    ]

    logging.info(f"bwa index command: {shlex.join(bwa_index_fasta_command)}")

    if not dry_run:
        os.system(shlex.join(bwa_index_fasta_command))
        if not fasta_index.exists():
            # This is actually just one of the files BWA generates.
            # Quick stand in to ensure it runs properly.
            logging.error(
                f"FASTA index {fasta_index} failed to generate")
            exit(1)

    return fasta_index, bwa_index_fasta_command

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
        '--reference',
        help="Reference genome for virus", type=Path,
        dest="reference", required=True
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

    log_format='%(levelname)s: %(filename)s: line %(lineno)d in %(funcName)s: \n\t%(message)s\n'
    logging.basicConfig(level=args.loglevel, format=log_format)

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

    align_dir = tmp_dir / "bwa"

    if not align_dir.exists():
        align_dir.mkdir()

    aligned_contigs, align_contigs_cmd = align_contigs_to_ref(
        contigs, args.reference, align_dir, args.sample_name,
        dry_run=args.dry_run)

    bam_aligned_contigs, sam_to_bam_cmd = sam_to_bam(
        aligned_contigs, args.reference, dry_run=args.dry_run)

    sorted_aligned_contigs, sort_bam_cmd = sort_bam(
        bam_aligned_contigs, dry_run=args.dry_run)

    indexed_bam, index_bam_cmd  = samtools_index_bam(
        sorted_aligned_contigs, dry_run=args.dry_run)

    consensus_fasta, samtools_consensus_cmd = call_samtools_consensus(
        sorted_aligned_contigs, align_dir, args.sample_name,
        dry_run=args.dry_run)

    # Map all the high quality reads to the new consensus
    indexed_fasta, bwa_index_fasta_cmd = bwa_index_fasta(
        consensus_fasta, dry_run=args.dry_run)

    aligned_reads, align_reads_cmd = align_reads_to_consensus(
        r1_fq_trim, r2_fq_trim, consensus_fasta, align_dir, args.sample_name,
        dry_run=args.dry_run)

    bam_aligned_reads, read_sam_to_bam_cmd = sam_to_bam(
        aligned_reads, consensus_fasta, dry_run=args.dry_run)

    sorted_bam_aligned_reads, sort_bam_aligned_reads = sort_bam(
        bam_aligned_reads, dry_run=args.dry_run)

    indexed_reads_bam, index_reads_bam_cmd = samtools_index_bam(
        sorted_bam_aligned_reads, dry_run=args.dry_run)


if __name__ == '__main__':
    # This allows you to do "python run.py"
    run()
