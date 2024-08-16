#!/bin/bash

# Check if sufficient arguments are provided
if [ "$#" -ne 3 ]; then
  echo "Usage: $0 <input_folder> <threshold> <num_cores>"
  exit 1
fi

# Assign arguments to variables
INPUT_FOLDER="$1"
THRESHOLD="$2"
NUM_CORES="$3"

# Define the output folder name based on the input folder and threshold
OUTPUT_FOLDER="${INPUT_FOLDER}_readpos_mapq${THRESHOLD}"

# Create output folder if it doesn't exist
mkdir -p "$OUTPUT_FOLDER"

# Start the timer
START_TIME=$(date +%s)

# Find all BAM files and process them in parallel
find "$INPUT_FOLDER" -name '*.bam' | parallel -j "$NUM_CORES" '
  BAM_FILE={}
  BASE_NAME=$(basename "$BAM_FILE" .bam)
  OUTPUT_FILE="'"$OUTPUT_FOLDER"'/${BASE_NAME}_readPos.txt"
  python3 extract_read_positions.py "$BAM_FILE" '"$THRESHOLD"' "$OUTPUT_FILE"
'

# End the timer
END_TIME=$(date +%s)
RUNTIME=$((END_TIME - START_TIME))

echo "Processing complete. Output files are in $OUTPUT_FOLDER."
echo "Total runtime: $RUNTIME seconds."
