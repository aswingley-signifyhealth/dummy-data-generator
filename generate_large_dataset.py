#!/usr/bin/env python3
"""
Memory-efficient generator for large datasets with direct blob storage upload.
Processes data in chunks to minimize memory usage and local storage requirements.
"""

import csv
import io
import os
import random
import re
import string
import sys
import tempfile
import time
from datetime import datetime, timezone
from typing import Iterator, Dict, Any, Optional

import yaml
from faker import Faker
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceExistsError

from utils import generate_medicaid_id, get_supported_states


class MemoryEfficientDataGenerator:
    """
    Generates large datasets in memory-efficient chunks with direct cloud upload capability.
    """
    
    def __init__(self, yaml_config_path: str, chunk_size: int = 10000):
        """
        Initialize the generator.
        
        Args:
            yaml_config_path: Path to YAML configuration file
            chunk_size: Number of records to process in each chunk (affects memory usage)
        """
        self.yaml_config_path = yaml_config_path
        self.chunk_size = chunk_size
        self.fake = Faker()
        
        # Load configuration
        with open(yaml_config_path, 'r') as file:
            self.config = yaml.safe_load(file)
        
        self.columns = list(self.config['columns'].keys())
        
    def generate_medicare_id(self) -> str:
        """Generate a valid Medicare ID."""
        letters = ''.join(set(string.ascii_uppercase) - set('SLOIBZ'))
        numbers = '123456789'
        
        medicare_id = [
            random.choice(numbers),  # 1st character
            random.choice(letters),  # 2nd character
            random.choice(numbers),  # 3rd character
            random.choice(numbers),  # 4th character
            random.choice(letters),  # 5th character
            random.choice(numbers),  # 6th character
            random.choice(numbers),  # 7th character
            random.choice(letters),  # 8th character
            random.choice(letters),  # 9th character
            random.choice(numbers),  # 10th character
            random.choice(numbers)   # 11th character
        ]
        
        return ''.join(medicare_id)
    
    def get_supported_state(self) -> str:
        """Get a random supported state."""
        return random.choice(get_supported_states())
    
    def generate_member_id(self) -> str:
        """Generate a member ID."""
        prefix = "MEMB"
        number = ''.join(random.choices('0123456789', k=11))
        return f"{prefix}{number}"
    
    def generate_name_details(self, gender: str) -> Dict[str, str]:
        """Generate name details based on gender."""
        if gender == "1":
            full_name = self.fake.name_male()
            prefix = self.fake.prefix_male()
            suffix = self.fake.suffix_male()
        else:
            full_name = self.fake.name_female()
            prefix = self.fake.prefix_female()
            suffix = self.fake.suffix_female()
        
        name_parts = full_name.split()
        return {
            "first_name": name_parts[0],
            "middle_name": name_parts[1] if len(name_parts) > 2 else "",
            "last_name": name_parts[-1],
            "prefix": prefix,
            "suffix": suffix,
            "full_name": full_name
        }
    
    def generate_single_record(self) -> Dict[str, str]:
        """Generate a single membership record."""
        state = self.get_supported_state()
        gender = self.fake.random_element(elements=("1", "2"))
        name_details = self.generate_name_details(gender)
        dob = self.fake.date_of_birth(minimum_age=18, maximum_age=98)
        
        record = {}
        
        for column in self.columns:
            column_lower = column.lower()
            
            if 'date' in column_lower and 'birth' in column_lower or 'dob' in column_lower:
                record[column] = dob.strftime("%Y%m%d")
            elif 'date' in column_lower and 'death' in column_lower:
                age = (datetime.now().date() - dob).days // 365
                if age > 95:
                    death_date = dob.replace(year=dob.year + random.randint(70, 95))
                    record[column] = death_date.strftime('%Y%m%d')
                else:
                    if random.random() < 0.2:
                        death_date = dob.replace(year=dob.year + random.randint(70, 95))
                        record[column] = death_date.strftime('%Y%m%d')
                    else:
                        record[column] = ''
            elif 'email' in column_lower:
                record[column] = self.fake.email()
            elif 'phone' in column_lower:
                record[column] = self.fake.phone_number()
            elif 'name' in column_lower and 'first' in column_lower:
                record[column] = name_details['first_name']
            elif 'name' in column_lower and 'last' in column_lower:
                record[column] = name_details['last_name']
            elif 'name' in column_lower and 'middle' in column_lower:
                record[column] = name_details['middle_name']
            elif 'name' in column_lower and 'prefix' in column_lower:
                record[column] = name_details['prefix']
            elif 'name' in column_lower and 'suffix' in column_lower:
                record[column] = name_details['suffix']
            elif 'name' in column_lower and 'preferred' in column_lower:
                record[column] = name_details['full_name']
            elif 'address' in column_lower:
                record[column] = self.fake.street_address()
            elif 'city' in column_lower:
                record[column] = self.fake.city()
            elif 'state' in column_lower:
                record[column] = state
            elif 'zip' in column_lower:
                record[column] = self.fake.zipcode()
            elif 'country' in column_lower:
                record[column] = self.fake.country_code()
            elif 'gender' in column_lower:
                record[column] = gender
            elif 'ethnicity' in column_lower:
                record[column] = self.fake.random_element(elements=(
                    "Hispanic", "Caucasian", "African American", "Asian", 
                    "Not Provided", "", "American Indian", "Pacific Islander"
                ))
            elif 'race' in column_lower:
                record[column] = self.fake.random_element(elements=(
                    "White (Non-Hispanic)", "Black or African American", 
                    "Asian or Pacific Islander", "Other"
                ))
            elif 'language' in column_lower:
                record[column] = self.fake.random_element(elements=(
                    "English", "Spanish", "Vietnamese", "Russian", "Chinese Cantonese",
                    "Khmer", "Korean", "Arabic", "Persian", "Hmong", "French", "German"
                ))
            elif 'relationship' in column_lower:
                record[column] = self.fake.random_element(elements=("Self", "Spouse", "Child"))
            elif 'marital' in column_lower:
                record[column] = self.fake.random_element(elements=(
                    "Single", "Married", "Divorced", "Widowed"
                ))
            elif 'medicare' in column_lower:
                record[column] = self.generate_medicare_id()
            elif 'medicaid' in column_lower:
                record[column] = generate_medicaid_id(state)
            elif 'memberid' in column_lower or 'member_id' in column_lower:
                record[column] = self.generate_member_id()
            else:
                record[column] = self.fake.uuid4()
        
        return record
    
    def generate_chunk(self, chunk_size: int) -> Iterator[Dict[str, str]]:
        """Generate a chunk of records."""
        for _ in range(chunk_size):
            yield self.generate_single_record()
    
    def generate_to_local_file(self, total_records: int, output_file: str, 
                              progress_callback: Optional[callable] = None) -> str:
        """
        Generate data directly to a local CSV file in chunks.
        
        Args:
            total_records: Total number of records to generate
            output_file: Output file path
            progress_callback: Optional callback function for progress updates
            
        Returns:
            Path to the generated file
        """
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        
        # Add timestamp to filename
        if output_file.endswith('.csv'):
            base_name = output_file[:-4]
            final_output = f"{base_name}_{timestamp}.csv"
        else:
            final_output = f"{output_file}_{timestamp}.csv"
        
        records_written = 0
        start_time = time.time()
        
        with open(final_output, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.columns)
            writer.writeheader()
            
            while records_written < total_records:
                remaining = total_records - records_written
                current_chunk_size = min(self.chunk_size, remaining)
                
                # Generate and write chunk
                for record in self.generate_chunk(current_chunk_size):
                    writer.writerow(record)
                    records_written += 1
                
                # Progress callback
                if progress_callback:
                    elapsed = time.time() - start_time
                    progress_callback(records_written, total_records, elapsed)
        
        return final_output
    
    def generate_to_blob_storage(self, total_records: int, 
                                connection_string: str, 
                                container_name: str, 
                                blob_name: str,
                                progress_callback: Optional[callable] = None) -> str:
        """
        Generate data and upload directly to Azure Blob Storage using a temporary file.
        This approach minimizes memory usage while still providing efficient blob upload.
        
        Args:
            total_records: Total number of records to generate
            connection_string: Azure Storage connection string
            container_name: Blob container name
            blob_name: Blob name (will add timestamp)
            progress_callback: Optional callback function for progress updates
            
        Returns:
            Final blob name with timestamp
        """
        # Initialize blob client
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        
        # Add timestamp to blob name
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        if blob_name.endswith('.csv'):
            base_name = blob_name[:-4]
            final_blob_name = f"{base_name}_{timestamp}.csv"
        else:
            final_blob_name = f"{blob_name}_{timestamp}.csv"
        
        # Create container if it doesn't exist
        try:
            blob_service_client.create_container(container_name)
        except ResourceExistsError:
            pass
        
        blob_client = blob_service_client.get_blob_client(
            container=container_name, 
            blob=final_blob_name
        )
        
        records_written = 0
        start_time = time.time()
        
        # Use a temporary file to generate data, then upload
        with tempfile.NamedTemporaryFile(mode='w+', newline='', encoding='utf-8', delete=False) as temp_file:
            temp_path = temp_file.name
            
            try:
                # Write CSV data to temporary file
                writer = csv.DictWriter(temp_file, fieldnames=self.columns)
                writer.writeheader()
                
                # Process data in chunks
                while records_written < total_records:
                    remaining = total_records - records_written
                    current_chunk_size = min(self.chunk_size, remaining)
                    
                    # Generate chunk and write to temp file
                    for record in self.generate_chunk(current_chunk_size):
                        writer.writerow(record)
                        records_written += 1
                    
                    # Flush to ensure data is written
                    temp_file.flush()
                    
                    # Progress callback
                    if progress_callback:
                        elapsed = time.time() - start_time
                        progress_callback(records_written, total_records, elapsed)
                
                # Close the file before uploading
                temp_file.close()
                
                # Upload the complete file to blob storage
                with open(temp_path, 'rb') as upload_file:
                    blob_client.upload_blob(upload_file, overwrite=True)
                
            finally:
                # Clean up temp file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
        
        return final_blob_name


