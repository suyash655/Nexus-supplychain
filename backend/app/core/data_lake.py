"""
NEXUS — Data Lake Architecture (SAP IBP-style)
==============================================
Data lake storage, organization, and management for enterprise
supply chain data with support for structured, semi-structured,
and unstructured data, plus streaming processing capabilities.
"""

import hashlib
import logging
import os
import queue
import threading
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

import boto3
import pandas as pd
from botocore.exceptions import ClientError

logger_dl = logging.getLogger("nexus.data_lake")


class DataType(Enum):
    """Types of data stored in the data lake."""
    STRUCTURED = "structured"      # Tables, CSV, JSON
    SEMI_STRUCTURED = "semi_structured"  # XML, JSON logs
    UNSTRUCTURED = "unstructured"  # PDFs, images, documents
    STREAMING = "streaming"        # Real-time data streams


class DataLakeZone(Enum):
    """Data lake zones for organizing data by processing stage."""
    RAW = "raw"                    # Original data, immutable
    BRONZE = "bronze"             # Cleaned but not transformed
    SILVER = "silver"             # Validated and conformed
    GOLD = "gold"                 # Business-ready, aggregated


class StreamProcessingMode(Enum):
    """Stream processing modes."""
    REALTIME = "realtime"         # Process records as they arrive
    MICRO_BATCH = "micro_batch"   # Process in small batches
    WINDOWED = "windowed"         # Process in time windows


@dataclass
class StreamEvent:
    """Represents a single streaming event."""
    event_id: str
    event_type: str
    data: Dict[str, Any]
    timestamp: datetime
    source: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ProcessingResult:
    """Result of stream processing operation."""
    success: bool
    event_id: str
    processed_at: datetime
    error_message: Optional[str] = None
    processing_time_ms: Optional[float] = None


