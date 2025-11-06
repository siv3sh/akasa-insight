"""
Storage abstraction for local filesystem and S3-compatible storage.
"""

import os
import boto3
import pandas as pd
from pathlib import Path
from typing import Optional, Union
from abc import ABC, abstractmethod


class StorageBackend(ABC):
    """Abstract base class for storage backends."""
    
    @abstractmethod
    def save_dataframe(self, df: pd.DataFrame, path: str, **kwargs) -> str:
        """Save DataFrame to storage."""
        pass
    
    @abstractmethod
    def load_dataframe(self, path: str, **kwargs) -> pd.DataFrame:
        """Load DataFrame from storage."""
        pass
    
    @abstractmethod
    def file_exists(self, path: str) -> bool:
        """Check if file exists in storage."""
        pass


class LocalStorage(StorageBackend):
    """Local filesystem storage backend."""
    
    def __init__(self, base_path: str = "."):
        """
        Initialize local storage backend.
        
        Args:
            base_path: Base path for local storage
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def save_dataframe(self, df: pd.DataFrame, path: str, **kwargs) -> str:
        """
        Save DataFrame to local filesystem.
        
        Args:
            df: DataFrame to save
            path: Path to save file
            **kwargs: Additional arguments (format, etc.)
            
        Returns:
            Full path to saved file
        """
        full_path = self.base_path / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        format = kwargs.get('format', 'parquet')
        if format == 'parquet':
            df.to_parquet(full_path, index=False)
        elif format == 'csv':
            df.to_csv(full_path, index=False)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        return str(full_path)
    
    def load_dataframe(self, path: str, **kwargs) -> pd.DataFrame:
        """
        Load DataFrame from local filesystem.
        
        Args:
            path: Path to file
            **kwargs: Additional arguments
            
        Returns:
            Loaded DataFrame
        """
        full_path = self.base_path / path
        
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {full_path}")
        
        format = kwargs.get('format', 'parquet')
        if format == 'parquet':
            return pd.read_parquet(full_path)
        elif format == 'csv':
            return pd.read_csv(full_path)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def file_exists(self, path: str) -> bool:
        """
        Check if file exists in local filesystem.
        
        Args:
            path: Path to check
            
        Returns:
            True if file exists, False otherwise
        """
        full_path = self.base_path / path
        return full_path.exists()


class S3Storage(StorageBackend):
    """S3-compatible storage backend."""
    
    def __init__(self, bucket_name: str, aws_access_key_id: Optional[str] = None,
                 aws_secret_access_key: Optional[str] = None, region_name: Optional[str] = None,
                 endpoint_url: Optional[str] = None):
        """
        Initialize S3 storage backend.
        
        Args:
            bucket_name: S3 bucket name
            aws_access_key_id: AWS access key ID
            aws_secret_access_key: AWS secret access key
            region_name: AWS region name
            endpoint_url: S3 endpoint URL (for non-AWS S3-compatible services)
        """
        self.bucket_name = bucket_name
        
        # Initialize S3 client
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name,
            endpoint_url=endpoint_url
        )
    
    def save_dataframe(self, df: pd.DataFrame, path: str, **kwargs) -> str:
        """
        Save DataFrame to S3.
        
        Args:
            df: DataFrame to save
            path: S3 key path
            **kwargs: Additional arguments (format, etc.)
            
        Returns:
            S3 URI of saved file
        """
        format = kwargs.get('format', 'parquet')
        
        # Save to temporary local file
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=f'.{format}', delete=False) as tmp_file:
            temp_path = tmp_file.name
            if format == 'parquet':
                df.to_parquet(temp_path, index=False)
            elif format == 'csv':
                df.to_csv(temp_path, index=False)
            else:
                raise ValueError(f"Unsupported format: {format}")
        
        # Upload to S3
        try:
            self.s3_client.upload_file(temp_path, self.bucket_name, path)
            s3_uri = f"s3://{self.bucket_name}/{path}"
            return s3_uri
        finally:
            # Clean up temporary file
            os.unlink(temp_path)
    
    def load_dataframe(self, path: str, **kwargs) -> pd.DataFrame:
        """
        Load DataFrame from S3.
        
        Args:
            path: S3 key path
            **kwargs: Additional arguments
            
        Returns:
            Loaded DataFrame
        """
        format = kwargs.get('format', 'parquet')
        
        # Download to temporary local file
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=f'.{format}', delete=False) as tmp_file:
            temp_path = tmp_file.name
        
        try:
            # Download from S3
            self.s3_client.download_file(self.bucket_name, path, temp_path)
            
            # Load DataFrame
            if format == 'parquet':
                return pd.read_parquet(temp_path)
            elif format == 'csv':
                return pd.read_csv(temp_path)
            else:
                raise ValueError(f"Unsupported format: {format}")
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def file_exists(self, path: str) -> bool:
        """
        Check if file exists in S3.
        
        Args:
            path: S3 key path
            
        Returns:
            True if file exists, False otherwise
        """
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=path)
            return True
        except self.s3_client.exceptions.NoSuchKey:
            return False
        except self.s3_client.exceptions.ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            raise


class StorageManager:
    """Storage manager that abstracts different storage backends."""
    
    def __init__(self, backend: str = 'local', **kwargs):
        """
        Initialize storage manager.
        
        Args:
            backend: Storage backend ('local' or 's3')
            **kwargs: Backend-specific configuration
        """
        if backend == 'local':
            self.storage = LocalStorage(**kwargs)
        elif backend == 's3':
            self.storage = S3Storage(**kwargs)
        else:
            raise ValueError(f"Unsupported backend: {backend}")
    
    def save_dataframe(self, df: pd.DataFrame, path: str, **kwargs) -> str:
        """
        Save DataFrame using configured backend.
        
        Args:
            df: DataFrame to save
            path: Path/Key to save file
            **kwargs: Additional arguments
            
        Returns:
            URI/Path of saved file
        """
        return self.storage.save_dataframe(df, path, **kwargs)
    
    def load_dataframe(self, path: str, **kwargs) -> pd.DataFrame:
        """
        Load DataFrame using configured backend.
        
        Args:
            path: Path/Key to file
            **kwargs: Additional arguments
            
        Returns:
            Loaded DataFrame
        """
        return self.storage.load_dataframe(path, **kwargs)
    
    def file_exists(self, path: str) -> bool:
        """
        Check if file exists using configured backend.
        
        Args:
            path: Path/Key to check
            
        Returns:
            True if file exists, False otherwise
        """
        return self.storage.file_exists(path)


# Example usage
if __name__ == "__main__":
    # Local storage example
    local_storage = StorageManager('local', base_path='data/warehouse')
    
    # Create sample DataFrame
    sample_df = pd.DataFrame({
        'id': [1, 2, 3],
        'name': ['Alice', 'Bob', 'Charlie'],
        'value': [100, 200, 300]
    })
    
    # Save to local storage
    local_path = local_storage.save_dataframe(sample_df, 'sample_data.parquet')
    print(f"Saved to local storage: {local_path}")
    
    # Load from local storage
    loaded_df = local_storage.load_dataframe('sample_data.parquet')
    print("Loaded from local storage:")
    print(loaded_df)
    
    # S3 storage example (uncomment and configure for actual use)
    # s3_storage = StorageManager('s3', 
    #                            bucket_name='your-bucket',
    #                            aws_access_key_id='your-access-key',
    #                            aws_secret_access_key='your-secret-key')
    # s3_path = s3_storage.save_dataframe(sample_df, 'sample_data.parquet')
    # print(f"Saved to S3: {s3_path}")