import boto3
from src.config.env_config import Configuration

AWS_REGION = Configuration.get("AWS_REGION")

print("Creating Bedrock clients with region:", AWS_REGION)

def createBedrockRuntime():
    return boto3.client("bedrock-runtime", region_name=AWS_REGION)

def createBedrockControl():
    return boto3.client("bedrock", region_name=AWS_REGION)
