from google.cloud import bigquery
import os
import pandas as pd

def runme():

    dataset_id = 'IanTest'
    table_id = 'ia'
    
    path1 = os.path.dirname(os.path.realpath(__file__))
    parentPath = os.path.dirname(path1)
    #type = sys.argv[1]
    #file = os.path.join(parentPath,"store",type + ".pkl")
    filename = os.path.join(parentPath,"store","adviser.csv")
    creds = os.path.join(parentPath,"creds","backlogger_bq.json")
    client = bigquery.Client.from_service_account_json(creds)

    dataset_ref = client.dataset(dataset_id)
    table_ref = dataset_ref.table(table_id)
    job_config = bigquery.LoadJobConfig()
    job_config.source_format = bigquery.SourceFormat.CSV
    job_config.skip_leading_rows = 1
    job_config.autodetect = True
    job_config.WriteDisposition = "WRITE_TRUNCATE"
    job_config.CreateDisposition = "CREATE_IF_NEEDED"

    with open(filename, "rb") as source_file:
        job = client.load_table_from_file(
            source_file,
            table_ref,
            #location="EU",  # Must match the destination dataset location.
            job_config=job_config
        )  # API request


    try:
        job.result()  # Waits for table load to complete.

    except:
        for er in job.errors:
            print(er)





    print("Loaded {} rows into {}:{}.".format(job.output_rows, dataset_id, table_id))



if __name__ == '__main__':
    runme()