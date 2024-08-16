import os
import gzip
from pathlib import Path
import sys
import time
from tqdm import tqdm
from multiprocessing import Pool, cpu_count, Manager

def process_file(args):
    file_path, output_folder, lock = args
    subdir, file = os.path.split(file_path)
    parts = file.split('_')
    sample_name = 'Sample_' + parts[0]  # Adjust index if necessary
    read_number = parts[3]  # Adjust index if necessary

    new_file_name = f"{sample_name}_{read_number}.fastq.gz"
    new_file_path = os.path.join(output_folder, sample_name, new_file_name)

    Path(os.path.join(output_folder, sample_name)).mkdir(parents=True, exist_ok=True)

    with gzip.open(file_path, 'rb') as f, gzip.open(new_file_path, 'ab') as nf:
        nf.write(f.read())

    with lock:
        pbar.update(1)

def combine_fastq_files_parallel(main_folder, num_cores):
    output_folder = f"{main_folder}_combined"
    if Path(output_folder).exists():
        print(f"Error: The output directory '{output_folder}' already exists. Please specify a different directory or remove the existing one.")
        return
    
    Path(output_folder).mkdir(parents=True)
    fastq_files = [os.path.join(dp, f) for dp, dn, filenames in os.walk(main_folder) for f in filenames if f.endswith('fastq.gz')]

    with Manager() as manager:
        lock = manager.Lock()
        global pbar
        pbar = tqdm(total=len(fastq_files), desc="Combining FASTQ files", unit="file")
        with Pool(processes=num_cores) as pool:
            pool.map(process_file, [(file_path, output_folder, lock) for file_path in fastq_files])
        pbar.close()

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python combine_fastq_files.py <path_to_main_folder> <num_cores>")
        sys.exit(1)

    main_folder = sys.argv[1]
    num_cores = int(sys.argv[2])  # Convert the number of cores from string to integer

    # Ensure num_cores does not exceed the available CPU count
    num_cores = min(num_cores, cpu_count())

    start_time = time.time()
    combine_fastq_files_parallel(main_folder, num_cores)
    end_time = time.time()

    print(f"Execution time: {end_time - start_time} seconds")
