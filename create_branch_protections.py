import json
import boto3

client = boto3.client('ssm')

def lambda_handler(event, context):
    parameter = client.get_parameter(Name='gh_pat', WithDecryption=True)
    print(parameter)
    return parameter ['Parameter']['Value']