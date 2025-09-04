# Large Dataset Generation Guide

This guide explains how to efficiently generate large datasets (millions of records) while managing memory and storage constraints.

## 🚀 Quick Start

### Option 1: Direct to Azure Blob Storage (Recommended)
```bash
# Install dependencies
pip install -r requirements.txt

# Generate 4M records directly to blob storage
python generate_large_dataset.py \
    examples/ClientD_Medicare_Membership.yml \
    blob \
    4000000 \
    "DefaultEndpointsProtocol=https;AccountName=..." \
    membership-data \
    membership_4million.csv
```

### Option 2: Local File Generation
```bash
# Generate 4M records to local file
python generate_large_dataset.py \
    examples/ClientD_Medicare_Membership.yml \
    membership_4million.csv \
    4000000
```

### Option 3: Interactive Examples
```bash
# Run interactive examples
python example_4m_generation.py
```

## 📊 Memory & Performance Characteristics

| Records | Memory Usage | File Size | Generation Time* |
|---------|-------------|-----------|------------------|
| 10K     | ~8 MB       | ~8 MB     | ~30 seconds      |
| 100K    | ~8 MB       | ~80 MB    | ~5 minutes       |
| 1M      | ~8 MB       | ~800 MB   | ~45 minutes      |
| 4M      | ~8 MB       | ~3.2 GB   | ~3 hours         |

*Approximate times on modern hardware

## 🔧 Key Features

### Memory Efficiency
- **Chunk-based processing**: Processes data in configurable chunks (default: 10K records)
- **Constant memory usage**: ~8MB regardless of total dataset size
- **No pandas overhead**: Direct CSV writing without DataFrame creation

### Storage Options
- **Direct blob upload**: Stream directly to Azure Blob Storage
- **Local file generation**: Traditional file-based output
- **No temporary files**: Minimal local storage requirements

### Progress Monitoring
- **Real-time progress**: Shows completion percentage, rate, and ETA
- **Memory monitoring**: Tracks actual memory usage during generation
- **Error handling**: Graceful handling of interruptions and errors

## ⚙️ Configuration Options

### Chunk Size Optimization
```python
# For maximum memory efficiency (slower)
generator = MemoryEfficientDataGenerator(yaml_file, chunk_size=1000)

# For balanced performance (recommended)
generator = MemoryEfficientDataGenerator(yaml_file, chunk_size=10000)

# For maximum speed (higher memory usage)
generator = MemoryEfficientDataGenerator(yaml_file, chunk_size=50000)
```

### Azure Blob Storage Setup
```bash
# Set connection string as environment variable
export AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=myaccount;AccountKey=mykey;EndpointSuffix=core.windows.net"

# Or pass directly in command
python generate_large_dataset.py ... blob ... "$CONNECTION_STRING" ...
```

## 🎯 Best Practices for 4M Records

### 1. Use Blob Storage for Large Datasets
- **Pros**: No local storage required, automatic backup, scalable
- **Cons**: Requires Azure account, network dependency

```bash
# Recommended approach for 4M records (with chunked upload)
python generate_large_dataset.py \
    examples/ClientD_Medicare_Membership.yml \
    blob \
    400000 \
    "$AZURE_STORAGE_CONNECTION_STRING" \
    membership-data \
    dev_membership_400k.csv

# Alternative: Simple upload approach (if chunked upload has issues)
python generate_with_simple_blob_upload.py \
    examples/ClientD_Medicare_Membership.yml \
    4000000 \
    "$AZURE_STORAGE_CONNECTION_STRING" \
    membership-data \
    dev_membership_400k.csv
```

### 1a. Handling Upload Timeouts
For very large datasets, Azure blob uploads can timeout. We provide two approaches:

**Chunked Upload (Default)**:
- Uploads data in 50K record blocks
- Includes retry logic and extended timeouts
- More complex but handles large files better

**Simple Upload (Fallback)**:
- Generates local file first, then uploads
- Uses Azure's built-in chunking
- Simpler approach, requires temporary local storage

### 2. Optimize Chunk Size for Your System
```python
# For systems with limited RAM (< 8GB)
chunk_size = 2500  # ~2MB chunks

# For systems with adequate RAM (8-16GB)
chunk_size = 10000  # ~8MB chunks

# For systems with plenty of RAM (> 16GB)
chunk_size = 25000  # ~20MB chunks
```

### 3. Monitor System Resources
```bash
# Monitor memory usage during generation
watch -n 5 'ps aux | grep python | grep generate_large_dataset'

# Monitor disk space (if generating locally)
df -h /path/to/output/directory
```

### 4. Handle Interruptions Gracefully
The generator supports resumable operations:
- Progress is displayed in real-time
- Ctrl+C will cleanly terminate
- For blob uploads, partial data may remain (clean up manually if needed)

## 🔍 Troubleshooting

### Memory Issues
```
Error: MemoryError or system becomes unresponsive
Solution: Reduce chunk_size to 1000-2500
```

### Blob Upload Issues

#### Timeout Errors
```
Error: TimeoutError('The write operation timed out')
Error: ServiceResponseError: ('Connection aborted.', TimeoutError)

Root Cause: Large file uploads (>1GB) can exceed Azure's default timeout limits

Solutions:
1. Use the improved chunked upload (automatically applied in generate_large_dataset.py)
2. Use the simple upload approach: python generate_with_simple_blob_upload.py
3. Reduce dataset size for testing: try 100K records first
4. Check network stability and speed
```

#### Connection Issues
```
Error: Azure connection timeout
Solution: Check connection string and network connectivity
```

### Disk Space Issues
```
Error: No space left on device
Solution: Use blob storage option or free up disk space
```

### Performance Issues
```
Issue: Generation is very slow
Solutions:
- Increase chunk_size (if memory allows)
- Use SSD storage for local generation
- Check network speed for blob uploads
```

## 📈 Scaling Beyond 4M Records

For datasets larger than 4M records:

1. **Use smaller chunk sizes** (1000-2500) to maintain memory efficiency
2. **Consider parallel generation** across multiple processes/machines
3. **Use blob storage** to avoid local storage limitations
4. **Monitor progress carefully** as generation times increase significantly

## 🧪 Testing Your Setup

Always test with a small dataset first:

```bash
# Test with 1K records
python example_4m_generation.py test

# Test with 10K records
python generate_large_dataset.py \
    examples/ClientD_Medicare_Membership.yml \
    test_10k.csv \
    10000
```

## 💡 Tips for Production Use

1. **Set up monitoring**: Track generation progress and system resources
2. **Use environment variables**: Store connection strings securely
3. **Plan for interruptions**: Large generations can take hours
4. **Validate output**: Spot-check generated data for quality
5. **Clean up**: Remove temporary files and failed uploads

## 🔗 Related Files

- `generate_large_dataset.py` - Main memory-efficient generator
- `example_4m_generation.py` - Interactive examples and demos
- `generate_dummy_data.py` - Original generator (for smaller datasets)
- `requirements.txt` - Updated with Azure Blob Storage dependency
