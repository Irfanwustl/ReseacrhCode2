import os
import pandas as pd
import argparse
import time

# Function to combine seg.v2.txt files by category (primary_site and sample_type)
def combine_seg_files_by_category(directory, metadata_csv):
    # Start timing the process to measure execution time
    start_time = time.time()
    
    # Read the metadata file which contains information about file_id, file_name, primary_site, and sample_type
    metadata = pd.read_csv(metadata_csv)
    
    # Filter the metadata to get only file names ending with 'seg.v2.txt'
    seg_files = metadata[metadata['file_name'].str.endswith('seg.v2.txt')]
    
    # Group the metadata by two columns: primary_site and sample_type
    # This allows us to create separate DataFrames for each combination of primary_site and sample_type
    grouped = seg_files.groupby(['primary_site', 'sample_type'])

    # Iterate over each combination (group) of primary_site and sample_type
    for (primary_site, sample_type), group in grouped:
        combined_df = pd.DataFrame()  # Create an empty DataFrame to hold combined data for the group

        # Loop through each file in the group
        for _, row in group.iterrows():
            file_id = row['file_id']  # Get the file_id for constructing the file path
            file_name = row['file_name']  # Get the file_name (ends with seg.v2.txt)
            file_path = os.path.join(directory, file_id, file_name)  # Build the full path to the file
            
            # Read the relevant columns (Chromosome, Start, End, Segment_Mean) from the file
            df = pd.read_csv(file_path, sep='\t', usecols=['Chromosome', 'Start', 'End', 'Segment_Mean'])
            
            # Keep the full file name (including '.seg.v2.txt') as the column name for Segment_Mean
            df = df.rename(columns={'Segment_Mean': file_name})
            
            # Merge the current file's data into the combined DataFrame for this group
            if combined_df.empty:
                combined_df = df  # If it's the first file, just assign it to the DataFrame
            else:
                combined_df = pd.merge(combined_df, df, on=['Chromosome', 'Start', 'End'], how='outer')  # Merge based on Chromosome, Start, End

        # Construct the output file name using the combination of primary_site and sample_type
        output_file = f"{primary_site}_{sample_type}.csv"
        output_file_path = os.path.join(directory, output_file)  # Save output file in the same directory

        # Save the combined DataFrame for this group to a CSV file
        combined_df.to_csv(output_file_path, index=False)
        print(f"Saved {output_file_path}")  # Print confirmation of saved file
    
    # End timing the process and calculate the total execution time
    end_time = time.time()
    total_time = end_time - start_time
    
    # Print the total time taken for the entire process
    print(f"Total execution time: {total_time:.2f} seconds")

# Main block to handle command-line arguments and invoke the main function
if __name__ == "__main__":
    # Use argparse to get directory and metadata_csv from the command line
    parser = argparse.ArgumentParser(description='Combine seg.v2.txt files into summary DataFrames based on primary_site and sample_type.')
    parser.add_argument('directory', type=str, help='Directory containing the files')  # Directory with seg.v2.txt files
    parser.add_argument('metadata_csv', type=str, help='Path to the metadata CSV file')  # Path to the metadata CSV file

    # Parse the arguments from the command line
    args = parser.parse_args()

    # Call the main function with the provided directory and metadata_csv
    combine_seg_files_by_category(args.directory, args.metadata_csv)
