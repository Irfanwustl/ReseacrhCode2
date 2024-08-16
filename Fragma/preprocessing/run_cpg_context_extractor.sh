#!/bin/bash

# Ensure the script exits if any command fails
set -e

# Check if correct number of arguments is provided
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <input_folder> <reference_genome> <number_of_cores>"
    exit 1
fi

# Input parameters
INPUT_FOLDER=$1
REFERENCE_GENOME=$2
NUM_CORES=$3
OUTPUT_FOLDER="${INPUT_FOLDER}_cpgContext"

# Create the output folder if it does not exist
mkdir -p "$OUTPUT_FOLDER"

# Start timing the script
START_TIME=$(date +%s)

# Export variables for GNU parallel
export OUTPUT_FOLDER
export REFERENCE_GENOME

# Run the Python script in parallel for each file in the input folder
find "$INPUT_FOLDER" -type f | parallel -j "$NUM_CORES" python cpg_context_extractor.py {} "$REFERENCE_GENOME" "$OUTPUT_FOLDER/{/.}_output.tsv"

# End timing the script
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

# Display the duration
echo "Processing complete. Output files are saved in $OUTPUT_FOLDER."
echo "Time taken: $DURATION seconds."
