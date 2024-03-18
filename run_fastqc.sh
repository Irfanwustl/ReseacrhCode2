#!/bin/bash

# Check if the required arguments were provided
if [ $# -ne 2 ]; then
    echo "Usage: $0 <number_of_cores> <mother_directory>"
    exit 1
fi

# Assign the arguments to variables
number_of_cores=$1
mother_directory=$2
output_directory="${mother_directory}_fastqc"

# Create the output directory if it doesn't exist
mkdir -p "$output_directory"

# Start timing
start_time=$(date +%s)

# Use find to list all FASTQ files and pipe them to parallel for parallel processing
find "$mother_directory" -name "*.fastq.gz" | parallel -j $number_of_cores fastqc {} -o "$output_directory"

# End timing
end_time=$(date +%s)

# Calculate and print the elapsed time
elapsed=$(( end_time - start_time ))
echo "FastQC processing took $elapsed seconds."
