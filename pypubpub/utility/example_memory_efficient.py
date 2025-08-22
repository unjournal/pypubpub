#!/usr/bin/env python3
"""
Example of memory-efficient RePEc metadata processing without temporary files
"""

from ftp_utils import RePECFTPUtility
import json


def example_single_file_processing():
    """Example of processing a single metadata file in memory"""
    print("=== Single File Memory-Efficient Processing ===")
    
    repec_ftp = RePECFTPUtility()
    
    try:
        if repec_ftp.connect():
            print("Connected to RePEc FTP server!")
            
            # Get list of available files
            files = repec_ftp.list_files()
            if not files:
                print("No RDF files found on server")
                return
                
            # Process first available file
            filename = files[0]
            print(f"\nProcessing {filename}...")
            
            # Download, convert, and parse in one operation
            success, content, metadata = repec_ftp.download_and_parse_metadata(
                filename, path=RePECFTPUtility._PATH, target_encoding=RePECFTPUtility._TARGET_ENCODING
            )
            
            if success:
                print(f"✓ Successfully processed {filename}")
                print(f"  Content length: {len(content)} characters")
                print(f"  Metadata fields: {len(metadata)}")
                
                # Display key metadata fields
                print("\n  Key metadata:")
                for key, value in metadata.items():
                    if key in ['Title', 'Author-Name', 'Abstract', 'DOI', 'Handle']:
                        if isinstance(value, list):
                            print(f"    {key}: {value[0]}... (and {len(value)-1} more)")
                        else:
                            print(f"    {key}: {str(value)[:100]}...")
                            
                # Show full metadata structure
                print(f"\n  Full metadata structure:")
                print(json.dumps(metadata, indent=2, ensure_ascii=False)[:500] + "...")
            else:
                print(f"✗ Failed to process {filename}")
                
    finally:
        repec_ftp.disconnect()


def example_batch_processing():
    """Example of batch processing multiple metadata files in memory"""
    print("\n=== Batch Memory-Efficient Processing ===")
    
    repec_ftp = RePECFTPUtility()
    
    try:
        if repec_ftp.connect():
            print("Connected to RePEc FTP server!")
            
            # Process multiple files efficiently
            print("Processing multiple metadata files...")
            
            results = repec_ftp.download_multiple_metadata_files()
            
            print(f"\nProcessed {len(results)} files:")
            
            successful_count = 0
            total_metadata_fields = 0
            
            for filename, content, metadata, success in results:
                if success:
                    successful_count += 1
                    total_metadata_fields += len(metadata)
                    
                    # Extract key information
                    title = metadata.get('Title', 'No title')
                    authors = metadata.get('Author-Name', [])
                    if isinstance(authors, str):
                        authors = [authors]
                    
                    print(f"  ✓ {filename}")
                    print(f"    Title: {str(title)[:80]}...")
                    print(f"    Authors: {len(authors)} author(s)")
                    print(f"    Fields: {len(metadata)} metadata fields")
                else:
                    print(f"  ✗ {filename}: Failed")
                    
            print(f"\nSummary:")
            print(f"  Total files: {len(results)}")
            print(f"  Successful: {successful_count}")
            print(f"  Failed: {len(results) - successful_count}")
            print(f"  Total metadata fields: {total_metadata_fields}")
            
    finally:
        repec_ftp.disconnect()


def example_encoding_workflow():
    """Example of the complete encoding workflow in memory"""
    print("\n=== Complete Encoding Workflow in Memory ===")
    
    repec_ftp = RePECFTPUtility()
    
    try:
        if repec_ftp.connect():
            print("Connected to RePEc FTP server!")
            
            files = repec_ftp.list_files()
            if not files:
                print("No RDF files found on server")
                return
                
            filename = files[0]
            print(f"Demonstrating encoding workflow for {filename}")
            
            # Step 1: Download to bytes
            print("\n1. Downloading to bytes...")
            success, content_bytes = repec_ftp.download_file_to_bytes(filename,path=RePECFTPUtility._PATH )
            
            if not success:
                print("Failed to download file")
                return
                
            print(f"   Downloaded {len(content_bytes)} bytes")
            
            # Step 2: Detect encoding
            print("\n2. Detecting encoding...")
            detected_encoding = repec_ftp.detect_bytes_encoding(content_bytes)
            print(f"   Detected encoding: {detected_encoding}")
            
            # Step 3: Convert to string
            print("\n3. Converting to string...")
            content_string = repec_ftp.convert_bytes_to_string(
                content_bytes
            )
            print(f"   Converted to string: {len(content_string)} characters")
            print(f"   Preview: {content_string[:200]}...")
            
            # Step 4: Parse metadata
            print("\n4. Parsing metadata...")
            metadata = repec_ftp.parse_repec_metadata(content_string)
            print(f"   Parsed {len(metadata)} metadata fields")
            
            # Show sample metadata
            print("\n   Sample metadata:")
            for i, (key, value) in enumerate(metadata.items()):
                if i >= 5:  # Show first 5 fields
                    break
                print(f"     {key}: {str(value)[:50]}...")
                
    finally:
        repec_ftp.disconnect()


def example_error_handling():
    """Example of error handling in memory-efficient workflow"""
    print("\n=== Error Handling in Memory-Efficient Workflow ===")
    
    repec_ftp = RePECFTPUtility()
    
    try:
        if repec_ftp.connect():
            print("Connected to RePEc FTP server!")
            
            # Test with non-existent file
            print("\n1. Testing with non-existent file...")
            success, content, metadata = repec_ftp.download_and_parse_metadata(
                "non_existent_file.rdf", RePECFTPUtility.path, "utf-8"
            )
            
            print(f"   Success: {success}")
            print(f"   Content length: {len(content)}")
            print(f"   Metadata fields: {len(metadata)}")
            
            # Test encoding fallbacks
            print("\n2. Testing encoding fallbacks...")
            
            # Create test bytes with mixed encoding
            test_bytes = b"Hello World! " + "Café résumé".encode('iso-8859-1')
            
            # Try to convert with wrong encoding first
            print("   Testing UTF-8 conversion (should trigger fallback)...")
            content = repec_ftp.convert_bytes_to_string(
                test_bytes
            )
            print(f"   Result: {len(content)} characters")
            print(f"   Preview: {content[:50]}...")
            
    finally:
        repec_ftp.disconnect()


if __name__ == "__main__":
    print("RePEc FTP Utility - Memory-Efficient Processing Examples")
    print("Demonstrating workflow without temporary files")
    print()
    
    try:
        example_single_file_processing()
    except Exception as e:
        print(f"Single file processing example failed (expected): {e}")
    
    try:
        example_batch_processing()
    except Exception as e:
        print(f"Batch processing example failed (expected): {e}")
    
    try:
        example_encoding_workflow()
    except Exception as e:
        print(f"Encoding workflow example failed (expected): {e}")
    
    try:
        example_error_handling()
    except Exception as e:
        print(f"Error handling example failed (expected): {e}")
    
    print("\nExamples completed. Check the code to see the memory-efficient API usage patterns.")
