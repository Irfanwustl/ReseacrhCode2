import pysam
import csv
import argparse
from tqdm import tqdm

def fetch_sequence(reference_genome, chromosome, start):
    """Fetch 12nt genomic context around the CpG site from the reference genome"""
    with pysam.FastaFile(reference_genome) as fasta:
        try:
            sequence = fasta.fetch(chromosome, start-5, start+7)
        except ValueError:
            sequence = None  # Ignore errors
    return sequence

def process_bedgraph(bedgraph_file, reference_genome, output_file, threshold_m=70, threshold_u=30):
    with open(bedgraph_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
        reader = csv.reader(infile, delimiter='\t')
        writer = csv.writer(outfile, delimiter='\t')

        # Get the total number of lines for the progress bar
        total_lines = sum(1 for line in open(bedgraph_file))
        infile.seek(0)

        for row in tqdm(reader, total=total_lines, desc="Processing bedgraph"):
            chromosome, start, end, methylation_value = row[0], int(row[1]), int(row[2]), float(row[3])
            methylation_value *= 100  # Scale methylation value from 0-1 to 0-100
            sequence = fetch_sequence(reference_genome, chromosome, start)
            if sequence is not None:
                if methylation_value > threshold_m:
                    label = 'M'
                elif methylation_value < threshold_u:
                    label = 'U'
                else:
                    continue  # Skip rows where methylation_value is between 30 and 70
                writer.writerow([chromosome, start, end, sequence, methylation_value, label])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process a bedgraph file to fetch sequences and label methylation values.")
    parser.add_argument("bedgraph_file", help="Path to the bedgraph file")
    parser.add_argument("reference_genome", help="Path to the reference genome in fasta format")
    parser.add_argument("output_file", help="Path to the output file")

    args = parser.parse_args()

    process_bedgraph(args.bedgraph_file, args.reference_genome, args.output_file)
