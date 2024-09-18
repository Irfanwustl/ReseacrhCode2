import requests
import json
import pandas as pd
import subprocess
import os
import argparse

# Set the gdc-client path at the top of the script
GDC_CLIENT_PATH = '/logo2/irfan/Codes/GenomicTranslation/gdc-client'

def get_all_tcga_projects():
    """Query the GDC API to fetch TCGA projects for specified cancer sites."""
    endpoint = "https://api.gdc.cancer.gov/projects"
    params = {
        "filters": json.dumps({
            "op": "in",
            "content": {
                "field": "program.name",
                "value": ["TCGA"]
            }
        }),
        "fields": "project_id,primary_site",
        "format": "json",
        "size": 1000
    }
    response = requests.get(endpoint, params=params)
    response_data = response.json()
    projects = {hit['project_id']: hit['primary_site'] for hit in response_data['data']['hits']}

    # Filter the projects dictionary to include only specific ones
    desired_projects = {
        "TCGA-KIRC": "Kidney",    # Kidney Renal Clear Cell Carcinoma
        "TCGA-PRAD": "Prostate gland",    # Prostate Cancer
        "TCGA-BLCA": "Bladder",    # Bladder Cancer
        "TCGA-KIRP": "Kidney",    # Kidney Renal Papillary Cell Carcinoma
        "TCGA-KICH": "Kidney"     # Kidney Chromophobe
    }

    # Return only the desired projects
    filtered_projects = {proj: site for proj, site in projects.items() if proj in desired_projects}
    
    print("Filtered projects and their primary sites:")
    for proj_id, site in filtered_projects.items():
        print(f"{proj_id}: {site}")

    return filtered_projects


def get_files_with_case_ids(project, data_type, fields, size):
    """Query the GDC API to fetch file metadata with case IDs for a given project and data type."""
    endpoint = "https://api.gdc.cancer.gov/files"
    files = []
    page = 1
    
    while len(files) < size:
        params = {
            "filters": json.dumps({
                "op": "and",
                "content": [
                    {"op": "in", "content": {"field": "cases.project.project_id", "value": [project]}},
                    {"op": "in", "content": {"field": "files.data_category", "value": [data_type]}}
                ]
            }),
            "fields": ",".join(fields),
            "format": "json",
            "size": min(size - len(files), 500),  # Request only as many as needed, max 500
            "from": (page - 1) * 500 + 1
        }
        response = requests.get(endpoint, params=params)
        response_data = response.json()
        files.extend(response_data['data']['hits'])
        
        # Break if we have reached the last page
        if response_data['data']['pagination']['page'] == response_data['data']['pagination']['pages']:
            break
        
        page += 1
    
    return files


def process_metadata(all_metadata):
    """Process the fetched metadata to flatten nested structures."""
    df = pd.DataFrame(all_metadata)
    if 'cases' in df.columns:
        df['case_id'] = df['cases'].apply(lambda x: x[0]['case_id'] if x else None)
        df['sample_type'] = df['cases'].apply(lambda x: x[0]['samples'][0]['sample_type'] if x and x[0]['samples'] else None)
        df['disease_type'] = df['cases'].apply(lambda x: x[0]['disease_type'] if x else None)
        df['primary_site'] = df['cases'].apply(lambda x: x[0]['primary_site'] if x else None)
        df.drop(columns=['cases'], inplace=True)
    return df

def create_manifest(file_ids, download_dir):
    """Creates a manifest file for the gdc-client."""
    manifest_path = os.path.join(download_dir, 'gdc_manifest.txt')
    with open(manifest_path, 'w') as file:  # Corrected line
        file.write("id\n")
        for file_id in file_ids:
            file.write(f"{file_id}\n")
    return manifest_path

def download_files(manifest_path, download_dir):
    """Uses gdc-client to download files specified in the manifest."""
    subprocess.run([GDC_CLIENT_PATH, 'download', '-m', manifest_path, '-d', download_dir], check=True)
    print("Download completed.")

def main(master_directory, size):
    if not os.path.exists(master_directory):
        os.makedirs(master_directory)

    projects = get_all_tcga_projects()
    
    data_type = "Copy Number Variation"
    fields = ["file_id", "file_name", "cases.case_id", "cases.samples.sample_type", "cases.disease_type", "cases.primary_site", "platform"]

    all_metadata = []

    for project_id in projects:
        files_data = get_files_with_case_ids(project_id, data_type, fields, size=size)
        for file_data in files_data:
            file_data['project_id'] = project_id  # Add project ID to each file's metadata
        all_metadata.extend(files_data)

    if not all_metadata:
        print("No CNV data available for the specified projects and filters.")
        return

    cnv_df = process_metadata(all_metadata)
    
    # Saving metadata to CSV
    csv_path = os.path.join(master_directory, "cnv_metadata.csv")
    cnv_df.to_csv(csv_path, index=False)
    print(f"Metadata for CNV saved to {csv_path}")

    # Create manifest and download files
    file_ids = cnv_df['file_id'].tolist()
    manifest_path = create_manifest(file_ids, master_directory)
    download_files(manifest_path, master_directory)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download specific TCGA data.")
    parser.add_argument("master_directory", help="Directory to save downloaded files and metadata")
    parser.add_argument("--size", type=int, default=100, help="Number of files to download per type (default is 100)")
    args = parser.parse_args()
    
    # Pass the size argument to main
    main(args.master_directory, args.size)
