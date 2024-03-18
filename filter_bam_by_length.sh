#!/bin/bash

# Start timing the script
start_time=$(date +%s)

# Check if exactly 3 arguments are provided
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <path_to_bam_files> <min_length> <max_length>"
    exit 1
fi

# Assign command line arguments to variables
BAM_DIR="$1"
MIN_LENGTH="$2"
MAX_LENGTH="$3"

# Construct the output directory name
OUTPUT_DIR="${BAM_DIR}_filtered_${MIN_LENGTH}_${MAX_LENGTH}"

# Check if the output directory already exists
if [ -d "$OUTPUT_DIR" ]; then
    echo "Output directory $OUTPUT_DIR already exists. Please remove it or use a different name."
    exit 1
fi

# Create the output directory
mkdir "$OUTPUT_DIR"

# Loop through all BAM files in the directory
for bam_file in "$BAM_DIR"/*.bam; do
    # Extract the filename without the directory and extension
    filename=$(basename "$bam_file" .bam)
    
    # Use samtools and awk to filter reads by length and save to a new BAM file
    samtools view -h "$bam_file" | \
    awk -v min_len="$MIN_LENGTH" -v max_len="$MAX_LENGTH" \
        'length($10) >= min_len && length($10) <= max_len || $1 ~ /^@/' | \
    samtools view -bS - > "$OUTPUT_DIR/${filename}_filtered.bam"
done

# End timing the script
end_time=$(date +%s)

# Calculate the duration
duration=$((end_time - start_time))

echo "Filtering complete."
echo "Time taken: $duration seconds."
