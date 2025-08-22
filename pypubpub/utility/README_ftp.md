# FTP Utility Classes

This module provides utility classes for FTP operations, specifically designed for working with RePEc metadata files.

## Classes

### FTPUtility

Base class for general FTP operations.

**Features:**
- Connect/disconnect to FTP servers
- List files with pattern filtering
- Download individual files
- Batch download multiple files
- Get file information (size, modification date)
- Comprehensive error handling and logging

**Usage:**
```python
from pypubpub.utility import FTPUtility

# Create instance
ftp_util = FTPUtility(
    host="ftp.example.com",
    username="user",
    password="pass",
    timeout=30
)

# Connect and use
if ftp_util.connect():
    files = ftp_util.list_files("/", "*.pdf")
    ftp_util.download_file("file.pdf", "local_file.pdf", "/")
    
    # Advanced: Download all files with glob patterns
    results = ftp_util.download_alldir_files(
        remote_dir="/data",
        local_dir="./downloads",
        pattern="*.txt",
        recursive=True,
        exclude_patterns=["*.tmp", "*draft*"]
    )
finally:
    ftp_util.disconnect()
```

### RePECFTPUtility

Specialized class for RePEc.org FTP operations.

**Features:**
- Inherits all functionality from FTPUtility
- Pre-configured for RePEc servers (default: 54.54.54.54)
- Anonymous login by default
- RePEc-specific methods for metadata files

**Usage:**
```python
from pypubpub.utility import RePECFTPUtility

# Create RePEc FTP utility
repec_ftp = RePECFTPUtility()

# Get metadata files
if repec_ftp.connect():
    metadata_files = repec_ftp.get_metadata_files("/zhb", "*.rdf")
    
    # Download all metadata files
    results = repec_ftp.download_metadata_files(
        subdir="/zhb",
        local_dir="./downloads",
        pattern="*.rdf"
    )
finally:
    repec_ftp.disconnect()
```

## Methods

### Connection Management
- `connect()` - Connect to FTP server
- `disconnect()` - Disconnect from FTP server

### File Operations
- `list_files(directory, pattern)` - List files with optional pattern filtering
- `download_file(remote_file, local_file, directory)` - Download single file
- `download_files_by_pattern(directory, pattern, local_dir)` - Batch download files
- `download_alldir_files(remote_dir, local_dir, pattern, recursive, exclude_patterns)` - Download all files using glob patterns
- `get_file_info(filename, directory)` - Get file metadata

### Advanced File Operations
- `download_alldir_files(remote_dir, local_dir, pattern, recursive, exclude_patterns)` - Advanced file downloading with:
  - **Glob pattern matching**: Use patterns like `*.rdf`, `pub-*.rdf`, `[0-9]*.txt`
  - **Recursive directory traversal**: Optionally search subdirectories
  - **Exclusion patterns**: Skip files matching specific patterns
  - **Smart file detection**: Automatically distinguishes files from directories

### RePEc Specific
- `get_metadata_files(subdir, pattern)` - Get RePEc metadata files
- `download_metadata_files(subdir, local_dir, pattern)` - Download RePEc metadata files
- `download_all_metadata_files(subdir, local_dir, pattern, recursive, exclude_patterns)` - Download all RePEc metadata files with glob patterns
- `detect_file_encoding(file_path, sample_size)` - Detect character encoding of downloaded files
- `convert_file_to_string(file_path, target_encoding, source_encoding)` - Convert files to strings with proper encoding
- `download_and_convert_file(remote_file, local_file, directory, target_encoding)` - Download and convert in one operation
- `download_metadata_as_strings(subdir, pattern, target_encoding)` - Download multiple files and return as strings
- `download_file_to_bytes(remote_file, directory)` - Download file directly to memory as bytes
- `convert_bytes_to_string(content_bytes, target_encoding, source_encoding)` - Convert bytes to string with encoding detection
- `detect_bytes_encoding(content_bytes, sample_size)` - Detect encoding from bytes in memory
- `download_and_parse_metadata(remote_file, directory, target_encoding)` - Download, convert, and parse into metadata dictionary
- `parse_repec_metadata(content_string)` - Parse RePEc metadata string into dictionary
- `download_multiple_metadata_files(subdir, pattern, target_encoding)` - Download and parse multiple files into dictionaries

## Error Handling

All methods include comprehensive error handling:
- Connection failures
- Authentication errors
- File access errors
- Network timeouts
- Local file system errors

## Logging

The utility uses Python's logging module to track operations:
- Connection status
- File operations
- Error conditions
- Download progress

## Examples

See `example_ftp_usage.py` for complete usage examples.

## Integration with RePEc Module

The `RePEcParseExisting` class now uses these utilities:

```python
from pypubpub.repec import RePEcParseExisting

parser = RePEcParseExisting("input_dir")

# Get list of metadata files
files = parser.get_metadata_via_ftpserver(
    ftp_server="54.54.54.54",
    subdir="/zhb"
)

# Download files
results = parser.download_metadata_files(
    ftp_server="54.54.54.54",
    subdir="/zhb",
    local_dir="./downloads"
)
```

