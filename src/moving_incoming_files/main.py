"""Runs as Incoming Data to S3 Transform Location Lambda.

Raises-
    error: lambda exception
Returns-
    [dict]:

"""
import os
from datetime import datetime
import logging
import boto3

logging.getLogger().setLevel(logging.INFO)

bucket_name = os.environ['bucket_name']
source_key = os.environ['processing_folder']
dest_key = os.environ['dataset_folder']

@staticmethod
def incoming_data_mover(filedate):

    s3_client = boto3.client("s3")
    s3_resource = boto3.resource("s3")
    bucket = s3_resource.Bucket(bucket_name)
    event_date = datetime.strptime(filedate, "%Y-%m-%d")
    day, month, yyyy = str(event_date.day).zfill(2), str(event_date.month).zfill(2), str(event_date.year)
    print(f"""{yyyy}-{month}-{day}""")
    final_source_key = f"{source_key}/yyyy={yyyy}/mm={month}/dd={day}"
    for bucket_object in bucket.objects.filter(Prefix=final_source_key):
        path, file = os.path.split(bucket_object.key)
        copy_source_object = {
            'Bucket': bucket_name, 'Key': f"""{path}/{file}"""
        }
        if file != "":
            s3_client.copy_object(CopySource=copy_source_object, Bucket=bucket_name,
                                  Key=f"""{dest_key}/yyyy={yyyy}/mm={month}/dd={day}/{file}""") 
            s3_client.delete_object(Bucket=bucket_name, Key=f"""{path}/{file}""")
    return "success"


def lambda_handler(event: dict, _context: dict) -> dict:
    """Main lambda handler for Incoming Data to S3 Transform Location Lambda."""

    # In case a correct event is encountered -------------------------------------------
    if event:
        # Create template and extract values from event --------------------------------
        logging.info("This is the event we received: %s", event)
        try:
            filedate = event['asof_date']
            incoming_data_mover(filedate)
            return {
                'asof_date': filedate
            }
        # In case an error is encountered even when a correct event is present ---------
        except Exception as error:
            logging.error("An error occurred: %s", error)
            raise error
    # In case no event is present ------------------------------------------------------
    else:
        logging.error("We couldn't find a suitable event. Exiting....")
        raise OSError("No event found")