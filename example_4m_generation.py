#!/usr/bin/env python3
"""
Example script demonstrating how to generate 4 million membership records
efficiently with minimal memory usage and direct blob storage upload.
"""

import os
import sys
from generate_large_dataset import MemoryEfficientDataGenerator, format_progress


def example_local_generation():
    """Example: Generate 4M records to local file."""
    print("🚀 Example: Generating 4M records to local file")
    print("=" * 50)
    
    # Configuration
    yaml_file = "examples/ClientD_Medicare_Membership.yml"
    output_file = "membership_4million.csv"
    num_records = 4_000_000
    
    # Use smaller chunk size for memory efficiency
    chunk_size = 5000  # ~4MB per chunk
    
    generator = MemoryEfficientDataGenerator(yaml_file, chunk_size=chunk_size)
    
    print(f"📊 Configuration:")
    print(f"   Records: {num_records:,}")
    print(f"   Chunk size: {chunk_size:,}")
    print(f"   Estimated memory per chunk: ~{(chunk_size * 0.8 / 1024):.1f} MB")
    print(f"   Estimated final file size: ~{(num_records * 0.8 / 1024):.0f} MB")
    print()
    
    try:
        final_file = generator.generate_to_local_file(
            total_records=num_records,
            output_file=output_file,
            progress_callback=format_progress
        )
        
        file_size_mb = os.path.getsize(final_file) / (1024 * 1024)
        print(f"\n✅ Success! Generated: {final_file}")
        print(f"📁 File size: {file_size_mb:.1f} MB")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")


def example_blob_generation():
    """Example: Generate 4M records directly to Azure Blob Storage."""
    print("☁️  Example: Generating 4M records to Azure Blob Storage")
    print("=" * 60)
    
    # Configuration - you'll need to set these environment variables
    connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    if not connection_string:
        print("❌ Please set AZURE_STORAGE_CONNECTION_STRING environment variable")
        print("   Example: export AZURE_STORAGE_CONNECTION_STRING='DefaultEndpointsProtocol=https;...'")
        return
    
    yaml_file = "examples/ClientD_Medicare_Membership.yml"
    container_name = "membership-data"
    blob_name = "membership_4million.csv"
    num_records = 4_000_000
    
    # Smaller chunk size for blob uploads
    chunk_size = 2500  # ~2MB per chunk for better upload performance
    
    generator = MemoryEfficientDataGenerator(yaml_file, chunk_size=chunk_size)
    
    print(f"📊 Configuration:")
    print(f"   Records: {num_records:,}")
    print(f"   Chunk size: {chunk_size:,}")
    print(f"   Container: {container_name}")
    print(f"   Blob: {blob_name}")
    print(f"   Estimated memory per chunk: ~{(chunk_size * 0.8 / 1024):.1f} MB")
    print()
    
    try:
        final_blob_name = generator.generate_to_blob_storage(
            total_records=num_records,
            connection_string=connection_string,
            container_name=container_name,
            blob_name=blob_name,
            progress_callback=format_progress
        )
        
        print(f"\n✅ Success! Uploaded to blob: {container_name}/{final_blob_name}")
        print("🌐 No local storage used!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")


def example_test_run():
    """Example: Small test run to verify everything works."""
    print("🧪 Example: Test run with 1000 records")
    print("=" * 40)
    
    yaml_file = "examples/ClientD_Medicare_Membership.yml"
    output_file = "test_membership.csv"
    num_records = 1000
    
    generator = MemoryEfficientDataGenerator(yaml_file, chunk_size=500)
    
    try:
        final_file = generator.generate_to_local_file(
            total_records=num_records,
            output_file=output_file,
            progress_callback=format_progress
        )
        
        file_size_kb = os.path.getsize(final_file) / 1024
        print(f"\n✅ Test successful! Generated: {final_file}")
        print(f"📁 File size: {file_size_kb:.1f} KB")
        print("🎯 Ready for large-scale generation!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")


def main():
    """Main function with example selection."""
    if len(sys.argv) > 1:
        example_type = sys.argv[1].lower()
    else:
        print("Choose an example:")
        print("1. test     - Generate 1K records (test)")
        print("2. local    - Generate 4M records to local file")
        print("3. blob     - Generate 4M records to Azure Blob Storage")
        print()
        choice = input("Enter choice (1-3): ").strip()
        
        if choice == "1":
            example_type = "test"
        elif choice == "2":
            example_type = "local"
        elif choice == "3":
            example_type = "blob"
        else:
            print("Invalid choice")
            return
    
    if example_type == "test":
        example_test_run()
    elif example_type == "local":
        example_local_generation()
    elif example_type == "blob":
        example_blob_generation()
    else:
        print("Usage: python example_4m_generation.py [test|local|blob]")


if __name__ == "__main__":
    main()
