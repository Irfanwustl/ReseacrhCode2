import requests
import json
import pandas as pd
import subprocess
import os
import argparse

def get_all_tcga_projects():
    """Query the GDC API to fetch all TCGA projects."""
    endpoint = "https://api.gdc.cancer.gov/projects"
    params = {
        "filters": json.dumps({
            "op": "in",
            "content": {
                "field": "program.name",
                "value": ["TCGA"]
            }
        }),
        "fields": "project_id",
        "format": "json",
        "size": 1000
    }
    response = requests.get(endpoint, params=params)
    response_data = response.json()
    projects = [hit['project_id'] for hit in response_data['data']['hits']]
    return projects

def get_files_with_case_ids(project, data_type, fields, size=500):
    """Query the GDC API to fetch file metadata with case IDs for a given project and data type."""
    endpoint = "https://api.gdc.cancer.gov/files"
    params = {
        "filters": json.dumps({
            "op": "and",
            "content": [
                {"op": "in", "content": {"field": "cases.project.project_id", "value": [project]}},
                {"op": "in", "content": {"field": "files.data_type", "value": [data_type]}}
            ]
        }),
        "fields": ",".join(fields),
        "format": "json",
        "size": size
    }
    response = requests.get(endpoint, params=params)
    response_data = response.json()
    # Print the first few entries to debug the response structure
   # print(f"Response for {data_type} in project {project}:")
   # print(json.dumps(response_data, indent=2)[:1000])  # Print a truncated part of the response
    return response_data

def create_manifest_file(uuids, filename="gdc_manifest.tsv"):
    """Create a manifest file for gdc-client download."""
    with open(filename, "w") as file:
        file.write("id\n")
        for uuid in uuids:
            file.write(f"{uuid}\n")

def download_files(uuids, data_directory, max_retries=5):
    """Use gdc-client to download files by UUID with retry logic."""
    create_manifest_file(uuids)
    gdc_client_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gdc-client")
    
    if not os.path.exists(data_directory):
        os.makedirs(data_directory)
    
    print(f"Downloading files using gdc-client into {data_directory}...")
    
    for attempt in range(max_retries):
        try:
            result = subprocess.run([gdc_client_path, "download", "-m", "gdc_manifest.tsv", "-d", data_directory], check=True)
            if result.returncode == 0:
                print("Download completed successfully.")
                break
        except subprocess.CalledProcessError as e:
            print(f"Download attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                print("Retrying in 5 seconds...")
                time.sleep(5)
            else:
                print("Maximum retry attempts reached. Download failed.")
                raise

def main(master_directory):
    data_directory = os.path.join(master_directory, "data")
    
    # Fetch all TCGA projects
    projects = get_all_tcga_projects()
    
    data_types = ["Gene Expression Quantification", "Methylation Beta Value"]
    fields = ["file_id", "file_name", "cases.case_id", "cases.disease_type", "cases.primary_site", "platform", "cases.samples.sample_type"]

    rna_metadata = []
    methylation_metadata = []

    # Fetch metadata for RNA-Seq and Methylation files for all projects
    for project in projects:
        rna_files = get_files_with_case_ids(project, data_types[0], fields)
        methylation_files = get_files_with_case_ids(project, data_types[1], fields)

        rna_metadata += rna_files['data']['hits']
        methylation_metadata += methylation_files['data']['hits']

    # Create DataFrames for easier handling
    rna_df = pd.DataFrame(rna_metadata)
    methylation_df = pd.DataFrame(methylation_metadata)

    # Print the first few rows to understand the structure
    print("RNA-Seq DataFrame Structure:")
    print(rna_df.head())
    print("\nMethylation DataFrame Structure:")
    print(methylation_df.head())

    # Extract 'cases.case_id' and other case-related information from nested dictionary if it exists
    if 'cases' in rna_df.columns:
        rna_df['case_id'] = rna_df['cases'].apply(lambda x: x[0]['case_id'] if len(x) > 0 else None)
        rna_df['disease_type'] = rna_df['cases'].apply(lambda x: x[0]['disease_type'] if len(x) > 0 else None)
        rna_df['primary_site'] = rna_df['cases'].apply(lambda x: x[0]['primary_site'] if len(x) > 0 else None)
        rna_df['sample_type'] = rna_df['cases'].apply(lambda x: x[0]['samples'][0]['sample_type'] if len(x[0]['samples']) > 0 else None)
        rna_df.drop(columns=['cases'], inplace=True)
    if 'cases' in methylation_df.columns:
        methylation_df['case_id'] = methylation_df['cases'].apply(lambda x: x[0]['case_id'] if len(x) > 0 else None)
        methylation_df['disease_type'] = methylation_df['cases'].apply(lambda x: x[0]['disease_type'] if len(x) > 0 else None)
        methylation_df['primary_site'] = methylation_df['cases'].apply(lambda x: x[0]['primary_site'] if len(x) > 0 else None)
        methylation_df['sample_type'] = methylation_df['cases'].apply(lambda x: x[0]['samples'][0]['sample_type'] if len(x[0]['samples']) > 0 else None)
        methylation_df.drop(columns=['cases'], inplace=True)

    # Rename columns for clarity
    rna_df.rename(columns={'file_id': 'rna_file_id', 'file_name': 'rna_file_name', 'platform': 'rna_platform'}, inplace=True)
    methylation_df.rename(columns={'file_id': 'meth_file_id', 'file_name': 'meth_file_name', 'platform': 'meth_platform'}, inplace=True)

    # Merge DataFrames on case_id to find pairs
    if 'case_id' in rna_df.columns and 'case_id' in methylation_df.columns:
        paired_df = pd.merge(rna_df, methylation_df, on="case_id", suffixes=('_rna', '_meth'))
    else:
        paired_df = pd.DataFrame()  # Empty DataFrame if case_id is not present

    # Save the manifest for download if pairs are found
    if not paired_df.empty:
        rna_uuids = paired_df['rna_file_id'].tolist()
        methylation_uuids = paired_df['meth_file_id'].tolist()
        download_files(rna_uuids + methylation_uuids, data_directory)  # Combine both UUID lists for a single manifest
        paired_df.to_csv(os.path.join(master_directory, "paired_files_manifest.csv"), index=False)
        print(f"Paired RNA-seq and Methylation files manifest saved to {os.path.join(master_directory, 'paired_files_manifest.csv')}")
    else:
        print("No paired data found.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download TCGA paired RNA-seq and Methylation data.")
    parser.add_argument("master_directory", help="Directory to save downloaded files and manifest")
    args = parser.parse_args()
    main(args.master_directory)
