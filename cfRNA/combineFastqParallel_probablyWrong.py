import concurrent.futures
import os
import gzip
from pathlib import Path
import sys
import time
import threading
from tqdm import tqdm

def process_file(file_path, output_folder, lock):
    subdir, file = os.path.split(file_path)
    parts = file.split('_')
    sample_name = 'Sample_' + parts[0]  # Adjust index if necessary
    read_number = parts[3]  # This assumes a specific filename format

    new_file_name = f"{sample_name}_{read_number}.fastq.gz"
    new_file_path = os.path.join(output_folder, sample_name, new_file_name)

    # Ensure output subdirectory exists for the sample
    Path(os.path.join(output_folder, sample_name)).mkdir(parents=True, exist_ok=True)

    with lock:
        # Thread-safe writing to the combined file
        with gzip.open(new_file_path, 'ab') as nf:  # Use 'ab' for appending in binary mode
            with gzip.open(file_path, 'rb') as f:
                nf.write(f.read())

def combine_fastq_files(main_folder):
    output_folder = main_folder + '_combined_parallel'
    if Path(output_folder).exists():
        sys.exit(f"Error: The output directory '{output_folder}' already exists. Please specify a different directory or remove the existing one.")
    
    Path(output_folder).mkdir(parents=True)
    
    fastq_files = [os.path.join(dp, f) for dp, dn, filenames in os.walk(main_folder) for f in filenames if f.endswith('fastq.gz')]
    
    lock = threading.Lock()

    with tqdm(total=len(fastq_files), desc="Combining FASTQ files", unit="file") as pbar:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(process_file, file_path, output_folder, lock) for file_path in fastq_files]
            
            for future in concurrent.futures.as_completed(futures):
                pbar.update(1)

if __name__ == '__main__':
    # Check for correct usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python script.py <path_to_main_folder>")

    # Start the timer
    start_time = time.time()

    main_folder = sys.argv[1]

    # Run the file processing function
    combine_fastq_files(main_folder)

    # End the timer and print the execution time
    end_time = time.time()
    print(f"Execution time: {end_time - start_time} seconds")
