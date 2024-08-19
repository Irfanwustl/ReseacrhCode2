import os
import shutil
import pandas as pd
import sys
import argparse
import time

# Set up command-line argument parsing
parser = argparse.ArgumentParser(description="Copy RNA-seq and Methylation files based on a CSV file.")
parser.add_argument('csv_path', type=str, help="Path to the CSV file.")
parser.add_argument('base_directory', type=str, help="Base directory containing subfolders with RNA-seq and Methylation files.")
args = parser.parse_args()

# Start timing
start_time = time.time()

# Load the CSV file
csv_path = args.csv_path
data = pd.read_csv(csv_path)

# Define the directory containing the subfolders with RNA-seq and Methylation files
base_directory = args.base_directory

# Determine the parent directory of the base_directory
parent_directory = os.path.dirname(base_directory)

# Define the destination folders in the parent directory
rna_seq_destination = os.path.join(parent_directory, 'RNA-seq')
methylation_destination = os.path.join(parent_directory, 'Methylation')

# Check if the destination folders already exist and abort if they do
if os.path.exists(rna_seq_destination) or os.path.exists(methylation_destination):
    print(f"Error: One or both of the destination folders ('RNA-seq' or 'Methylation') already exist. Aborting.")
    sys.exit(1)

# Create the destination folders
os.makedirs(rna_seq_destination, exist_ok=False)
os.makedirs(methylation_destination, exist_ok=False)

# Counters for the number of files copied
total_files_copied = 0
rna_files_copied = 0
methylation_files_copied = 0

# Iterate over each row in the CSV
for index, row in data.iterrows():
    # Process RNA-seq files
    rna_file_id = row['rna_file_id']
    rna_file_name = row['rna_file_name']
    
    rna_file_path = os.path.join(base_directory, rna_file_id, rna_file_name)
    
    if os.path.exists(rna_file_path):
        shutil.copy(rna_file_path, rna_seq_destination)
        rna_files_copied += 1
        total_files_copied += 1

    # Process Methylation files
    meth_file_id = row['meth_file_id']
    meth_file_name = row['meth_file_name']
    
    meth_file_path = os.path.join(base_directory, meth_file_id, meth_file_name)
    
    if os.path.exists(meth_file_path):
        shutil.copy(meth_file_path, methylation_destination)
        methylation_files_copied += 1
        total_files_copied += 1

# End timing
end_time = time.time()
elapsed_time = end_time - start_time

# Print the summary
print(f"File copying completed. Total files copied: {total_files_copied}")
print(f"RNA-seq files copied: {rna_files_copied}")
print(f"Methylation files copied: {methylation_files_copied}")
print(f"Time taken: {elapsed_time:.2f} seconds")
