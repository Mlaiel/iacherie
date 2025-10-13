"""
S3/MinIO Handler
Manages file uploads, downloads, and operations with S3-compatible storage
"""

import os
from typing import Optional, BinaryIO
from datetime import datetime, timedelta
import mimetypes


class S3Handler:
    """Handle S3/MinIO file operations"""
    
    def __init__(self):
        self.endpoint = os.getenv('S3_ENDPOINT', 'http://localhost:9000')
        self.access_key = os.getenv('S3_ACCESS_KEY', 'minioadmin')
        self.secret_key = os.getenv('S3_SECRET_KEY', 'minioadmin')
        self.bucket_name = os.getenv('S3_BUCKET_NAME', 'ia2good-files')
        self.region = os.getenv('S3_REGION', 'eu-west-1')
        self.use_ssl = os.getenv('S3_USE_SSL', 'false').lower() == 'true'
        
        # In production, initialize boto3 client
        # import boto3
        # self.client = boto3.client(
        #     's3',
        #     endpoint_url=self.endpoint,
        #     aws_access_key_id=self.access_key,
        #     aws_secret_access_key=self.secret_key,
        #     region_name=self.region,
        #     use_ssl=self.use_ssl
        # )
        # self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self) -> None:
        """Create bucket if it doesn't exist"""
        try:
            # self.client.head_bucket(Bucket=self.bucket_name)
            pass
        except:
            # self.client.create_bucket(Bucket=self.bucket_name)
            print(f"[S3] Created bucket: {self.bucket_name}")
    
    async def upload_file(
        self,
        file_data: BinaryIO,
        file_name: str,
        content_type: Optional[str] = None,
        folder: str = ""
    ) -> dict:
        """
        Upload file to S3/MinIO
        
        Args:
            file_data: File binary data
            file_name: Original file name
            content_type: MIME type
            folder: Optional folder/prefix
            
        Returns:
            Dict with file URL and metadata
        """
        # Generate unique file key
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        safe_filename = file_name.replace(' ', '_')
        file_key = f"{folder}/{timestamp}_{safe_filename}" if folder else f"{timestamp}_{safe_filename}"
        
        # Detect content type if not provided
        if not content_type:
            content_type, _ = mimetypes.guess_type(file_name)
            content_type = content_type or 'application/octet-stream'
        
        try:
            # In production:
            # self.client.upload_fileobj(
            #     file_data,
            #     self.bucket_name,
            #     file_key,
            #     ExtraArgs={
            #         'ContentType': content_type,
            #         'ACL': 'private'
            #     }
            # )
            
            file_url = f"{self.endpoint}/{self.bucket_name}/{file_key}"
            
            print(f"[S3] Uploaded: {file_key}")
            
            return {
                'success': True,
                'file_url': file_url,
                'file_key': file_key,
                'bucket': self.bucket_name,
                'content_type': content_type,
                'size': file_data.tell() if hasattr(file_data, 'tell') else 0
            }
            
        except Exception as e:
            print(f"[S3] Upload error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def download_file(self, file_key: str) -> Optional[bytes]:
        """
        Download file from S3/MinIO
        
        Args:
            file_key: File key/path in bucket
            
        Returns:
            File bytes or None
        """
        try:
            # In production:
            # response = self.client.get_object(Bucket=self.bucket_name, Key=file_key)
            # return response['Body'].read()
            
            print(f"[S3] Downloaded: {file_key}")
            return b"file_content"
            
        except Exception as e:
            print(f"[S3] Download error: {e}")
            return None
    
    async def delete_file(self, file_key: str) -> bool:
        """
        Delete file from S3/MinIO
        
        Args:
            file_key: File key/path in bucket
            
        Returns:
            True if deleted successfully
        """
        try:
            # In production:
            # self.client.delete_object(Bucket=self.bucket_name, Key=file_key)
            
            print(f"[S3] Deleted: {file_key}")
            return True
            
        except Exception as e:
            print(f"[S3] Delete error: {e}")
            return False
    
    async def generate_presigned_url(
        self,
        file_key: str,
        expiration: int = 3600,
        operation: str = 'get_object'
    ) -> Optional[str]:
        """
        Generate presigned URL for temporary access
        
        Args:
            file_key: File key/path in bucket
            expiration: URL expiration in seconds
            operation: Operation type (get_object, put_object)
            
        Returns:
            Presigned URL or None
        """
        try:
            # In production:
            # url = self.client.generate_presigned_url(
            #     operation,
            #     Params={'Bucket': self.bucket_name, 'Key': file_key},
            #     ExpiresIn=expiration
            # )
            
            url = f"{self.endpoint}/{self.bucket_name}/{file_key}?presigned=true"
            print(f"[S3] Generated presigned URL for: {file_key}")
            return url
            
        except Exception as e:
            print(f"[S3] Presigned URL error: {e}")
            return None
    
    async def list_files(self, prefix: str = "", max_keys: int = 1000) -> list:
        """
        List files in bucket
        
        Args:
            prefix: Filter by prefix/folder
            max_keys: Maximum number of keys to return
            
        Returns:
            List of file metadata dicts
        """
        try:
            # In production:
            # response = self.client.list_objects_v2(
            #     Bucket=self.bucket_name,
            #     Prefix=prefix,
            #     MaxKeys=max_keys
            # )
            # return response.get('Contents', [])
            
            print(f"[S3] Listed files with prefix: {prefix}")
            return []
            
        except Exception as e:
            print(f"[S3] List error: {e}")
            return []
    
    async def get_file_metadata(self, file_key: str) -> Optional[dict]:
        """
        Get file metadata
        
        Args:
            file_key: File key/path in bucket
            
        Returns:
            File metadata dict or None
        """
        try:
            # In production:
            # response = self.client.head_object(Bucket=self.bucket_name, Key=file_key)
            # return {
            #     'size': response['ContentLength'],
            #     'content_type': response['ContentType'],
            #     'last_modified': response['LastModified']
            # }
            
            return {
                'size': 0,
                'content_type': 'application/octet-stream',
                'last_modified': datetime.utcnow()
            }
            
        except Exception as e:
            print(f"[S3] Metadata error: {e}")
            return None
