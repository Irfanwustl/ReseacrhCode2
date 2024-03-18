import os
import gzip
from pathlib import Path
import sys
import time
from tqdm import tqdm

def combine_fastq_files(main_folder, output_folder):
    # Check if output directory already exists
    if Path(output_folder).exists():
        sys.exit(f"Error: The output directory '{output_folder}' already exists. Please specify a different directory or remove the existing one.")
    
    # Create the output directory since it does not exist
    Path(output_folder).mkdir(parents=True)

    # Dictionary to hold file handles for writing
    file_handles = {}

    # Collect all fastq.gz files
    fastq_files = [os.path.join(dp, f) for dp, dn, filenames in os.walk(main_folder) for f in filenames if f.endswith('fastq.gz')]
    
    # Initialize tqdm progress bar
    pbar = tqdm(total=len(fastq_files), desc="Combining FASTQ files", unit="file")

    for file_path in fastq_files:
        subdir, file = os.path.split(file_path)
        # Extract the sample name and read number from the file name
        parts = file.split('_')
        sample_name = 'Sample_'+parts[0] # Adjust index if necessary
        read_number = parts[3]

        


        # Construct the new file name
        new_file_name = f"{sample_name}_{read_number}.fastq.gz"
        new_file_path = os.path.join(output_folder, sample_name, new_file_name)

        # print(parts)
        # print(sample_name)
        # print(read_number)
        # print(new_file_name)
        # print(new_file_path)

        # Ensure output subdirectory exists for the sample
        Path(os.path.join(output_folder, sample_name)).mkdir(parents=True, exist_ok=True)

        # Open the file handle if not already done
        if new_file_path not in file_handles:
            file_handles[new_file_path] = gzip.open(new_file_path, 'wb')

        # Append the content of the current file to the new file
        with gzip.open(file_path, 'rb') as f:
            file_handles[new_file_path].write(f.read())

        # Update the progress bar
        pbar.update(1)

    # Close the progress bar
    pbar.close()

    # Close all file handles
    for fh in file_handles.values():
        fh.close()

if __name__ == '__main__':
    # Check for correct usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python script.py <path_to_main_folder>")

    # Start the timer
    start_time = time.time()

    # Get the main folder from the command line
    main_folder = sys.argv[1]
    output_folder = main_folder + "_combined"

    # Run the file processing function
    combine_fastq_files(main_folder, output_folder)

    # End the timer and print the execution time
    end_time = time.time()
    print(f"Execution time: {end_time - start_time} seconds")
