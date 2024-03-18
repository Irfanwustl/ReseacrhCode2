#!/bin/bash

# Check if the correct number of arguments is given
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <input_folder> <n_motif> <threads>"
    exit 1
fi

# Assign arguments to variables
input_folder="$1"
n_motif="$2"
threads="$3"

# Hardcoded path to the FASTA file
in_fasta="/logo2/irfan/BioInfoSoftware/LIQUORICE/Ref/hg38.p12.fa"

# Create output folder name based on input folder and number of motifs
output_folder="${input_folder}_motifs_${n_motif}"

# Check if output folder already exists
if [ -d "$output_folder" ]; then
    echo "Error: Output folder $output_folder already exists."
    exit 1
fi

# Create the output folder
mkdir "$output_folder"

# Process each BAM file in the input folder
for bam_file in "$input_folder"/*.bam; do
    # Skip if no BAM files are found
    [ -e "$bam_file" ] || continue

    # Extract the base name of the file
    base_name=$(basename "$bam_file" .bam)

    # Define output file path
    output_file="$output_folder/${base_name}_motifs.txt"

    # Time the processing of each BAM file
    echo "Processing $bam_file..."
    time ./process_motifs.sh "$bam_file" "$in_fasta" "$n_motif" "$threads" "$output_file"
done

echo "Processing complete. Output files are in $output_folder."