class DataLakeEngine:
    """
    Enterprise data lake with multi-zone architecture,
    support for multiple storage backends, and automated
    data organization.
    """

    def __init__(self):
        self.storage_config = {}
        self.metadata_store = {}
        self.partitions = {}
        self._initialised = False

    def initialize(self, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Initialize data lake with storage configuration.

        Args:
            config: Configuration dict with storage backend settings
                - storage_type: "local", "s3", "azure", "gcs"
                - base_path: Base path for data storage
                - credentials: Storage credentials (if needed)
        """
        try:
            default_config = {
                "storage_type": "local",
                "base_path": "./data_lake",
                "zones": {
                    "raw": "raw",
                    "bronze": "bronze",
                    "silver": "silver",
                    "gold": "gold"
                },
                "partitions": ["year", "month", "day", "tenant_id"],
                "formats": {
                    "structured": "parquet",
                    "semi_structured": "json",
                    "unstructured": "original",
                    "streaming": "parquet"
                }
            }

            config = config or default_config
            self.storage_config = config

            # Create directory structure for local storage
            if config["storage_type"] == "local":
                self._create_local_structure(config["base_path"], config["zones"])

            # Initialize S3 client if using S3
            elif config["storage_type"] == "s3":
                self._init_s3_storage(config)

            self._initialised = True

            return {
                "status": "success",
                "storage_type": config["storage_type"],
                "zones_configured": len(config["zones"]),
                "initialised_at": datetime.now(timezone.utc).isoformat()
            }

        except Exception as e:
            logger_dl.error(f"Error initializing data lake: {e}")
            return {"error": str(e), "initialised": False}

    def _create_local_structure(self, base_path: str, zones: Dict[str, str]):
        """Create local directory structure for data lake."""
        base = Path(base_path)

        for zone_name, zone_path in zones.items():
            zone_dir = base / zone_path
            zone_dir.mkdir(parents=True, exist_ok=True)

            # Create subdirectories for data types
            for data_type in DataType:
                type_dir = zone_dir / data_type.value
                type_dir.mkdir(parents=True, exist_ok=True)

    def _init_s3_storage(self, config: Dict[str, Any]):
        """Initialize S3 storage client."""
        try:
            credentials = config.get("credentials", {})
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=credentials.get("access_key_id"),
                aws_secret_access_key=credentials.get("secret_access_key"),
                region_name=credentials.get("region", "us-east-1")
            )
            self.s3_bucket = config.get("bucket_name")

            # Create bucket if it doesn't exist
            try:
                self.s3_client.head_bucket(Bucket=self.s3_bucket)
            except ClientError:
                self.s3_client.create_bucket(Bucket=self.s3_bucket)

        except Exception as e:
            logger_dl.error(f"Error initializing S3 storage: {e}")
            raise

    def ingest_data(self,
                    data: pd.DataFrame,
                    data_type: DataType,
                    zone: DataLakeZone,
                    source: str,
                    metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Ingest data into the data lake.

        Args:
            data: Pandas DataFrame to ingest
            data_type: Type of data being ingested
            zone: Target zone in the data lake
            source: Data source identifier
            metadata: Optional metadata about the data
        """
        if not self._initialised:
            return {"error": "Data lake not initialised"}

        try:
            # Generate data ID
            data_id = self._generate_data_id(source, data_type, zone)

            # Create partition structure
            partitions = self._create_partitions(zone)

            # Determine storage path
            storage_path = self._get_storage_path(data_type, zone, partitions, source)

            # Store data based on format
            format_type = self.storage_config["formats"][data_type.value]

            if format_type == "parquet":
                self._store_parquet(data, storage_path)
            elif format_type == "json":
                self._store_json(data, storage_path)
            else:
                self._store_original(data, storage_path)

            # Create metadata
            data_metadata = {
                "data_id": data_id,
                "data_type": data_type.value,
                "zone": zone.value,
                "source": source,
                "storage_path": storage_path,
                "partitions": partitions,
                "row_count": len(data),
                "columns": list(data.columns),
                "size_bytes": self._estimate_size(data),
                "ingested_at": datetime.now(timezone.utc).isoformat(),
                "metadata": metadata or {}
            }

            # Store metadata
            self.metadata_store[data_id] = data_metadata

            return {
                "status": "success",
                "data_id": data_id,
                "storage_path": storage_path,
                "zone": zone.value,
                "partitions": partitions,
                "row_count": len(data),
                "ingested_at": data_metadata["ingested_at"]
            }

        except Exception as e:
            logger_dl.error(f"Error ingesting data: {e}")
            return {"error": str(e)}

    def _generate_data_id(self, source: str, data_type: DataType, zone: DataLakeZone) -> str:
        """Generate unique data ID."""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        hash_input = f"{source}-{data_type.value}-{zone.value}-{timestamp}"
        hash_digest = hashlib.md5(hash_input.encode()).hexdigest()[:8]
        return f"DATA-{timestamp}-{hash_digest}"

    def _create_partitions(self, zone: DataLakeZone) -> Dict[str, str]:
        """Create partition structure for data organization."""
        now = datetime.now(timezone.utc)
        partitions = {
            "year": str(now.year),
            "month": str(now.month).zfill(2),
            "day": str(now.day).zfill(2),
            "hour": str(now.hour).zfill(2)
        }

        # Add tenant partition if available
        if hasattr(self, 'current_tenant_id'):
            partitions["tenant_id"] = self.current_tenant_id

        return partitions

    def _get_storage_path(self, data_type: DataType, zone: DataLakeZone,
                         partitions: Dict[str, str], source: str) -> str:
        """Get storage path based on configuration."""
        if self.storage_config["storage_type"] == "local":
            base_path = self.storage_config["base_path"]
            zone_path = self.storage_config["zones"][zone.value]

            # Create path: base/zone/data_type/partitions/source
            partition_str = "/".join([f"{k}={v}" for k, v in partitions.items()])
            path = f"{base_path}/{zone_path}/{data_type.value}/{partition_str}/{source}"

        elif self.storage_config["storage_type"] == "s3":
            zone_path = self.storage_config["zones"][zone.value]
            partition_str = "/".join([f"{k}={v}" for k, v in partitions.items()])
            path = f"s3://{self.s3_bucket}/{zone_path}/{data_type.value}/{partition_str}/{source}"

        return path

    def _store_parquet(self, data: pd.DataFrame, path: str):
        """Store data as Parquet format."""
        if self.storage_config["storage_type"] == "local":
            # Ensure directory exists
            os.makedirs(os.path.dirname(path), exist_ok=True)
            data.to_parquet(f"{path}.parquet", index=False)
        elif self.storage_config["storage_type"] == "s3":
            # Convert to S3 path
            s3_path = path.replace("s3://", "")
            buffer = data.to_parquet(index=False)
            self.s3_client.put_object(Bucket=self.s3_bucket, Key=s3_path, Body=buffer)

    def _store_json(self, data: pd.DataFrame, path: str):
        """Store data as JSON format."""
        if self.storage_config["storage_type"] == "local":
            os.makedirs(os.path.dirname(path), exist_ok=True)
            data.to_json(f"{path}.json", orient='records', indent=2)
        elif self.storage_config["storage_type"] == "s3":
            s3_path = path.replace("s3://", "")
            buffer = data.to_json(orient='records', indent=2)
            self.s3_client.put_object(Bucket=self.s3_bucket, Key=s3_path, Body=buffer)

    def _store_original(self, data: pd.DataFrame, path: str):
        """Store data in original format."""
        # For now, use parquet as original
        self._store_parquet(data, path)

    def _estimate_size(self, data: pd.DataFrame) -> int:
        """Estimate data size in bytes."""
        return data.memory_usage(deep=True).sum()

    def query_data(self,
                   zone: DataLakeZone,
                   data_type: DataType,
                   filters: Optional[Dict[str, Any]] = None,
                   time_range: Optional[Tuple[datetime, datetime]] = None) -> Dict[str, Any]:
        """
        Query data from the data lake.

        Args:
            zone: Zone to query
            data_type: Type of data to query
            filters: Optional filters to apply
            time_range: Optional time range for data
        """
        if not self._initialised:
            return {"error": "Data lake not initialised"}

        try:
            # Build query path
            partitions = self._create_partitions(zone)
            base_path = self._get_storage_path(data_type, zone, partitions, "")

            # Collect matching files
            matching_files = self._find_matching_files(base_path, filters, time_range)

            # Load and combine data
            all_data = []
            for file_path in matching_files:
                try:
                    if file_path.endswith('.parquet'):
                        df = pd.read_parquet(file_path)
                    elif file_path.endswith('.json'):
                        df = pd.read_json(file_path)
                    else:
                        continue

                    all_data.append(df)
                except Exception as e:
                    logger_dl.warning(f"Error reading file {file_path}: {e}")

            if all_data:
                combined_data = pd.concat(all_data, ignore_index=True)

                # Apply filters
                if filters:
                    combined_data = self._apply_filters(combined_data, filters)

                return {
                    "status": "success",
                    "data": combined_data,
                    "row_count": len(combined_data),
                    "columns": list(combined_data.columns),
                    "files_processed": len(matching_files)
                }
            else:
                return {
                    "status": "success",
                    "data": pd.DataFrame(),
                    "row_count": 0,
                    "message": "No matching data found"
                }

        except Exception as e:
            logger_dl.error(f"Error querying data: {e}")
            return {"error": str(e)}

    def _find_matching_files(self, base_path: str, filters: Optional[Dict[str, Any]],
                           time_range: Optional[Tuple[datetime, datetime]]) -> List[str]:
        """Find files matching the query criteria."""
        matching_files = []

        if self.storage_config["storage_type"] == "local":
            if os.path.exists(base_path):
                for root, dirs, files in os.walk(base_path):
                    for file in files:
                        if file.endswith(('.parquet', '.json')):
                            file_path = os.path.join(root, file)
                            matching_files.append(file_path)

        elif self.storage_config["storage_type"] == "s3":
            # List S3 objects
            prefix = base_path.replace(f"s3://{self.s3_bucket}/", "")
            paginator = self.s3_client.get_paginator('list_objects_v2')

            for page in paginator.paginate(Bucket=self.s3_bucket, Prefix=prefix):
                for obj in page.get('Contents', []):
                    key = obj['Key']
                    if key.endswith(('.parquet', '.json')):
                        file_path = f"s3://{self.s3_bucket}/{key}"
                        matching_files.append(file_path)

        return matching_files

    def _apply_filters(self, data: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
        """Apply filters to the data."""
        filtered_data = data.copy()

        for column, condition in filters.items():
            if column in filtered_data.columns:
                if isinstance(condition, dict):
                    # Handle complex conditions
                    if 'eq' in condition:
                        filtered_data = filtered_data[filtered_data[column] == condition['eq']]
                    elif 'ne' in condition:
                        filtered_data = filtered_data[filtered_data[column] != condition['ne']]
                    elif 'gt' in condition:
                        filtered_data = filtered_data[filtered_data[column] > condition['gt']]
                    elif 'lt' in condition:
                        filtered_data = filtered_data[filtered_data[column] < condition['lt']]
                    elif 'in' in condition:
                        filtered_data = filtered_data[filtered_data[column].isin(condition['in'])]
                else:
                    # Simple equality filter
                    filtered_data = filtered_data[filtered_data[column] == condition]

        return filtered_data

    def promote_data(self,
                    data_id: str,
                    target_zone: DataLakeZone,
                    transformations: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Promote data from one zone to another with optional transformations.

        Args:
            data_id: ID of data to promote
            target_zone: Target zone for promotion
            transformations: Optional transformations to apply
        """
        if data_id not in self.metadata_store:
            return {"error": "Data ID not found"}

        try:
            metadata = self.metadata_store[data_id]
            current_zone = DataLakeZone(metadata["zone"])

            # Validate promotion path
            if not self._validate_promotion(current_zone, target_zone):
                return {"error": f"Invalid promotion path from {current_zone.value} to {target_zone.value}"}

            # Load data from current zone
            storage_path = metadata["storage_path"]
            data = self._load_data(storage_path)

            # Apply transformations if provided
            if transformations:
                data = self._apply_transformations(data, transformations)

            # Ingest into target zone
            result = self.ingest_data(
                data=data,
                data_type=DataType(metadata["data_type"]),
                zone=target_zone,
                source=metadata["source"],
                metadata={
                    "parent_data_id": data_id,
                    "transformations": transformations
                }
            )

            # Update metadata
            metadata["promoted_to"] = target_zone.value
            metadata["promoted_at"] = datetime.now(timezone.utc).isoformat()
            metadata["child_data_id"] = result.get("data_id")

            return {
                "status": "success",
                "original_data_id": data_id,
                "new_data_id": result.get("data_id"),
                "from_zone": current_zone.value,
                "to_zone": target_zone.value,
                "promoted_at": metadata["promoted_at"]
            }

        except Exception as e:
            logger_dl.error(f"Error promoting data: {e}")
            return {"error": str(e)}

    def _validate_promotion(self, from_zone: DataLakeZone, to_zone: DataLakeZone) -> bool:
        """Validate that promotion follows the data lake path."""
        zone_order = [DataLakeZone.RAW, DataLakeZone.BRONZE, DataLakeZone.SILVER, DataLakeZone.GOLD]

        from_index = zone_order.index(from_zone)
        to_index = zone_order.index(to_zone)

        return to_index == from_index + 1

    def _load_data(self, storage_path: str) -> pd.DataFrame:
        """Load data from storage path."""
        if storage_path.startswith("s3://"):
            # Load from S3
            s3_path = storage_path.replace("s3://", "")
            obj = self.s3_client.get_object(Bucket=self.s3_bucket, Key=s3_path)
            if s3_path.endswith('.parquet'):
                return pd.read_parquet(obj['Body'])
            elif s3_path.endswith('.json'):
                return pd.read_json(obj['Body'])
        else:
            # Load from local storage
            if storage_path.endswith('.parquet'):
                return pd.read_parquet(storage_path)
            elif storage_path.endswith('.json'):
                return pd.read_json(storage_path)

        return pd.DataFrame()

    def _apply_transformations(self, data: pd.DataFrame,
                             transformations: Dict[str, Any]) -> pd.DataFrame:
        """Apply transformations to the data."""
        transformed_data = data.copy()

        for transformation in transformations.get("operations", []):
            transform_type = transformation.get("type")

            if transform_type == "filter":
                transformed_data = self._apply_filters(transformed_data, transformation.get("conditions", {}))

            elif transform_type == "aggregate":
                group_by = transformation.get("group_by", [])
                aggregations = transformation.get("aggregations", {})
                transformed_data = transformed_data.groupby(group_by).agg(aggregations).reset_index()

            elif transform_type == "rename_columns":
                column_mapping = transformation.get("mapping", {})
                transformed_data = transformed_data.rename(columns=column_mapping)

            elif transform_type == "add_columns":
                new_columns = transformation.get("columns", {})
                for col_name, col_value in new_columns.items():
                    transformed_data[col_name] = col_value

            elif transform_type == "drop_columns":
                columns_to_drop = transformation.get("columns", [])
                transformed_data = transformed_data.drop(columns=columns_to_drop, errors='ignore')

        return transformed_data

    def get_metadata(self, data_id: str) -> Dict[str, Any]:
        """Get metadata for a specific data ID."""
        if data_id in self.metadata_store:
            return self.metadata_store[data_id]
        else:
            return {"error": "Data ID not found"}

    def list_data(self,
                  zone: Optional[DataLakeZone] = None,
                  data_type: Optional[DataType] = None,
                  source: Optional[str] = None) -> Dict[str, Any]:
        """List data in the data lake with optional filters."""
        filtered_metadata = {}

        for data_id, metadata in self.metadata_store.items():
            # Apply filters
            if zone and metadata["zone"] != zone.value:
                continue
            if data_type and metadata["data_type"] != data_type.value:
                continue
            if source and metadata["source"] != source:
                continue

            filtered_metadata[data_id] = metadata

        return {
            "status": "success",
            "count": len(filtered_metadata),
            "data": filtered_metadata
        }

    def get_storage_usage(self) -> Dict[str, Any]:
        """Get storage usage statistics."""
        zone_usage = {}
        total_size = 0

        for metadata in self.metadata_store.values():
            zone = metadata["zone"]
            size = metadata.get("size_bytes", 0)

            if zone not in zone_usage:
                zone_usage[zone] = {"count": 0, "total_bytes": 0}

            zone_usage[zone]["count"] += 1
            zone_usage[zone]["total_bytes"] += size
            total_size += size

        return {
            "status": "success",
            "total_data_ids": len(self.metadata_store),
            "total_size_bytes": total_size,
            "zone_usage": zone_usage,
            "calculated_at": datetime.now(timezone.utc).isoformat()
        }


class StreamProcessor:
    """
    Real-time stream processing engine for the data lake.
    Handles ingestion, processing, and storage of streaming data.
    """

    def __init__(self, data_lake: DataLakeEngine):
        self.data_lake = data_lake
        self.event_queue = queue.Queue(maxsize=10000)
        self.processors = {}  # event_type -> processing_function
        self.running = False
        self.worker_thread = None
        self.processing_stats = defaultdict(int)
        self.error_stats = defaultdict(int)
        self.window_buffer = defaultdict(list)  # For windowed processing
        self.config = {
            "batch_size": 100,
            "window_size_seconds": 60,
            "max_retries": 3,
            "processing_timeout": 30
        }

    def initialize(self, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Initialize stream processor with configuration.

        Args:
            config: Configuration dict for stream processing
        """
        try:
            if config:
                self.config.update(config)

            # Register default processors
            self._register_default_processors()

            return {
                "status": "success",
                "config": self.config,
                "registered_processors": len(self.processors),
                "initialized_at": datetime.now(timezone.utc).isoformat()
            }

        except Exception as e:
            logger_dl.error(f"Error initializing stream processor: {e}")
            return {"error": str(e)}

    def _register_default_processors(self):
        """Register default event processors."""
        # Supply chain event processor
        self.processors["supply_chain_event"] = self._process_supply_chain_event
        # Inventory update processor
        self.processors["inventory_update"] = self._process_inventory_update
        # Demand signal processor
        self.processors["demand_signal"] = self._process_demand_signal
        # Risk event processor
        self.processors["risk_event"] = self._process_risk_event

    def register_processor(self, event_type: str, processor: Callable):
        """
        Register a custom processor for an event type.

        Args:
            event_type: Type of event to process
            processor: Processing function that takes a StreamEvent and returns ProcessingResult
        """
        self.processors[event_type] = processor
        logger_dl.info(f"Registered processor for event type: {event_type}")

    def start(self, mode: StreamProcessingMode = StreamProcessingMode.MICRO_BATCH) -> Dict[str, Any]:
        """
        Start the stream processor.

        Args:
            mode: Processing mode (realtime, micro_batch, windowed)
        """
        if self.running:
            return {"error": "Stream processor already running"}

        try:
            self.running = True
            self.processing_mode = mode

            # Start worker thread
            self.worker_thread = threading.Thread(
                target=self._processing_loop,
                args=(mode,),
                daemon=True
            )
            self.worker_thread.start()

            return {
                "status": "success",
                "mode": mode.value,
                "started_at": datetime.now(timezone.utc).isoformat()
            }

        except Exception as e:
            logger_dl.error(f"Error starting stream processor: {e}")
            return {"error": str(e)}

    def stop(self) -> Dict[str, Any]:
        """Stop the stream processor."""
        if not self.running:
            return {"error": "Stream processor not running"}

        try:
            self.running = False

            # Wait for worker thread to finish
            if self.worker_thread:
                self.worker_thread.join(timeout=5)

            # Process remaining events in window buffer
            self._flush_window_buffer()

            return {
                "status": "success",
                "stopped_at": datetime.now(timezone.utc).isoformat(),
                "stats": dict(self.processing_stats),
                "errors": dict(self.error_stats)
            }

        except Exception as e:
            logger_dl.error(f"Error stopping stream processor: {e}")
            return {"error": str(e)}

    def ingest_event(self, event: StreamEvent) -> Dict[str, Any]:
        """
        Ingest a streaming event.

        Args:
            event: StreamEvent to process
        """
        if not self.running:
            return {"error": "Stream processor not running"}

        try:
            # Add to queue
            self.event_queue.put(event, timeout=1)

            return {
                "status": "success",
                "event_id": event.event_id,
                "queued_at": datetime.now(timezone.utc).isoformat()
            }

        except queue.Full:
            return {"error": "Event queue is full"}
        except Exception as e:
            logger_dl.error(f"Error ingesting event: {e}")
            return {"error": str(e)}

    def _processing_loop(self, mode: StreamProcessingMode):
        """Main processing loop."""
        logger_dl.info(f"Starting processing loop in {mode.value} mode")

        while self.running:
            try:
                if mode == StreamProcessingMode.REALTIME:
                    self._process_realtime()
                elif mode == StreamProcessingMode.MICRO_BATCH:
                    self._process_micro_batch()
                elif mode == StreamProcessingMode.WINDOWED:
                    self._process_windowed()

            except Exception as e:
                logger_dl.error(f"Error in processing loop: {e}")
                self.error_stats["processing_loop_errors"] += 1
                threading.Event().wait(1)  # Prevent tight error loop

    def _process_realtime(self):
        """Process events as they arrive (realtime mode)."""
        try:
            event = self.event_queue.get(timeout=0.1)
            result = self._process_single_event(event)

            if result.success:
                self.processing_stats["processed"] += 1
            else:
                self.error_stats["processing_errors"] += 1

        except queue.Empty:
            pass  # No events to process

    def _process_micro_batch(self):
        """Process events in micro-batches."""
        batch = []
        batch_size = self.config["batch_size"]

        # Collect batch
        for _ in range(batch_size):
            try:
                event = self.event_queue.get(timeout=0.1)
                batch.append(event)
            except queue.Empty:
                break

        # Process batch
        if batch:
            results = [self._process_single_event(event) for event in batch]
            successful = sum(1 for r in results if r.success)

            self.processing_stats["batches_processed"] += 1
            self.processing_stats["processed"] += successful
            self.error_stats["processing_errors"] += len(results) - successful

    def _process_windowed(self):
        """Process events in time windows."""
        try:
            event = self.event_queue.get(timeout=0.1)
            event_type = event.event_type

            # Add to window buffer
            self.window_buffer[event_type].append(event)

            # Check if window should be processed
            window_size = self.config["window_size_seconds"]
            if len(self.window_buffer[event_type]) > 0:
                oldest_event = self.window_buffer[event_type][0]
                window_age = (datetime.now(timezone.utc) - oldest_event.timestamp).total_seconds()

                if window_age >= window_size:
                    self._process_window(event_type)

        except queue.Empty:
            # Check for windows that need processing
            for event_type in list(self.window_buffer.keys()):
                if len(self.window_buffer[event_type]) > 0:
                    oldest_event = self.window_buffer[event_type][0]
                    window_age = (datetime.now(timezone.utc) - oldest_event.timestamp).total_seconds()

                    if window_age >= self.config["window_size_seconds"]:
                        self._process_window(event_type)

    def _process_window(self, event_type: str):
        """Process a window of events."""
        events = self.window_buffer[event_type]

        if not events:
            return

        # Convert to DataFrame for batch processing
        data_list = [event.data for event in events]
        df = pd.DataFrame(data_list)

        # Store in data lake
        self.data_lake.ingest_data(
            data=df,
            data_type=DataType.STREAMING,
            zone=DataLakeZone.BRONZE,
            source=f"stream_{event_type}",
            metadata={
                "window_start": events[0].timestamp.isoformat(),
                "window_end": events[-1].timestamp.isoformat(),
                "event_count": len(events)
            }
        )

        # Clear buffer
        self.window_buffer[event_type] = []

        self.processing_stats["windows_processed"] += 1
        self.processing_stats["processed"] += len(events)

    def _process_single_event(self, event: StreamEvent) -> ProcessingResult:
        """Process a single event."""
        start_time = datetime.now(timezone.utc)

        try:
            # Get processor for event type
            processor = self.processors.get(event.event_type)

            if not processor:
                logger_dl.warning(f"No processor found for event type: {event.event_type}")
                return ProcessingResult(
                    success=False,
                    event_id=event.event_id,
                    processed_at=datetime.now(timezone.utc),
                    error_message=f"No processor for event type: {event.event_type}"
                )

            # Process event
            processed_data = processor(event)

            # Store processed data
            if isinstance(processed_data, pd.DataFrame):
                self.data_lake.ingest_data(
                    data=processed_data,
                    data_type=DataType.STREAMING,
                    zone=DataLakeZone.BRONZE,
                    source=event.source,
                    metadata={
                        "event_id": event.event_id,
                        "event_type": event.event_type,
                        "original_timestamp": event.timestamp.isoformat()
                    }
                )

            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000

            return ProcessingResult(
                success=True,
                event_id=event.event_id,
                processed_at=datetime.now(timezone.utc),
                processing_time_ms=processing_time
            )

        except Exception as e:
            logger_dl.error(f"Error processing event {event.event_id}: {e}")
            return ProcessingResult(
                success=False,
                event_id=event.event_id,
                processed_at=datetime.now(timezone.utc),
                error_message=str(e)
            )

    def _flush_window_buffer(self):
        """Flush remaining events in window buffer."""
        for event_type in list(self.window_buffer.keys()):
            if self.window_buffer[event_type]:
                self._process_window(event_type)

    # Default processors
    def _process_supply_chain_event(self, event: StreamEvent) -> pd.DataFrame:
        """Process supply chain events."""
        data = event.data
        df = pd.DataFrame([data])

        # Add processing metadata
        df["processed_at"] = datetime.now(timezone.utc).isoformat()
        df["event_id"] = event.event_id

        return df

    def _process_inventory_update(self, event: StreamEvent) -> pd.DataFrame:
        """Process inventory updates."""
        data = event.data
        df = pd.DataFrame([data])

        # Calculate inventory metrics
        if "quantity" in df.columns and "reorder_point" in df.columns:
            df["below_reorder_point"] = df["quantity"] < df["reorder_point"]

        df["processed_at"] = datetime.now(timezone.utc).isoformat()
        df["event_id"] = event.event_id

        return df

    def _process_demand_signal(self, event: StreamEvent) -> pd.DataFrame:
        """Process demand signals."""
        data = event.data
        df = pd.DataFrame([data])

        # Add demand classification
        if "demand_quantity" in df.columns:
            df["demand_level"] = pd.cut(
                df["demand_quantity"],
                bins=[0, 100, 500, float('inf')],
                labels=["LOW", "MEDIUM", "HIGH"]
            )

        df["processed_at"] = datetime.now(timezone.utc).isoformat()
        df["event_id"] = event.event_id

        return df

    def _process_risk_event(self, event: StreamEvent) -> pd.DataFrame:
        """Process risk events."""
        data = event.data
        df = pd.DataFrame([data])

        # Add risk classification
        if "risk_score" in df.columns:
            df["risk_category"] = pd.cut(
                df["risk_score"],
                bins=[0, 30, 70, 100],
                labels=["LOW", "MEDIUM", "HIGH"]
            )

        df["processed_at"] = datetime.now(timezone.utc).isoformat()
        df["event_id"] = event.event_id

        return df

    def get_processing_stats(self) -> Dict[str, Any]:
        """Get current processing statistics."""
        queue_size = self.event_queue.qsize()

        return {
            "status": "success",
            "running": self.running,
            "processing_mode": getattr(self, 'processing_mode', None),
            "queue_size": queue_size,
            "processing_stats": dict(self.processing_stats),
            "error_stats": dict(self.error_stats),
            "registered_processors": list(self.processors.keys()),
            "window_buffer_sizes": {k: len(v) for k, v in self.window_buffer.items()}
        }
