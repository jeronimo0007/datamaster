# Python - AWS Kinesis
import boto3

kinesis = boto3.client('kinesis', region_name='us-east-1')
response = kinesis.put_record(
    StreamName='fraud-transactions',
    Data=json.dumps(transaction),
    PartitionKey=transaction['user_id']
)