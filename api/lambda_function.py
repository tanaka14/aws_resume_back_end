import boto3
import json
from decimal import Decimal

# Custom encoder for JSON serialization
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            # Convert Decimal to float or int
            return int(obj) if obj % 1 == 0 else float(obj)
        return super(DecimalEncoder, self).default(obj)

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('VisitorCounter')

def lambda_handler(event, context):
    try:
        # Update the visitor count atomically
        response = table.update_item(
            Key={'id': 'counter'},
            UpdateExpression="SET #c = if_not_exists(#c, :start) + :inc",
            ExpressionAttributeNames={'#c': 'count'},
            ExpressionAttributeValues={
                ':inc': 1,
                ':start': 0
            },
            ReturnValues="UPDATED_NEW"
        )

        # Get the updated count
        new_count = response['Attributes']['count']
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'visitor_count': new_count}, cls=DecimalEncoder)
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