## Requirements

- Python 3.7+
- Standard library modules: `ftplib`, `os`, `typing`, `logging`
- No external dependencies

## Character Encoding Detection

The `RePECFTPUtility` class includes advanced character encoding detection and conversion capabilities specifically designed for RePEc metadata files, which commonly use ISO-LATIN-1 encoding but may also be UTF-8.

### Memory-Efficient Workflow

For RePEc metadata processing, the utility now supports a memory-efficient workflow that eliminates temporary files:

1. **Download to Memory**: `download_file_to_bytes()` downloads files directly to memory as bytes
2. **Encoding Detection**: `detect_bytes_encoding()` detects encoding from bytes in memory
3. **String Conversion**: `convert_bytes_to_string()` converts bytes to properly encoded strings
4. **Metadata Parsing**: `parse_repec_metadata()` parses strings into structured dictionaries
5. **Combined Operations**: `download_and_parse_metadata()` combines all steps in one call

### Benefits

- **No Temporary Files**: All processing happens in memory
- **Faster Processing**: Eliminates disk I/O overhead
- **Better Integration**: Direct pipeline from FTP to parsed metadata
- **Resource Efficient**: Reduces disk usage and cleanup complexity

### Usage Examples

```python
from pypubpub.utility import RePECFTPUtility

repec_ftp = RePECFTPUtility()

# Memory-efficient single file processing
success, content, metadata = repec_ftp.download_and_parse_metadata(
    "file.rdf", "/zhb", "utf-8"
)

# Process multiple files efficiently
results = repec_ftp.download_multiple_metadata_files(
    subdir="/zhb", pattern="*.rdf", target_encoding="utf-8"
)

for filename, content, metadata, success in results:
    if success:
        print(f"{filename}: {metadata.get('Title', 'No title')}")
```

### Encoding Detection Features

- **Smart Fallback Detection**: Tries UTF-8 first, then falls back to ISO-LATIN-1 and other encodings
- **RePEc-Specific Fallbacks**: Defaults to ISO-LATIN-1 for RePEc files when detection fails
- **Multiple Encoding Support**: Handles ISO-LATIN-1, UTF-8, Windows-1252, and ASCII
- **Robust Error Handling**: Automatic fallback between UTF-8 and ISO-LATIN-1 on encoding errors
- **No External Dependencies**: Uses only Python standard library for encoding detection

### How It Works

1. **Primary Detection**: Tries to decode file samples with common encodings in order of likelihood for RePEc files:
   - ISO-LATIN-1 (most common for RePEc files)
   - UTF-8 (modern encoding, but less common for RePEc)
   - Windows-1252 (Windows-specific Latin)
   - ASCII (basic 7-bit encoding)

2. **Smart Fallbacks**: If the primary encoding fails during conversion:
   - If UTF-8 fails → automatically tries ISO-LATIN-1 first
   - If ISO-LATIN-1 fails → automatically tries UTF-8 second
   - Always prioritizes ISO-LATIN-1 as the primary fallback for RePEc files

3. **Final Fallback**: If all encodings fail, uses binary read with UTF-8 replacement characters

### Supported Encodings

- **ISO-LATIN-1** (`iso-8859-1`) - Common for RePEc files
- **UTF-8** (`utf-8`) - Modern Unicode encoding
- **Windows-1252** (`windows-1252`) - Windows-specific Latin encoding
- **ASCII** (`ascii`) - Basic 7-bit encoding
- **Auto-detected** - Any encoding detected by chardet

### Usage Examples

```python
from pypubpub.utility import RePECFTPUtility

repec_ftp = RePECFTPUtility()

# Detect encoding of downloaded file
encoding = repec_ftp.detect_file_encoding("downloaded_file.rdf")
print(f"Detected encoding: {encoding}")

# Convert to UTF-8 string
content = repec_ftp.convert_file_to_string("file.rdf", target_encoding='utf-8')

# Download and convert in one operation
success, content = repec_ftp.download_and_convert_file(
    "remote_file.rdf", "local_file.rdf", "/zhb", "utf-8"
)

# Batch download and convert multiple files
results = repec_ftp.download_metadata_as_strings(
    subdir="/zhb", pattern="*.rdf", target_encoding='utf-8'
)
```

## Glob Pattern Syntax

The `download_alldir_files` method supports standard glob patterns for file matching:

### Basic Patterns
- `*` - Matches any sequence of characters
- `?` - Matches any single character
- `[abc]` - Matches any character in the set
- `[a-z]` - Matches any character in the range
- `[!abc]` - Matches any character NOT in the set

### Examples
- `*.rdf` - All files ending with .rdf
- `pub-*.rdf` - Files starting with "pub-" and ending with .rdf
- `[0-9]*.txt` - Files starting with a digit and ending with .txt
- `pub-{2023,2024}*.rdf` - Files starting with "pub-2023" or "pub-2024"
- `*.{rdf,txt,md}` - Files with multiple extensions

### Exclusion Patterns
Use `exclude_patterns` to skip unwanted files:
```python
exclude_patterns=["*.tmp", "*draft*", "*test*", "*.bak"]
```
