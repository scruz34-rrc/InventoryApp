import boto3
import json

def lambda_handler(event, context):
    # Initialize DynamoDB client
    dynamo_client = boto3.client('dynamodb')
    table_name = 'Inventory'
    
    # Extract the 'id' from the path parameters
    if 'pathParameters' not in event or 'id' not in event['pathParameters']:
        return {
            'statusCode': 400,
            'body': json.dumps("Missing 'id' path parameter")
        }
    
    key_value = event['pathParameters']['id']
    
    # Need to find the item first to get both PK and SK
    try:
        # Scan to find item with matching item_id
        scan_response = dynamo_client.scan(
            TableName=table_name,
            FilterExpression='item_id = :id',
            ExpressionAttributeValues={
                ':id': {'S': key_value}
            }
        )
        
        items = scan_response.get('Items', [])
        
        if not items:
            return {
                'statusCode': 404,
                'body': json.dumps('Item not found')
            }
        
        # Get the full key from the found item
        item = items[0]
        key = {
            'item_id': item['item_id'],
            'location_id': item['location_id']
        }
        
        # Delete the item
        dynamo_client.delete_item(TableName=table_name, Key=key)
        
        return {
            'statusCode': 200,
            'body': json.dumps(f"Item with ID {key_value} deleted successfully.")
        }
    except Exception as e:
        print(e)
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error deleting item: {str(e)}")
        }