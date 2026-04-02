import boto3
import json
from boto3.dynamodb.conditions import Key
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
    # DynamoDB setup using resource (for query with GSI)
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Inventory')
    GSI_NAME = 'LocationInventoryIndex'
    
    # Get the location_id from path parameters
    if 'pathParameters' not in event or 'id' not in event['pathParameters']:
        return {
            'statusCode': 400,
            'body': json.dumps("Missing 'id' path parameter")
        }
    
    location_id = int(event['pathParameters']['id'])
    
    try:
        # Query using GSI to get all items at a location
        response = table.query(
            IndexName=GSI_NAME,
            KeyConditionExpression=Key('location_id').eq(location_id)
        )
        
        items = response.get('Items', [])
        
        # Convert Decimal values to JSON serializable types
        items = convert_decimals(items)
        
        return {
            'statusCode': 200,
            'body': json.dumps(items)
        }
    except Exception as e:
        print(e)
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error querying items: {str(e)}")
        }