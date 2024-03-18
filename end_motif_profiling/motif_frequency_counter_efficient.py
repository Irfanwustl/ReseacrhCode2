import itertools
import pandas as pd
import sys
import os
from tqdm import tqdm
import time
from concurrent.futures import ProcessPoolExecutor, as_completed  # Import as_completed
from collections import Counter

def create_motif_dataframe(num_nucleotides, file_names):
    nucleotides = 'ACGT'
    motifs = [''.join(p) for p in itertools.product(nucleotides, repeat=num_nucleotides)]
    motif_df = pd.DataFrame(0, index=motifs, columns=file_names)
    return motif_df

def process_file(file_path, motifs_set):
    counts = Counter()
    with open(file_path, 'r') as file:
        for line in file:
            motif = line.strip().upper()
            if motif in motifs_set:
                counts[motif] += 1
    return counts

def count_motifs_in_files(directory_path, num_nucleotides, num_cores):
    file_names = [f for f in os.listdir(directory_path) if f.endswith('.txt')]
    motifs = [''.join(p) for p in itertools.product('ACGT', repeat=num_nucleotides)]
    motifs_set = set(motifs)
    motif_df = create_motif_dataframe(num_nucleotides, file_names)

    with ProcessPoolExecutor(max_workers=num_cores) as executor:
        future_to_file = {executor.submit(process_file, os.path.join(directory_path, file_name), motifs_set): file_name for file_name in file_names}
        for future in tqdm(as_completed(future_to_file), total=len(file_names), desc="Processing Files"):
            file_name = future_to_file[future]
            counts = future.result()
            for motif, count in counts.items():
                motif_df.at[motif, file_name] = count

    return motif_df

# Check if correct number of command line arguments are provided
if len(sys.argv) != 4:
    print("Usage: python script.py <directory_of_sample_files> <motif_mar_number> <num_cores>")
    sys.exit(1)

directory_path = sys.argv[1]
motif_length = int(sys.argv[2])
num_cores = int(sys.argv[3])

# Start timing the script
start_time = time.time()

# Count motifs and create the dataframe
motif_counts_df = count_motifs_in_files(directory_path, motif_length, num_cores)

# End timing the script
end_time = time.time()

# Set the output file name to be the input folder name with a .txt extension
output_file = directory_path + '.txt'

# Save the dataframe to the output file
motif_counts_df.to_csv(output_file, sep='\t')

# Print out the time taken
print(f"Processed in {end_time - start_time:.2f} seconds.")

# Inform the user where the motif counts were saved
print(f"Motif counts saved to {output_file}")
