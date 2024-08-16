#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import os
from tqdm import tqdm
import sys

data_folder_path = sys.argv[1] #'/logo2/irfan/TCGA/TCGA_from_LTMEwork/TCGA_convertedto_MONOD2/TCGA_ready_monod2_intersectedSortedMerged_std_filtered_cpg5_std0.1_head'

final_df = pd.DataFrame()

# Ensure the output path is correctly formed, especially if data_folder_path ends with a slash
if data_folder_path.endswith('/'):
    output_file_path = f"{data_folder_path[:-1]}_Allmatrix"
else:
    output_file_path = f"{data_folder_path}_Allmatrix"

for file_name in tqdm(os.listdir(data_folder_path), desc='Processing files'):
    if file_name.endswith('.bedgraph'):
        file_path = os.path.join(data_folder_path, file_name)
        try:
            df = pd.read_csv(file_path, sep='\t', header=None, names=['chrom', 'start', 'end', 'value'])
            df['feature'] = df['chrom'].astype(str) + ':' + df['start'].astype(str) + '-' + df['end'].astype(str)
            sample_name = file_name.rsplit('.', 1)[0]

            sample_df = pd.DataFrame(df['value'].values, index=df['feature'], columns=[sample_name])
            
            if final_df.empty:
                final_df = sample_df
            else:
                final_df = final_df.join(sample_df, how='outer')
                
        except Exception as e:
            print(f"Error processing {file_name}: {e}")

final_df.to_csv(output_file_path, sep='\t', na_rep='NA')


# In[ ]:


final_df.shape


# In[ ]:




# Define the substrings to look for in column names
substrings = ['_Tumor', 'Metastatic', '_Normal','_Cancer']

# List to keep track of columns that do not contain any of the specified substrings
columns_without_substrings = []

# Function to truncate column names and check for substrings
def truncate_column_name(name):
    for substring in substrings:
        index = name.find(substring)
        if index != -1:
            return name[:index + len(substring)]
    # If the loop completes without returning, the substring wasn't found
    columns_without_substrings.append(name)
    return name

# Apply the function to each column name
final_df.columns = [truncate_column_name(col) for col in final_df.columns]

# Check if the list of columns without substrings is empty
if columns_without_substrings:
    print("The following columns do not contain any of the specified substrings:")
    print(len(columns_without_substrings))
else:
    print("All column names contain at least one of the specified substrings.")

# Display the updated column names (optional)
#print(final_df.shape)


# In[ ]:


columns_without_substrings


# In[ ]:


# Get the set of unique column names
unique_column_names = set(final_df.columns)



print(len(unique_column_names))
# Print the unique column names
#print(unique_column_names)


# In[ ]:


output_file_path = output_file_path+"_ML"


# In[ ]:


# Calculate the frequency of each unique column name
column_name_frequencies = final_df.columns.value_counts()

# Define the path for the output file
output_file_path = output_file_path+'_column_name_frequencies.txt'

# Save the frequencies to a tab-separated file
column_name_frequencies.to_csv(output_file_path, sep='\t', header=False)


# In[ ]:


#display(final_df.head())


# In[ ]:


#import pandas as pd

final_df.reset_index(inplace=True)

# Assuming final_df is already loaded and 'feature' is a column

# Split the 'feature' column into 'chrom', 'start', and 'end'
final_df[['chrom', 'positions']] = final_df['feature'].str.split(':', expand=True)
final_df[['start', 'end']] = final_df['positions'].str.split('-', expand=True)

# Convert 'start' to integer for sorting
final_df['start'] = final_df['start'].astype(int)
final_df['end'] = final_df['end'].astype(int)

# Sort by 'chrom' and 'start'
# Note: If chromosomes are not in the format 'chr1', 'chr2', ..., 'chrX', 'chrY', 'chrM', 
# this method may not sort chromosomes correctly and you'll need a custom sort.
final_df_sorted = final_df.sort_values(by=['chrom', 'start'])

#print(final_df_sorted.head())

# Drop the extra columns
final_df_sorted.drop(['chrom', 'start', 'end', 'positions'], axis=1, inplace=True)

# Now, if you previously reset the index to make 'feature' a column, you should set it back as the index
final_df_sorted.set_index('feature', inplace=True)

# Display to check
#display(final_df_sorted.head())


# In[ ]:



final_df_sorted.to_csv(output_file_path+"_sorted.txt", sep='\t', na_rep='NA')
print('done')

