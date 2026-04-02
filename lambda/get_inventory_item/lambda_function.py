import boto3
import json

def lambda_handler(event, context):
    # DynamoDB setup
    dynamo_client = boto3.client('dynamodb')
    table_name = 'Inventory'
    
    # Get the key from the path parameters
    if 'pathParameters' not in event or 'id' not in event['pathParameters']:
        return {
            'statusCode': 400,
            'body': json.dumps("Missing 'id' path parameter")
        }
    
    key_value = event['pathParameters']['id']
    
    # Note: We need both PK and SK to get an item
    # This function assumes we need to scan or use GSI
    # Alternative: Scan to find the item
    try:
        # Scan to find item with matching item_id
        response = dynamo_client.scan(
            TableName=table_name,
            FilterExpression='item_id = :id',
            ExpressionAttributeValues={
                ':id': {'S': key_value}
            }
        )
        
        items = response.get('Items', [])
        
        if not items:
            return {
                'statusCode': 404,
                'body': json.dumps('Item not found')
            }
        
        # Convert DynamoDB format to JSON
        item = items[0]
        converted = {}
        for key, value in item.items():
            if 'S' in value:
                converted[key] = value['S']
            elif 'N' in value:
                if '.' in value['N']:
                    converted[key] = float(value['N'])
                else:
                    converted[key] = int(value['N'])
        
        return {
            'statusCode': 200,
            'body': json.dumps(converted)
        }
    except Exception as e:
        print(e)
        return {
            'statusCode': 500,
            'body': json.dumps(str(e))
        }