def format_progress(current: int, total: int, elapsed_time: float):
    """Format progress information."""
    percentage = (current / total) * 100
    rate = current / elapsed_time if elapsed_time > 0 else 0
    eta = (total - current) / rate if rate > 0 else 0
    
    print(f"\rProgress: {current:,}/{total:,} ({percentage:.1f}%) | "
          f"Rate: {rate:.0f} records/sec | "
          f"ETA: {eta/60:.1f} min | "
          f"Elapsed: {elapsed_time/60:.1f} min", end='', flush=True)


def main():
    """Main execution function."""
    if len(sys.argv) < 4:
        print("Usage:")
        print("  Local file: python generate_large_dataset.py <yaml_file> <output_file> <num_records>")
        print("  Blob storage: python generate_large_dataset.py <yaml_file> blob <num_records> <connection_string> <container> <blob_name>")
        print("\nExample:")
        print("  python generate_large_dataset.py examples/ClientD_Medicare_Membership.yml membership_4m.csv 4000000")
        return
    
    yaml_file = sys.argv[1]
    output_type = sys.argv[2]
    num_records = int(sys.argv[3])
    
    # Initialize generator with appropriate chunk size
    # Smaller chunks for very large datasets to minimize memory usage
    chunk_size = min(10000, max(1000, num_records // 1000))
    generator = MemoryEfficientDataGenerator(yaml_file, chunk_size=chunk_size)
    
    print(f"Generating {num_records:,} records using chunk size of {chunk_size:,}")
    print(f"Estimated memory usage: ~{(chunk_size * 0.8 / 1024):.1f} MB per chunk")
    
    if output_type.lower() == 'blob':
        if len(sys.argv) < 7:
            print("Blob storage requires: <connection_string> <container> <blob_name>")
            return
        
        connection_string = sys.argv[4]
        container_name = sys.argv[5]
        blob_name = sys.argv[6]
        
        print(f"Uploading to blob storage: {container_name}/{blob_name}")
        
        final_blob_name = generator.generate_to_blob_storage(
            total_records=num_records,
            connection_string=connection_string,
            container_name=container_name,
            blob_name=blob_name,
            progress_callback=format_progress
        )
        
        print(f"\n✅ Successfully uploaded to blob: {container_name}/{final_blob_name}")
        
    else:
        # Local file generation
        output_file = output_type
        
        print(f"Generating to local file: {output_file}")
        
        final_file = generator.generate_to_local_file(
            total_records=num_records,
            output_file=output_file,
            progress_callback=format_progress
        )
        
        file_size_mb = os.path.getsize(final_file) / (1024 * 1024)
        print(f"\n✅ Successfully generated: {final_file}")
        print(f"📁 File size: {file_size_mb:.1f} MB")


if __name__ == "__main__":
    main()
