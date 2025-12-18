# CloudWatch Metrics
import boto3

cloudwatch = boto3.client('cloudwatch', region_name='us-east-1')

cloudwatch.put_metric_data(
    Namespace='FraudDetection',
    MetricData=[
        {
            'MetricName': 'FraudulentTransactions',
            'Value': fraud_count,
            'Unit': 'Count'
        }
    ]
)