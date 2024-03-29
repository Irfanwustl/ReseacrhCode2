#!/bin/bash
set -o errexit   # abort on nonzero exitstatus
set -o nounset   # abort on unbound variable
set -o pipefail  # don't hide errors within pipes

# Input and output folder paths
input_folder="$1"  # Folder containing BAM files
threads="$2"  # Number of threads to use for parallel processing

output_folder=${input_folder}_dedupped  # Folder to save deduplicated BAM files


# Create the output folder if it doesn't exist
mkdir -p "$output_folder"

# Loop through each BAM file in the input folder
for bam_file in "$input_folder"/*.bam; do
    # Extract the filename without extension
    base_name=$(basename "$bam_file" .bam)

    # Deduplicate the BAM file and save it to the output folder
    output_file="$output_folder/$base_name.dedup.bam"
    samtools sort -@ "$threads" -n -o - "$bam_file" |
        samtools fixmate -m - - |
        samtools sort -@ "$threads" -o - - |
        samtools markdup -@ "$threads" -r - "$output_file"

    # Index the deduplicated BAM file
    samtools index "$output_file"

    echo "Deduplicated $bam_file => $output_file"
done

echo "Deduplication process completed."
