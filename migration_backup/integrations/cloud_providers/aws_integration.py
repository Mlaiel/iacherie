"""AWS Integration - Amazon Web Services Cloud Integration
========================================================

Comprehensive AWS integration for cloud services including S3, CloudFront,
Lambda, SES, SNS, and other AWS services for the Ainflue platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import time
import boto3
import aioboto3
from typing import Dict, List, Optional, Any, Union, BinaryIO
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from decimal import Decimal
import hashlib
import base64
from urllib.parse import urlparse
import mimetypes

import aiofiles

logger = logging.getLogger(__name__)


class AWSRegion(Enum):
    """AWS regions."""
    US_EAST_1 = "us-east-1"
    US_EAST_2 = "us-east-2"
    US_WEST_1 = "us-west-1"
    US_WEST_2 = "us-west-2"
    EU_WEST_1 = "eu-west-1"
    EU_WEST_2 = "eu-west-2"
    EU_CENTRAL_1 = "eu-central-1"
    AP_SOUTHEAST_1 = "ap-southeast-1"
    AP_SOUTHEAST_2 = "ap-southeast-2"
    AP_NORTHEAST_1 = "ap-northeast-1"


class S3StorageClass(Enum):
    """S3 storage classes."""
    STANDARD = "STANDARD"
    REDUCED_REDUNDANCY = "REDUCED_REDUNDANCY"
    STANDARD_IA = "STANDARD_IA"
    ONEZONE_IA = "ONEZONE_IA"
    INTELLIGENT_TIERING = "INTELLIGENT_TIERING"
    GLACIER = "GLACIER"
    DEEP_ARCHIVE = "DEEP_ARCHIVE"
    GLACIER_IR = "GLACIER_IR"


class LambdaRuntime(Enum):
    """Lambda function runtimes."""
    PYTHON_3_9 = "python3.9"
    PYTHON_3_10 = "python3.10"
    PYTHON_3_11 = "python3.11"
    NODEJS_18 = "nodejs18.x"
    NODEJS_20 = "nodejs20.x"
    JAVA_17 = "java17"
    DOTNET_6 = "dotnet6"
    GO_1X = "go1.x"


@dataclass
class AWSCredentials:
    """AWS credentials configuration."""
    access_key_id: str
    secret_access_key: str
    session_token: Optional[str] = None
    region: AWSRegion = AWSRegion.US_EAST_1


@dataclass
class S3Object:
    """S3 object metadata."""
    key: str
    bucket: str
    size: int
    last_modified: datetime
    etag: str
    storage_class: str
    content_type: Optional[str] = None
    metadata: Optional[Dict[str, str]] = None
    url: Optional[str] = None
    signed_url: Optional[str] = None


@dataclass
class CloudFrontDistribution:
    """CloudFront distribution information."""
    id: str
    domain_name: str
    status: str
    enabled: bool
    origin_domain: str
    default_cache_behavior: Dict[str, Any]
    aliases: List[str] = field(default_factory=list)
    comment: str = ""
    price_class: str = "PriceClass_All"


@dataclass
class LambdaFunction:
    """Lambda function metadata."""
    function_name: str
    function_arn: str
    runtime: str
    handler: str
    role: str
    code_size: int
    description: str
    timeout: int
    memory_size: int
    last_modified: datetime
    version: str = "$LATEST"
    environment: Optional[Dict[str, str]] = None


@dataclass
class SESTemplate:
    """SES email template."""
    template_name: str
    subject: str
    text_part: Optional[str] = None
    html_part: Optional[str] = None
    created_timestamp: Optional[datetime] = None


class AWSIntegration:
    """Main AWS integration for Ainflue platform."""
    
    def __init__(self, credentials: AWSCredentials):
        self.credentials = credentials
        self.region = credentials.region.value
        
        # Boto3 sessions
        self.session = None
        self.async_session = None
        
        # Service clients (will be initialized)
        self.s3_client = None
        self.cloudfront_client = None
        self.lambda_client = None
        self.ses_client = None
        self.sns_client = None
        self.cloudwatch_client = None
        
        # Configuration
        self.default_bucket = None
        self.cloudfront_distribution_id = None
        
        # Content delivery cache
        self.cdn_cache = {}
        self.cache_ttl = 3600  # 1 hour
    
    async def initialize(self) -> bool:
        """Initialize AWS integration."""
        try:
            # Create async session
            self.async_session = aioboto3.Session(
                aws_access_key_id=self.credentials.access_key_id,
                aws_secret_access_key=self.credentials.secret_access_key,
                aws_session_token=self.credentials.session_token,
                region_name=self.region
            )
            
            # Test connection by listing S3 buckets
            async with self.async_session.client('s3') as s3:
                response = await s3.list_buckets()
                buckets = response.get('Buckets', [])
                
                if buckets and not self.default_bucket:
                    self.default_bucket = buckets[0]['Name']
                
            logger.info(f"AWS integration initialized in region {self.region}")
            logger.info(f"Found {len(buckets)} S3 buckets")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize AWS integration: {str(e)}")
            return False
    
    async def upload_content(self, file_path: str, key: str, 
                           bucket: Optional[str] = None,
                           storage_class: S3StorageClass = S3StorageClass.STANDARD,
                           metadata: Optional[Dict[str, str]] = None,
                           content_type: Optional[str] = None) -> S3Object:
        """Upload content to S3."""
        try:
            bucket = bucket or self.default_bucket
            if not bucket:
                raise ValueError("No bucket specified and no default bucket available")
            
            # Determine content type
            if not content_type:
                content_type, _ = mimetypes.guess_type(file_path)
                content_type = content_type or 'application/octet-stream'
            
            async with self.async_session.client('s3') as s3:
                # Upload file
                extra_args = {
                    'StorageClass': storage_class.value,
                    'ContentType': content_type
                }
                
                if metadata:
                    extra_args['Metadata'] = metadata
                
                await s3.upload_file(file_path, bucket, key, ExtraArgs=extra_args)
                
                # Get object metadata
                response = await s3.head_object(Bucket=bucket, Key=key)
                
                s3_object = S3Object(
                    key=key,
                    bucket=bucket,
                    size=response['ContentLength'],
                    last_modified=response['LastModified'],
                    etag=response['ETag'].strip('"'),
                    storage_class=response.get('StorageClass', storage_class.value),
                    content_type=response.get('ContentType'),
                    metadata=response.get('Metadata', {}),
                    url=f"https://{bucket}.s3.{self.region}.amazonaws.com/{key}"
                )
                
                logger.info(f"Uploaded content to S3: {bucket}/{key}")
                return s3_object
                
        except Exception as e:
            logger.error(f"Failed to upload content: {str(e)}")
            raise
    
    async def upload_content_bytes(self, content: bytes, key: str,
                                 bucket: Optional[str] = None,
                                 storage_class: S3StorageClass = S3StorageClass.STANDARD,
                                 metadata: Optional[Dict[str, str]] = None,
                                 content_type: str = 'application/octet-stream') -> S3Object:
        """Upload content bytes to S3."""
        try:
            bucket = bucket or self.default_bucket
            if not bucket:
                raise ValueError("No bucket specified and no default bucket available")
            
            async with self.async_session.client('s3') as s3:
                # Upload content
                extra_args = {
                    'StorageClass': storage_class.value,
                    'ContentType': content_type
                }
                
                if metadata:
                    extra_args['Metadata'] = metadata
                
                await s3.put_object(
                    Bucket=bucket,
                    Key=key,
                    Body=content,
                    **extra_args
                )
                
                # Get object metadata
                response = await s3.head_object(Bucket=bucket, Key=key)
                
                s3_object = S3Object(
                    key=key,
                    bucket=bucket,
                    size=response['ContentLength'],
                    last_modified=response['LastModified'],
                    etag=response['ETag'].strip('"'),
                    storage_class=response.get('StorageClass', storage_class.value),
                    content_type=response.get('ContentType'),
                    metadata=response.get('Metadata', {}),
                    url=f"https://{bucket}.s3.{self.region}.amazonaws.com/{key}"
                )
                
                logger.info(f"Uploaded content bytes to S3: {bucket}/{key}")
                return s3_object
                
        except Exception as e:
            logger.error(f"Failed to upload content bytes: {str(e)}")
            raise
    
    async def get_content_url(self, key: str, bucket: Optional[str] = None,
                            expires_in: int = 3600) -> str:
        """Get signed URL for S3 object."""
        try:
            bucket = bucket or self.default_bucket
            if not bucket:
                raise ValueError("No bucket specified and no default bucket available")
            
            cache_key = f"{bucket}/{key}/{expires_in}"
            
            # Check cache
            if cache_key in self.cdn_cache:
                cached_url, cached_time = self.cdn_cache[cache_key]
                if time.time() - cached_time < expires_in - 300:  # Refresh 5 minutes before expiry
                    return cached_url
            
            async with self.async_session.client('s3') as s3:
                signed_url = await s3.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': bucket, 'Key': key},
                    ExpiresIn=expires_in
                )
                
                # Cache the URL
                self.cdn_cache[cache_key] = (signed_url, time.time())
                
                return signed_url
                
        except Exception as e:
            logger.error(f"Failed to get content URL: {str(e)}")
            raise
    
    async def delete_content(self, key: str, bucket: Optional[str] = None) -> bool:
        """Delete content from S3."""
        try:
            bucket = bucket or self.default_bucket
            if not bucket:
                raise ValueError("No bucket specified and no default bucket available")
            
            async with self.async_session.client('s3') as s3:
                await s3.delete_object(Bucket=bucket, Key=key)
                
                logger.info(f"Deleted content from S3: {bucket}/{key}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to delete content: {str(e)}")
            return False
    
    async def list_content(self, prefix: str = "", bucket: Optional[str] = None,
                          max_keys: int = 1000) -> List[S3Object]:
        """List content in S3 bucket."""
        try:
            bucket = bucket or self.default_bucket
            if not bucket:
                raise ValueError("No bucket specified and no default bucket available")
            
            async with self.async_session.client('s3') as s3:
                paginator = s3.get_paginator('list_objects_v2')
                
                objects = []
                async for page in paginator.paginate(
                    Bucket=bucket,
                    Prefix=prefix,
                    MaxKeys=max_keys
                ):
                    for obj in page.get('Contents', []):
                        s3_object = S3Object(
                            key=obj['Key'],
                            bucket=bucket,
                            size=obj['Size'],
                            last_modified=obj['LastModified'],
                            etag=obj['ETag'].strip('"'),
                            storage_class=obj.get('StorageClass', 'STANDARD'),
                            url=f"https://{bucket}.s3.{self.region}.amazonaws.com/{obj['Key']}"
                        )
                        objects.append(s3_object)
                
                return objects
                
        except Exception as e:
            logger.error(f"Failed to list content: {str(e)}")
            return []
    
    async def create_cloudfront_distribution(self, origin_domain: str,
                                           aliases: Optional[List[str]] = None,
                                           comment: str = "Ainflue CDN",
                                           price_class: str = "PriceClass_100") -> CloudFrontDistribution:
        """Create CloudFront distribution."""
        try:
            async with self.async_session.client('cloudfront') as cloudfront:
                distribution_config = {
                    'CallerReference': f"ainflue-{int(time.time())}",
                    'Comment': comment,
                    'DefaultCacheBehavior': {
                        'TargetOriginId': origin_domain,
                        'ViewerProtocolPolicy': 'redirect-to-https',
                        'TrustedSigners': {
                            'Enabled': False,
                            'Quantity': 0
                        },
                        'ForwardedValues': {
                            'QueryString': False,
                            'Cookies': {'Forward': 'none'}
                        },
                        'MinTTL': 0,
                        'DefaultTTL': 86400,
                        'MaxTTL': 31536000
                    },
                    'Origins': {
                        'Quantity': 1,
                        'Items': [
                            {
                                'Id': origin_domain,
                                'DomainName': origin_domain,
                                'CustomOriginConfig': {
                                    'HTTPPort': 80,
                                    'HTTPSPort': 443,
                                    'OriginProtocolPolicy': 'https-only'
                                }
                            }
                        ]
                    },
                    'Enabled': True,
                    'PriceClass': price_class
                }
                
                if aliases:
                    distribution_config['Aliases'] = {
                        'Quantity': len(aliases),
                        'Items': aliases
                    }
                
                response = await cloudfront.create_distribution(
                    DistributionConfig=distribution_config
                )
                
                distribution_data = response['Distribution']
                
                distribution = CloudFrontDistribution(
                    id=distribution_data['Id'],
                    domain_name=distribution_data['DomainName'],
                    status=distribution_data['Status'],
                    enabled=distribution_data['DistributionConfig']['Enabled'],
                    origin_domain=origin_domain,
                    default_cache_behavior=distribution_data['DistributionConfig']['DefaultCacheBehavior'],
                    aliases=aliases or [],
                    comment=comment,
                    price_class=price_class
                )
                
                logger.info(f"Created CloudFront distribution: {distribution.id}")
                return distribution
                
        except Exception as e:
            logger.error(f"Failed to create CloudFront distribution: {str(e)}")
            raise
    
    async def invalidate_cloudfront_cache(self, paths: List[str],
                                        distribution_id: Optional[str] = None) -> str:
        """Invalidate CloudFront cache."""
        try:
            distribution_id = distribution_id or self.cloudfront_distribution_id
            if not distribution_id:
                raise ValueError("No distribution ID specified")
            
            async with self.async_session.client('cloudfront') as cloudfront:
                response = await cloudfront.create_invalidation(
                    DistributionId=distribution_id,
                    InvalidationBatch={
                        'Paths': {
                            'Quantity': len(paths),
                            'Items': paths
                        },
                        'CallerReference': f"ainflue-invalidation-{int(time.time())}"
                    }
                )
                
                invalidation_id = response['Invalidation']['Id']
                logger.info(f"Created CloudFront invalidation: {invalidation_id}")
                
                return invalidation_id
                
        except Exception as e:
            logger.error(f"Failed to invalidate CloudFront cache: {str(e)}")
            raise
    
    async def deploy_lambda_function(self, function_name: str, zip_file: bytes,
                                   handler: str, runtime: LambdaRuntime,
                                   role_arn: str, description: str = "",
                                   timeout: int = 30, memory_size: int = 128,
                                   environment: Optional[Dict[str, str]] = None) -> LambdaFunction:
        """Deploy Lambda function."""
        try:
            async with self.async_session.client('lambda') as lambda_client:
                function_config = {
                    'FunctionName': function_name,
                    'Runtime': runtime.value,
                    'Role': role_arn,
                    'Handler': handler,
                    'Code': {'ZipFile': zip_file},
                    'Description': description,
                    'Timeout': timeout,
                    'MemorySize': memory_size,
                    'Publish': True
                }
                
                if environment:
                    function_config['Environment'] = {'Variables': environment}
                
                try:
                    # Try to update existing function
                    await lambda_client.update_function_code(
                        FunctionName=function_name,
                        ZipFile=zip_file
                    )
                    
                    response = await lambda_client.update_function_configuration(
                        FunctionName=function_name,
                        Runtime=runtime.value,
                        Role=role_arn,
                        Handler=handler,
                        Description=description,
                        Timeout=timeout,
                        MemorySize=memory_size,
                        Environment={'Variables': environment} if environment else {}
                    )
                    
                except lambda_client.exceptions.ResourceNotFoundException:
                    # Create new function
                    response = await lambda_client.create_function(**function_config)
                
                lambda_function = LambdaFunction(
                    function_name=response['FunctionName'],
                    function_arn=response['FunctionArn'],
                    runtime=response['Runtime'],
                    handler=response['Handler'],
                    role=response['Role'],
                    code_size=response['CodeSize'],
                    description=response['Description'],
                    timeout=response['Timeout'],
                    memory_size=response['MemorySize'],
                    last_modified=datetime.fromisoformat(response['LastModified'].replace('Z', '+00:00')),
                    version=response['Version'],
                    environment=response.get('Environment', {}).get('Variables', {})
                )
                
                logger.info(f"Deployed Lambda function: {function_name}")
                return lambda_function
                
        except Exception as e:
            logger.error(f"Failed to deploy Lambda function: {str(e)}")
            raise
    
    async def invoke_lambda_function(self, function_name: str, payload: Dict[str, Any],
                                   invocation_type: str = "RequestResponse") -> Dict[str, Any]:
        """Invoke Lambda function."""
        try:
            async with self.async_session.client('lambda') as lambda_client:
                response = await lambda_client.invoke(
                    FunctionName=function_name,
                    InvocationType=invocation_type,
                    Payload=json.dumps(payload)
                )
                
                result = {
                    'status_code': response['StatusCode'],
                    'execution_result': response.get('ExecutedVersion'),
                    'log_result': response.get('LogResult')
                }
                
                if 'Payload' in response:
                    payload_data = await response['Payload'].read()
                    result['payload'] = json.loads(payload_data.decode())
                
                return result
                
        except Exception as e:
            logger.error(f"Failed to invoke Lambda function: {str(e)}")
            raise
    
    async def send_email(self, to_addresses: List[str], subject: str,
                        body_text: Optional[str] = None, body_html: Optional[str] = None,
                        from_address: Optional[str] = None,
                        reply_to_addresses: Optional[List[str]] = None) -> str:
        """Send email via SES."""
        try:
            async with self.async_session.client('ses') as ses:
                message = {
                    'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                    'Body': {}
                }
                
                if body_text:
                    message['Body']['Text'] = {'Data': body_text, 'Charset': 'UTF-8'}
                
                if body_html:
                    message['Body']['Html'] = {'Data': body_html, 'Charset': 'UTF-8'}
                
                destination = {'ToAddresses': to_addresses}
                
                if reply_to_addresses:
                    destination['ReplyToAddresses'] = reply_to_addresses
                
                response = await ses.send_email(
                    Source=from_address or f"noreply@ainflue.com",
                    Destination=destination,
                    Message=message
                )
                
                message_id = response['MessageId']
                logger.info(f"Sent email via SES: {message_id}")
                
                return message_id
                
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            raise
    
    async def create_email_template(self, template_name: str, subject: str,
                                  text_part: Optional[str] = None,
                                  html_part: Optional[str] = None) -> SESTemplate:
        """Create SES email template."""
        try:
            async with self.async_session.client('ses') as ses:
                template_data = {
                    'TemplateName': template_name,
                    'Subject': subject
                }
                
                if text_part:
                    template_data['TextPart'] = text_part
                
                if html_part:
                    template_data['HtmlPart'] = html_part
                
                await ses.create_template(Template=template_data)
                
                template = SESTemplate(
                    template_name=template_name,
                    subject=subject,
                    text_part=text_part,
                    html_part=html_part,
                    created_timestamp=datetime.utcnow()
                )
                
                logger.info(f"Created SES email template: {template_name}")
                return template
                
        except Exception as e:
            logger.error(f"Failed to create email template: {str(e)}")
            raise
    
    async def send_templated_email(self, to_addresses: List[str], template_name: str,
                                 template_data: Dict[str, str],
                                 from_address: Optional[str] = None) -> str:
        """Send templated email via SES."""
        try:
            async with self.async_session.client('ses') as ses:
                response = await ses.send_templated_email(
                    Source=from_address or f"noreply@ainflue.com",
                    Destination={'ToAddresses': to_addresses},
                    Template=template_name,
                    TemplateData=json.dumps(template_data)
                )
                
                message_id = response['MessageId']
                logger.info(f"Sent templated email via SES: {message_id}")
                
                return message_id
                
        except Exception as e:
            logger.error(f"Failed to send templated email: {str(e)}")
            raise
    
    async def publish_sns_notification(self, topic_arn: str, message: str,
                                     subject: Optional[str] = None,
                                     message_attributes: Optional[Dict[str, Any]] = None) -> str:
        """Publish notification to SNS topic."""
        try:
            async with self.async_session.client('sns') as sns:
                publish_args = {
                    'TopicArn': topic_arn,
                    'Message': message
                }
                
                if subject:
                    publish_args['Subject'] = subject
                
                if message_attributes:
                    publish_args['MessageAttributes'] = message_attributes
                
                response = await sns.publish(**publish_args)
                
                message_id = response['MessageId']
                logger.info(f"Published SNS notification: {message_id}")
                
                return message_id
                
        except Exception as e:
            logger.error(f"Failed to publish SNS notification: {str(e)}")
            raise
    
    async def put_cloudwatch_metric(self, namespace: str, metric_name: str,
                                  value: float, unit: str = "Count",
                                  dimensions: Optional[Dict[str, str]] = None) -> bool:
        """Put custom metric to CloudWatch."""
        try:
            async with self.async_session.client('cloudwatch') as cloudwatch:
                metric_data = {
                    'MetricName': metric_name,
                    'Value': value,
                    'Unit': unit,
                    'Timestamp': datetime.utcnow()
                }
                
                if dimensions:
                    metric_data['Dimensions'] = [
                        {'Name': k, 'Value': v} for k, v in dimensions.items()
                    ]
                
                await cloudwatch.put_metric_data(
                    Namespace=namespace,
                    MetricData=[metric_data]
                )
                
                logger.info(f"Put CloudWatch metric: {namespace}/{metric_name}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to put CloudWatch metric: {str(e)}")
            return False
    
    async def get_cloudwatch_metrics(self, namespace: str, metric_name: str,
                                   start_time: datetime, end_time: datetime,
                                   period: int = 300,
                                   statistics: List[str] = None) -> List[Dict[str, Any]]:
        """Get CloudWatch metrics."""
        try:
            statistics = statistics or ['Average']
            
            async with self.async_session.client('cloudwatch') as cloudwatch:
                response = await cloudwatch.get_metric_statistics(
                    Namespace=namespace,
                    MetricName=metric_name,
                    StartTime=start_time,
                    EndTime=end_time,
                    Period=period,
                    Statistics=statistics
                )
                
                return response.get('Datapoints', [])
                
        except Exception as e:
            logger.error(f"Failed to get CloudWatch metrics: {str(e)}")
            return []
    
    async def cleanup(self):
        """Cleanup AWS resources."""
        try:
            # Clear caches
            self.cdn_cache.clear()
            
            logger.info("AWS integration cleaned up successfully")
            
        except Exception as e:
            logger.error(f"Failed to cleanup AWS integration: {str(e)}")


# Example usage
async def main():
    """Example usage of AWS integration."""
    credentials = AWSCredentials(
        access_key_id="your-access-key-id",
        secret_access_key="your-secret-access-key",
        region=AWSRegion.US_EAST_1
    )
    
    aws = AWSIntegration(credentials)
    
    # Initialize
    if await aws.initialize():
        print("✅ AWS integration initialized")
        
        # Upload content
        content = b"Hello, Ainflue AWS Integration!"
        s3_object = await aws.upload_content_bytes(
            content=content,
            key="test/hello.txt",
            content_type="text/plain"
        )
        
        print(f"📁 Uploaded to S3: {s3_object.url}")
        
        # Get signed URL
        signed_url = await aws.get_content_url(s3_object.key)
        print(f"🔗 Signed URL: {signed_url}")
        
        # Send email
        message_id = await aws.send_email(
            to_addresses=["recipient@example.com"],
            subject="Test Email from Ainflue",
            body_text="This is a test email sent via AWS SES integration.",
            from_address="noreply@ainflue.com"
        )
        
        print(f"📧 Sent email: {message_id}")
        
        # Put CloudWatch metric
        await aws.put_cloudwatch_metric(
            namespace="Ainflue/Integration",
            metric_name="TestMetric",
            value=1.0,
            dimensions={"Service": "AWS"}
        )
        
        print("📊 Sent CloudWatch metric")


if __name__ == "__main__":
    asyncio.run(main())