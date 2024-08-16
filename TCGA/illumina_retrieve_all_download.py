import requests
import json
from io import StringIO
import pandas as pd
import numpy as np
import re
import os
from pandas.errors import EmptyDataError 
import sys
import time

fol = sys.argv[1]

start = time.time()

try:
    os.mkdir(fol)
except FileExistsError:
    pass

def save_files(): 
    # Fields we want in the dataframe
    fields = [
        "file_name",
        "cases.submitter_id",
        "cases.samples.sample_type",
        "cases.disease_type",
        "cases.project.project_id",
        "cases.primary_site"
        ]

    fields = ",".join(fields)

    files_endpt = "https://api.gdc.cancer.gov/files"

    # Filters for the API
    filters = {
        "op": "and",
        "content":[
            {
            "op": "in",
            "content":{
                "field": "files.data_format",
                "value": ["TXT"]
                }
            },
            {
            "op": "in",
            "content":{
                "field": "files.data_category",
                "value": ["DNA Methylation"]
                }
            },
            {
            "op": "in",
            "content":{
                "field": "files.platform",
                "value": ["Illumina Human Methylation 450"]
                }
            },
        ]
    }

    # A POST is used, so the filter parameters can be passed directly as a Dict object.
    params = {
        "filters": filters,
        "fields": fields,
        "format": "TSV",
        "size": "20000"
        }

    # The parameters are passed to 'json' rather than 'params' in this case
    response = requests.post(files_endpt, headers = {"Content-Type": "application/json"}, json = params)
    resp = response.content.decode("utf-8")
    try:
        df_sub = pd.read_csv(StringIO(resp), sep='\t')
        for i, ID in enumerate(np.array(df_sub['id'])):
            file_id = ID
            project_id = np.array(df_sub['cases.0.project.project_id'])[i]
            tissue = np.array(df_sub['cases.0.samples.0.sample_type'])[i]
            organ = np.array(df_sub['cases.0.primary_site'])[i]

            data_endpt = "https://api.gdc.cancer.gov/data/{}".format(file_id)

            response = requests.get(data_endpt, headers = {"Content-Type": "application/json"})

            # The file name can be found in the header within the Content-Disposition key.
            response_head_cd = response.headers["Content-Disposition"]

            file_name = re.findall("filename=(.+)", response_head_cd)[0]

            tissue_name = '_'.join(tissue.split(' '))
            organ_name = '_'.join(organ.split(' '))
            full_name = fol + '/' + organ_name + '_' + project_id + '_' + tissue_name + '_' + file_name
            with open(full_name, "wb") as output_file:
                output_file.write(response.content)
        return df_sub
    except EmptyDataError:
        print('No tissue')
        return 0

res = save_files()

end = time.time()
print ("Time elapsed:", end - start)
