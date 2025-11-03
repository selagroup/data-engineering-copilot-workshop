import os
import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Any, Union
from datetime import datetime
import logging

class DataPartitioner:
    """
    A class to partition datasets by date and write to parquet files.
    
    Supports configurable compression types, maximum file size limits,
    and custom output directory paths.
    """
    
    SUPPORTED_COMPRESSIONS = ['snappy', 'gzip', 'brotli', 'lz4', None]
    DEFAULT_MAX_FILE_SIZE_MB = 100
    DEFAULT_COMPRESSION = 'snappy'
    
    def __init__(self, 
                 outputDirectory: str,
                 maxFileSizeMb: Optional[int] = None,
                 compressionType: Optional[str] = None,
                 dateColumn: str = 'date'):
        """
        Initialize the DataPartitioner.
        
        Args:
            outputDirectory: Path where partitioned files will be written
            maxFileSizeMb: Maximum file size in MB before splitting
            compressionType: Compression type for parquet files
            dateColumn: Name of the date column for partitioning
        """
        self.outputDirectory = Path(outputDirectory)
        self.maxFileSizeMb = maxFileSizeMb or self.DEFAULT_MAX_FILE_SIZE_MB
        self.compressionType = compressionType or self.DEFAULT_COMPRESSION
        self.dateColumn = dateColumn
        
        self._validate_configuration()
        self._setup_logging()
        self._ensure_output_directory()
    
    def _validate_configuration(self) -> None:
        """Validate the configuration parameters."""
        if self.compressionType not in self.SUPPORTED_COMPRESSIONS:
            raise ValueError(f"Unsupported compression type: {self.compressionType}. "
                           f"Supported types: {self.SUPPORTED_COMPRESSIONS}")
        
        if self.maxFileSizeMb <= 0:
            raise ValueError("Maximum file size must be greater than 0")
    
    def _setup_logging(self) -> None:
        """Setup logging for the partitioner."""
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def _ensure_output_directory(self) -> None:
        """Create output directory if it doesn't exist."""
        self.outputDirectory.mkdir(parents=True, exist_ok=True)
        self.logger.info(f"Output directory set to: {self.outputDirectory}")
    
    def _get_partition_path(self, date_value: Union[str, datetime]) -> Path:
        """
        Generate partition path based on date value.
        
        Args:
            date_value: Date value for partitioning
            
        Returns:
            Path object for the partition directory
        """
        if isinstance(date_value, str):
            date_value = pd.to_datetime(date_value)
        
        year = date_value.year
        month = f"{date_value.month:02d}"
        day = f"{date_value.day:02d}"
        
        partition_path = self.outputDirectory / f"year={year}" / f"month={month}" / f"day={day}"
        partition_path.mkdir(parents=True, exist_ok=True)
        
        return partition_path
    
    def _get_file_size_mb(self, file_path: Path) -> float:
        """Get file size in MB."""
        if file_path.exists():
            return file_path.stat().st_size / (1024 * 1024)
        return 0.0
    
    def _generate_filename(self, partition_path: Path, chunk_index: int = 0) -> Path:
        """
        Generate unique filename for parquet file.
        
        Args:
            partition_path: Directory path for the partition
            chunk_index: Index for file chunks when splitting large partitions
            
        Returns:
            Complete file path for the parquet file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data_{timestamp}_chunk_{chunk_index:03d}.parquet"
        return partition_path / filename
    
    def partition_data(self, dataframe: pd.DataFrame) -> Dict[str, Any]:
        """
        Partition the dataframe by date and write to parquet files.
        
        Args:
            dataframe: Input dataframe to partition
            
        Returns:
            Dictionary with partitioning statistics
        """
        if self.dateColumn not in dataframe.columns:
            raise ValueError(f"Date column '{self.dateColumn}' not found in dataframe")
        
        # Ensure date column is datetime
        dataframe[self.dateColumn] = pd.to_datetime(dataframe[self.dateColumn])
        
        # Group by date
        grouped = dataframe.groupby(dataframe[self.dateColumn].dt.date)
        
        partitionStats = {
            'totalPartitions': 0,
            'totalFiles': 0,
            'totalRows': len(dataframe),
            'partitionDetails': []
        }
        
        for date_value, partition_data in grouped:
            self.logger.info(f"Processing partition for date: {date_value}")
            
            partition_path = self._get_partition_path(date_value)
            filesCreated = self._write_partition_data(partition_data, partition_path)
            
            partitionStats['totalPartitions'] += 1
            partitionStats['totalFiles'] += filesCreated
            partitionStats['partitionDetails'].append({
                'date': str(date_value),
                'rows': len(partition_data),
                'files': filesCreated,
                'path': str(partition_path)
            })
        
        self.logger.info(f"Partitioning complete. Created {partitionStats['totalFiles']} files "
                        f"across {partitionStats['totalPartitions']} partitions")
        
        return partitionStats
    
    def _write_partition_data(self, partition_data: pd.DataFrame, partition_path: Path) -> int:
        """
        Write partition data to parquet files, splitting if necessary.
        
        Args:
            partition_data: Data for this partition
            partition_path: Directory path for the partition
            
        Returns:
            Number of files created for this partition
        """
        filesCreated = 0
        chunkIndex = 0
        
        # Calculate approximate chunk size based on max file size
        estimatedRowSize = partition_data.memory_usage(deep=True).sum() / len(partition_data)
        approximateRowsPerChunk = int((self.maxFileSizeMb * 1024 * 1024) / estimatedRowSize)
        
        # Split data into chunks if needed
        if approximateRowsPerChunk < len(partition_data):
            self.logger.info(f"Splitting partition into chunks of ~{approximateRowsPerChunk} rows")
            
            for i in range(0, len(partition_data), approximateRowsPerChunk):
                chunk = partition_data.iloc[i:i + approximateRowsPerChunk]
                filePath = self._generate_filename(partition_path, chunkIndex)
                
                chunk.to_parquet(
                    filePath,
                    compression=self.compressionType,
                    index=False
                )
                
                actualSizeMb = self._get_file_size_mb(filePath)
                self.logger.info(f"Created file: {filePath.name} ({actualSizeMb:.2f} MB)")
                
                filesCreated += 1
                chunkIndex += 1
        else:
            # Write entire partition to single file
            filePath = self._generate_filename(partition_path, 0)
            
            partition_data.to_parquet(
                filePath,
                compression=self.compressionType,
                index=False
            )
            
            actualSizeMb = self._get_file_size_mb(filePath)
            self.logger.info(f"Created file: {filePath.name} ({actualSizeMb:.2f} MB)")
            filesCreated = 1
        
        return filesCreated
    
    def read_partition(self, date_value: Union[str, datetime]) -> pd.DataFrame:
        """
        Read all files from a specific date partition.
        
        Args:
            date_value: Date value to read
            
        Returns:
            Combined dataframe from all files in the partition
        """
        partition_path = self._get_partition_path(date_value)
        
        if not partition_path.exists():
            raise FileNotFoundError(f"Partition for date {date_value} not found at {partition_path}")
        
        parquet_files = list(partition_path.glob("*.parquet"))
        
        if not parquet_files:
            raise FileNotFoundError(f"No parquet files found in partition {partition_path}")
        
        dataframes = []
        for file_path in parquet_files:
            df = pd.read_parquet(file_path)
            dataframes.append(df)
        
        combined_df = pd.concat(dataframes, ignore_index=True)
        self.logger.info(f"Read {len(combined_df)} rows from {len(parquet_files)} files")
        
        return combined_df


# Example usage
if __name__ == "__main__":
    # Create sample data
    sampleData = pd.DataFrame({
        'date': pd.date_range('2024-01-01', periods=1000, freq='D'),
        'value': range(1000),
        'category': ['A', 'B', 'C'] * 334
    })
    
    # Initialize partitioner
    partitioner = DataPartitioner(
        outputDirectory="c:\\Users\\roeel\\projects\\sela\\data-engineering-copilot-workshop\\output\\partitioned_data",
        maxFileSizeMb=50,
        compressionType='snappy',
        dateColumn='date'
    )
    
    # Partition the data
    stats = partitioner.partition_data(sampleData)
    print(f"Partitioning completed: {stats}")
