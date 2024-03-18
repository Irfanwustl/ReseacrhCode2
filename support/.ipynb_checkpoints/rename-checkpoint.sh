#!/bin/bash

# Loop through all *_sorted files without an extension
for file in *_sorted; do
    # Check if the file does not have a .bam extension
    if [[ ! -f "${file}.bam" ]]; then
        mv "$file" "${file}.bam"
        echo "Renamed $file to ${file}.bam"
    fi
done

# Loop through all .bai files
for file in *.bai; do
    # Extract the base name without .bai extension
    base_name="${file%.bai}"
    # Check if the base name ends with _sorted
    if [[ $base_name == *_sorted ]]; then
        mv "$file" "${base_name}.bam.bai"
        echo "Renamed $file to ${base_name}.bam.bai"
    fi
done
