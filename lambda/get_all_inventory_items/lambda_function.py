import boto3
import json
from decimal import Decimal

# Function to convert Decimal to int/float
def convert_decimals(obj):
    if isinstance(obj, list):
        return [convert_decimals(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):  
        return int(obj) if obj % 1 == 0 else float(obj)
    return obj

def lambda_handler(event, context):
    # Initialize a DynamoDB client
    dynamo_client = boto3.client('dynamodb')
    
    # Name of the DynamoDB table
    table_name = 'Inventory'
    
    # Scan the table
    try:
        response = dynamo_client.scan(TableName=table_name)
        items = response['Items']
        
        # Convert DynamoDB format to JSON
        converted_items = []
        for item in items:
            converted = {}
            for key, value in item.items():
                if 'S' in value:
                    converted[key] = value['S']
                elif 'N' in value:
                    if '.' in value['N']:
                        converted[key] = float(value['N'])
                    else:
                        converted[key] = int(value['N'])
            converted_items.append(converted)
        
        return {
            'statusCode': 200,
            'body': json.dumps(converted_items)
        }
    except Exception as e:
        print(e)
        return {
            'statusCode': 500,
            'body': json.dumps(str(e))
        }