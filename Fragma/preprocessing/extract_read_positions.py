import pysam
import argparse

def extract_positions(bam_file, mapq_threshold):
    # Open the BAM file
    bam = pysam.AlignmentFile(bam_file, "rb")

    # List to store the read positions
    positions = []

    # Iterate through each read in the BAM file
    for read in bam.fetch():
        # Check if the read's mapping quality is above the threshold
        if read.mapping_quality >= mapq_threshold:
            # Extract the start and end positions
            start = read.reference_start
            end = read.reference_end
            # Store the chromosome, start, and end positions
            positions.append((read.reference_name, start, end))

    # Close the BAM file
    bam.close()

    return positions

def write_positions_to_file(positions, output_file):
    with open(output_file, 'w') as f:
        for pos in positions:
            f.write(f"{pos[0]}\t{pos[1]}\t{pos[2]}\n")

def main():
    # Create the parser
    parser = argparse.ArgumentParser(description='Extract start and end positions of reads from a BAM file based on MAPQ threshold.')

    # Add arguments
    parser.add_argument('bam_file', type=str, help='Path to the BAM file')
    parser.add_argument('mapq_threshold', type=int, help='MAPQ threshold')
    parser.add_argument('output_file', type=str, help='Path to the output file')

    # Parse the arguments
    args = parser.parse_args()
    print(args.bam_file, args.mapq_threshold,args.output_file)

    # Extract positions and write to file
    positions = extract_positions(args.bam_file, args.mapq_threshold)
    write_positions_to_file(positions, args.output_file)
    print(args.mapq_threshold)

   # print(f"Positions extracted and saved to {args.output_file}")

if __name__ == "__main__":
    main()
