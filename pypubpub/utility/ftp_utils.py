"""FTP utility functions for downloading and managing RePEc metadata files"""

import os
import glob
from ftplib import FTP, error_perm, error_temp
import re
from typing import List, Optional, Tuple, Union
import logging

logger = logging.getLogger(__name__)


class FTPUtility:
    """Utility class for FTP operations, specifically designed for RePEc metadata files"""
    
    def __init__(self, host: str, username: str = "", password: str = "", timeout: int = 30):
        """
        Initialize FTP utility
        
        Args:
            host: FTP server hostname or IP
            username: FTP username (empty string for anonymous)
            password: FTP password (empty string for anonymous)
            timeout: Connection timeout in seconds
        """
        self.host = host
        self.username = username
        self.password = password
        self.timeout = timeout
        self.ftp: Optional[FTP] = None
        
    def connect(self) -> bool:
        """
        Connect to FTP server
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.ftp = FTP(host=self.host, timeout=self.timeout)
            self.ftp.login(user=self.username, passwd=self.password)
            logger.info(f"Successfully connected to FTP server {self.host}")
            return True
        except (error_perm, error_temp, ConnectionRefusedError, OSError) as e:
            logger.error(f"Failed to connect to FTP server {self.host}: {e}")
            return False
            
    def disconnect(self):
        """Disconnect from FTP server"""
        if self.ftp:
            try:
                self.ftp.quit()
                logger.info(f"Disconnected from FTP server {self.host}")
            except Exception as e:
                logger.warning(f"Error during FTP disconnect: {e}")
            finally:
                self.ftp = None
                
    def list_files(self) -> List[str]:
        """
        List files in a directory
        
        Args:
            directory: Directory path to list
            pattern: Optional file pattern filter (e.g., "*.rdf")
            
        Returns:
            List of filenames
        """
        if not self.ftp:
            logger.error("Not connected to FTP server")
            return []
            
        try:
            self.ftp.cwd(self.path)
            files = self.ftp.nlst()
            
            if self.file_pattern:
                if self.file_pattern.startswith("*."):
                    extension = self.file_pattern[1:]  # Remove "*"
                    files = [f for f in files if f.endswith(extension)]
                else:
                    # Simple pattern matching
                    files = [f for f in files if self.file_pattern in f]
                    
            logger.info(f"Found {len(files)} files in {self.path}")
            return files
            
        except (error_perm, error_temp) as e:
            logger.error(f"Error listing directory {self.path}: {e}")
            return []
            
    def download_file(self, remote_file: str, local_file: str, directory: str = "/") -> bool:
        """
        Download a file from FTP server
        
        Args:
            remote_file: Name of file on FTP server
            local_file: Local path to save file
            directory: Remote directory containing the file
            
        Returns:
            True if download successful, False otherwise
        """
        if not self.ftp:
            logger.error("Not connected to FTP server")
            return False
            
        try:
            self.ftp.cwd(directory)
            
            local_dir = os.path.dirname(local_file)
            if local_dir and not os.path.exists(local_dir):
                os.makedirs(local_dir)
                # logger.error(F"Directory not found on FTP server: {local_dir}")
                # return False

                
            with open(local_file, 'wb') as f:
                self.ftp.retrbinary(f"RETR {remote_file}", f.write)
                
            logger.info(f"Successfully downloaded {remote_file} to {local_file}")
            return True
            
        except (error_perm, error_temp, OSError) as e:
            logger.error(f"Error downloading {remote_file}: {e}")
            return False
            
    def download_files_by_pattern(self, path: str, file_pattern: str, local_dir: str) -> List[Tuple[str, bool]]:
        """
        Download multiple files matching a pattern
        
        Args:
            directory: Remote directory to search
            pattern: File pattern (e.g., "*.rdf")
            local_dir: Local directory to save files
            
        Returns:
            List of tuples (filename, success_status)
        """
        self.path=path
        self.file_pattern=file_pattern
        files = self.list_files()
        results = []
        
        for filename in files:
            local_file = os.path.join(local_dir, filename)
            success = self.download_file(filename, local_file, path)
            results.append((filename, success))
            
        return results
        
    def download_alldir_files(self, remote_dir: str, local_dir: str, pattern: str = "*", 
                             recursive: bool = False, exclude_patterns: List[str] = None) -> List[Tuple[str, bool]]:
        """
        Download all files in a subdirectory using glob pattern matching
        
        Args:
            remote_dir: Remote directory to search
            local_dir: Local directory to save files
            pattern: Glob pattern to match files (default: "*" for all files)
            recursive: Whether to search subdirectories recursively
            exclude_patterns: List of patterns to exclude from download
            
        Returns:
            List of tuples (filename, success_status)
        """
        if not self.ftp:
            logger.error("Not connected to FTP server")
            return []
            
        try:
            # Change to remote directory
            self.ftp.cwd(remote_dir)
            
            # Get all files and directories
            all_items = self.ftp.nlst()
            files_to_download = []
            
            # Filter items based on pattern and type
            for item in all_items:
                # Check if item matches the glob pattern
                if not glob.fnmatch.fnmatch(item, pattern):
                    continue
                    
                # Check if item should be excluded
                if exclude_patterns:
                    if any(glob.fnmatch.fnmatch(item, exclude_pattern) for exclude_pattern in exclude_patterns):
                        continue
                
                # Determine if item is a file or directory
                try:
                    # Try to get file size - if it fails, it's likely a directory
                    size = self.ftp.size(item)
                    if size is not None:
                        files_to_download.append((item, False))  # False = not recursive
                except (error_perm, error_temp):
                    # Item is likely a directory
                    if recursive:
                        # Recursively process subdirectory
                        sub_remote_dir = f"{remote_dir}/{item}".replace("//", "/")
                        sub_local_dir = os.path.join(local_dir, item)
                        
                        # Create local subdirectory
                        if not os.path.exists(sub_local_dir):
                            os.makedirs(sub_local_dir)
                            
                        # Recursively download files in subdirectory
                        sub_results = self.download_alldir_files(
                            sub_remote_dir, sub_local_dir, pattern, recursive, exclude_patterns
                        )
                        files_to_download.extend(sub_results)
            
            # Download the files
            results = []
            for filename, is_recursive_result in files_to_download:
                if is_recursive_result:
                    # This is a result from recursive call, just add it
                    results.append((filename, True))
                else:
                    # Download this file
                    local_file = os.path.join(local_dir, filename)
                    success = self.download_file(filename, local_file, remote_dir)
                    results.append((filename, success))
                    
            logger.info(f"Downloaded {len([r for r in results if r[1]])} files from {remote_dir}")
            return results
            
        except (error_perm, error_temp) as e:
            logger.error(f"Error accessing directory {remote_dir}: {e}")
            return []
        
    def get_file_info(self, filename: str, directory: str = "/") -> Optional[dict]:
        """
        Get information about a file
        
        Args:
            filename: Name of the file
            directory: Directory containing the file
            
        Returns:
            Dictionary with file information or None if error
        """
        if not self.ftp:
            logger.error("Not connected to FTP server")
            return None
            
        try:
            self.ftp.cwd(directory)
            size = self.ftp.size(filename)
            modified = self.ftp.voidcmd(f"MDTM {filename}")[4:].strip()
            
            return {
                "filename": filename,
                "size": size,
                "modified": modified,
                "directory": directory
            }
        except (error_perm, error_temp) as e:
            logger.error(f"Error getting file info for {filename}: {e}")
            return None


class RePECFTPUtility(FTPUtility):
    """Specialized FTP utility for RePEc metadata files"""

    _PATH="/RePEc/bjn/evalua"
    _FILE_PATTERN="*.rdf"
    _HOST="45.79.160.157"
    _TIMEOUT=30
    _TARGET_ENCODING: str = 'iso-8859-1'
    _SOURCE_ENCODING: str = 'utf-8'
    
    def __init__(self, host: str = _HOST, path=_PATH,  file_pattern: str = _FILE_PATTERN, timeout: int = _TIMEOUT, source_encoding: str = _SOURCE_ENCODING, target_encoding: str = _TARGET_ENCODING):
        """
        Initialize RePEc FTP utility with default anonymous login
        
        Args:
            host: RePEc FTP server hostname or IP
            timeout: Connection timeout in seconds
        """
        self.host = host
        self.path = path
        self.timeout = timeout
        self.file_pattern = file_pattern
        self.source_encoding = source_encoding
        self.target_encoding = target_encoding
        print("STARTING::::",self.host,self.path,self.file_pattern)
        super().__init__(host=self.host, username="", password="", timeout=self.timeout)
        
    def get_metadata_files_names(self) -> List[str]:
        """
        Get list of RePEc metadata files
        
        Args:
            subdir: Subdirectory to search
            pattern: File pattern to match
            
        Returns:
            List of metadata filenames
        """
        return self.list_files()
        
    def download_metadata_files(self, subdir: str = "/zhb", local_dir: str = ".", pattern: str = "*.rdf") -> List[Tuple[str, bool]]:
        """
        Download RePEc metadata files
        
        Args:
            subdir: Remote subdirectory
            local_dir: Local directory to save files
            pattern: File pattern to match
            
        Returns:
            List of tuples (filename, success_status)
        """
        return self.download_files_by_pattern(subdir, pattern, local_dir)
        
    def download_all_metadata_files(self, subdir: str = "/zhb", local_dir: str = ".", 
                                   pattern: str = "*.rdf", recursive: bool = False, 
                                   exclude_patterns: List[str] = None) -> List[Tuple[str, bool]]:
        """
        Download all RePEc metadata files in a directory using glob pattern matching
        
        Args:
            subdir: Remote subdirectory
            local_dir: Local directory to save files
            pattern: Glob pattern to match files (default: "*.rdf")
            recursive: Whether to search subdirectories recursively
            exclude_patterns: List of patterns to exclude from download
            
        Returns:
            List of tuples (filename, success_status)
        """
        return self.download_alldir_files(subdir, local_dir, pattern, recursive, exclude_patterns)
        
    def detect_file_encoding(self, file_path: str, sample_size: int = 10000) -> str:
        """
        Detect the character encoding of a downloaded file
        
        Args:
            file_path: Path to the local file
            sample_size: Number of bytes to sample for encoding detection
            
        Returns:
            Detected encoding (e.g., 'utf-8', 'iso-8859-1', 'windows-1252')
        """
        try:
            with open(file_path, 'rb') as f:
                # Read a sample of the file for encoding detection
                sample = f.read(sample_size)
                
            # Try ISO-LATIN-1 first (common for RePEc files)
            try:
                sample.decode('iso-8859-1')
                logger.info("Detected encoding: iso-8859-1 (successful decode)")
                return 'iso-8859-1'
            except UnicodeDecodeError:
                pass
                
            # Try UTF-8 second (modern encoding, but less common for RePEc)
            try:
                sample.decode('utf-8')
                logger.info("Detected encoding: utf-8 (successful decode)")
                return 'utf-8'
            except UnicodeDecodeError:
                pass
                
            # Try Windows-1252 (Windows-specific Latin encoding)
            try:
                sample.decode('windows-1252')
                logger.info("Detected encoding: windows-1252 (successful decode)")
                return 'windows-1252'
            except UnicodeDecodeError:
                pass
                
            # Try ASCII (basic 7-bit encoding)
            try:
                sample.decode('ascii')
                logger.info("Detected encoding: ascii (successful decode)")
                return 'ascii'
            except UnicodeDecodeError:
                pass
                
            # If all common encodings fail, default to ISO-LATIN-1 for RePEc files
            logger.warning("All common encodings failed, defaulting to ISO-LATIN-1")
            return 'iso-8859-1'
                
        except Exception as e:
            logger.error(f"Error detecting encoding for {file_path}: {e}")
            # Default to ISO-LATIN-1 for RePEc files
            return 'iso-8859-1'
            
    def convert_file_to_string(self, file_path: str, target_encoding: str = 'utf-8', 
                              source_encoding: str = None) -> str:
        """
        Convert a downloaded file to a string with proper encoding
        
        Args:
            file_path: Path to the local file
            target_encoding: Desired output encoding (default: utf-8)
            source_encoding: Source encoding (if None, will auto-detect)
            
        Returns:
            File content as a properly encoded string
        """
        try:
            # Auto-detect source encoding if not provided
            if source_encoding is None:
                source_encoding = self.detect_file_encoding(file_path)
                
            # Try to read with detected encoding
            try:
                with open(file_path, 'r', encoding=source_encoding, errors='replace') as f:
                    content = f.read()
                    
                # Convert to target encoding if different
                if source_encoding.lower() != target_encoding.lower():
                    # First decode to unicode, then encode to target
                    if isinstance(content, bytes):
                        content = content.decode(source_encoding, errors='replace')
                    content = content.encode(target_encoding, errors='replace').decode(target_encoding)
                    
                logger.info(f"Successfully converted {file_path} from {source_encoding} to {target_encoding}")
                return content
                
            except (UnicodeDecodeError, UnicodeEncodeError) as encoding_error:
                logger.warning(f"Encoding error with {source_encoding}: {encoding_error}")
                
                # Fallback: try alternative encodings
                fallback_encodings = []
                
                # If source was UTF-8, try ISO-LATIN-1 first (more common for RePEc)
                if source_encoding.lower() in ['utf-8', 'utf8']:
                    fallback_encodings.append('iso-8859-1')
                # If source was ISO-LATIN-1, try UTF-8 second
                elif source_encoding.lower() in ['iso-8859-1', 'latin1', 'latin-1']:
                    fallback_encodings.append('utf-8')
                # Always try ISO-LATIN-1 first, then UTF-8 for RePEc files
                else:
                    fallback_encodings.extend(['iso-8859-1', 'utf-8'])
                
                # Try fallback encodings
                for fallback_encoding in fallback_encodings:
                    try:
                        logger.info(f"Trying fallback encoding: {fallback_encoding}")
                        with open(file_path, 'r', encoding=fallback_encoding, errors='replace') as f:
                            content = f.read()
                            
                        # Convert to target encoding
                        if fallback_encoding.lower() != target_encoding.lower():
                            if isinstance(content, bytes):
                                content = content.decode(fallback_encoding, errors='replace')
                            content = content.encode(target_encoding, errors='replace').decode(target_encoding)
                            
                        logger.info(f"Successfully converted {file_path} using fallback {fallback_encoding} to {target_encoding}")
                        return content
                        
                    except (UnicodeDecodeError, UnicodeEncodeError) as fallback_error:
                        logger.warning(f"Fallback encoding {fallback_encoding} also failed: {fallback_error}")
                        continue
                
                # If all fallbacks fail, use the most robust approach
                logger.error(f"All encoding attempts failed for {file_path}, using binary read with replacement")
                with open(file_path, 'rb') as f:
                    content = f.read()
                return content.decode('utf-8', errors='replace')
                
        except Exception as e:
            logger.error(f"Error converting file {file_path}: {e}")
            # Final fallback: try to read as bytes and decode with replacement
            try:
                with open(file_path, 'rb') as f:
                    content = f.read()
                return content.decode('utf-8', errors='replace')
            except Exception as fallback_error:
                logger.error(f"Final fallback conversion also failed: {fallback_error}")
                return ""
            
    def download_and_convert_file(self, remote_file: str, local_file: str, directory: str = "/", 
                                 target_encoding: str = 'utf-8') -> Tuple[bool, str]:
        """
        Download a file and convert it to a string with proper encoding
        
        Args:
            remote_file: Name of file on FTP server
            local_file: Local path to save file
            directory: Remote directory containing the file
            target_encoding: Desired output encoding (default: utf-8)
            
        Returns:
            Tuple of (success_status, file_content_string)
        """
        # First download the file
        download_success = self.download_file(remote_file, local_file, directory)
        
        if not download_success:
            return False, ""
            
        # Then convert to string
        try:
            content = self.convert_file_to_string(local_file, target_encoding)
            return True, content
        except Exception as e:
            logger.error(f"Error converting downloaded file {remote_file}: {e}")
            return True, ""  # Download succeeded but conversion failed
            
    def download_metadata_as_strings(self, path: str, file_pattern: str, 
                                    target_encoding: str = 'utf-8') -> List[Tuple[str, str, bool]]:
        """
        Download RePEc metadata files and return their content as strings
        
        Args:
            subdir: Remote subdirectory
            pattern: File pattern to match
            target_encoding: Desired output encoding (default: utf-8)
            
        Returns:
            List of tuples (filename, content_string, success_status)
        """
        if not self.ftp:
            logger.error("Not connected to FTP server")
            return []
            
        try:
            # Get list of files
            self.path=path
            self.file_pattern=file_pattern
            files = self.list_files()
            results = []
            
            for filename in files:
                # Create temporary local filename
                temp_local_file = f"temp_{filename}"
                
                # Download and convert
                success, content = self.download_and_convert_file(
                    filename, temp_local_file, path, target_encoding
                )
                
                results.append((filename, content, success))
                
                # Clean up temporary file
                try:
                    if os.path.exists(temp_local_file):
                        os.remove(temp_local_file)
                except Exception as e:
                    logger.warning(f"Could not remove temporary file {temp_local_file}: {e}")
                    
            return results
            
        except Exception as e:
            logger.error(f"Error in download_metadata_as_strings: {e}")
            return []
            
    def download_file_to_bytes(self, remote_file: str, path: str) -> Tuple[bool, bytes]:
        """
        Download a file directly to memory as bytes
        
        Args:
            remote_file: Name of file on FTP server
            directory: Remote directory containing the file
            
        Returns:
            Tuple of (success_status, file_content_bytes)
        """
        if not self.ftp:
            logger.error("Not connected to FTP server")
            return False, b""
            
        try:
            self.ftp.cwd(path)
            
            # Download file content to memory
            from io import BytesIO
            buffer = BytesIO()
            
            self.ftp.retrbinary(f"RETR {remote_file}", buffer.write)
            content_bytes = buffer.getvalue()
            buffer.close()
            
            logger.info(f"Successfully downloaded {remote_file} to memory ({len(content_bytes)} bytes)")
            return True, content_bytes
            
        except (error_perm, error_temp, OSError) as e:
            logger.error(f"Error downloading {remote_file}: {e}")
            return False, b""
            
    def convert_bytes_to_string(self, content_bytes: bytes, 
                            #     target_encoding: str = 'utf-8', 
                            #    source_encoding: str = None
                               ) -> str:
        """
        Convert bytes to string with proper encoding detection and fallbacks
        
        Args:
            content_bytes: File content as bytes
            XXtarget_encoding: Desired output encoding (default: utf-8)
            XXsource_encoding: Source encoding (if None, will auto-detect)
            
        Returns:
            File content as a properly encoded string
        """
        try:
            # # Auto-detect source encoding if not provided
            # if source_encoding is None:
            #     source_encoding = self.detect_bytes_encoding(content_bytes)
                
            # Try to decode with detected encoding
            try:
                content = content_bytes.decode(self.source_encoding, errors='replace')
                
                # Convert to target encoding if different
                if self.source_encoding.lower() != self.target_encoding.lower():
                    content = content.encode(self.target_encoding, errors='replace').decode(self.target_encoding)
                    
                logger.info(f"Successfully converted from {self.source_encoding} to {self.target_encoding}")
                return content
                
            except (UnicodeDecodeError, UnicodeEncodeError) as encoding_error:
                logger.warning(f"Encoding error with {self.source_encoding}: {encoding_error}")
                
                # Fallback: try alternative encodings
                fallback_encodings = []
                
                # If source was UTF-8, try ISO-LATIN-1 first (more common for RePEc)
                if self.source_encoding.lower() in ['utf-8', 'utf8']:
                    fallback_encodings.append('iso-8859-1')
                # If source was ISO-LATIN-1, try UTF-8 second
                elif self.source_encoding.lower() in ['iso-8859-1', 'latin1', 'latin-1']:
                    fallback_encodings.append('utf-8')
                # Always try ISO-LATIN-1 first, then UTF-8 for RePEc files
                else:
                    fallback_encodings.extend(['iso-8859-1', 'utf-8'])
                
                # Try fallback encodings
                for fallback_encoding in fallback_encodings:
                    try:
                        logger.info(f"Trying fallback encoding: {fallback_encoding}")
                        content = content_bytes.decode(fallback_encoding, errors='replace')
                        
                        # Convert to target encoding
                        if fallback_encoding.lower() != self.target_encoding.lower():
                            content = content.encode(self.target_encoding, errors='replace').decode(self.target_encoding)
                            
                        logger.info(f"Successfully converted using fallback {fallback_encoding} to {self.target_encoding}")
                        return content
                        
                    except (UnicodeDecodeError, UnicodeEncodeError) as fallback_error:
                        logger.warning(f"Fallback encoding {fallback_encoding} also failed: {fallback_error}")
                        continue
                
                # If all fallbacks fail, use the most robust approach
                logger.error(f"All encoding attempts failed, using replacement characters")
                return content_bytes.decode('utf-8', errors='replace')
                
        except Exception as e:
            logger.error(f"Error converting bytes to string: {e}")
            # Final fallback: decode with replacement characters
            return content_bytes.decode('utf-8', errors='replace')
            
    def XXdetect_bytes_encoding(self, content_bytes: bytes, sample_size: int = 10000) -> str:
        """
        Detect the character encoding of bytes content
        
        Args:
            content_bytes: File content as bytes
            sample_size: Number of bytes to sample for encoding detection
            
        Returns:
            Detected encoding (e.g., 'iso-8859-1', 'utf-8', 'windows-1252')
        """
        try:
            # Use a sample of the bytes for encoding detection
            sample = content_bytes[:sample_size]
            
            # Try ISO-LATIN-1 first (common for RePEc files)
            try:
                sample.decode('iso-8859-1')
                logger.info("Detected encoding: iso-8859-1 (successful decode)")
                return 'iso-8859-1'
            except UnicodeDecodeError:
                pass
                
            # Try UTF-8 second (modern encoding, but less common for RePEc)
            try:
                sample.decode('utf-8')
                logger.info("Detected encoding: utf-8 (successful decode)")
                return 'utf-8'
            except UnicodeDecodeError:
                pass
                
            # Try Windows-1252 (Windows-specific Latin encoding)
            try:
                sample.decode('windows-1252')
                logger.info("Detected encoding: windows-1252 (successful decode)")
                return 'windows-1252'
            except UnicodeDecodeError:
                pass
                
            # Try ASCII (basic 7-bit encoding)
            try:
                sample.decode('ascii')
                logger.info("Detected encoding: ascii (successful decode)")
                return 'ascii'
            except UnicodeDecodeError:
                pass
                
            # If all common encodings fail, default to ISO-LATIN-1 for RePEc files
            logger.warning("All common encodings failed, defaulting to ISO-LATIN-1")
            return 'iso-8859-1'
                
        except Exception as e:
            logger.error(f"Error detecting encoding from bytes: {e}")
            # Default to ISO-LATIN-1 for RePEc files
            return 'iso-8859-1'
            
    def download_and_parse_metadata(self, remote_file: str, path: str, 
                                   target_encoding: str) -> Tuple[bool, str, dict]:
        """
        Download a file, convert to string, and parse into RePEc metadata dictionary
        
        Args:
            remote_file: Name of file on FTP server
            directory: Remote directory containing the file
            target_encoding: Desired output encoding (default: utf-8)
            
        Returns:
            Tuple of (success_status, content_string, parsed_metadata_dict)
        """
        # Download to bytes
        success, content_bytes = self.download_file_to_bytes(remote_file, path)
        
        if not success:
            return False, "", {}
            
        # Convert bytes to string
        content_string = self.convert_bytes_to_string(content_bytes)
        
        # Parse into metadata dictionary
        metadata_dict = self.parse_repec_metadata(content_string)
        
        return True, content_string, metadata_dict
        
    def parse_repec_metadata_BAK1(self, content_string: str) -> dict:
        """
        Parse RePEc metadata string into a dictionary of key-value pairs
        
        Args:
            content_string: RePEc metadata content as string
            
        Returns:
            Dictionary containing parsed metadata
        """
        metadata = {}
        
        try:
            # Split content into lines
            lines = content_string.split('\n')
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                    
                # Parse RePEc format: Key: Value
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Handle multi-line values (indented lines)
                    if key in metadata:
                        if isinstance(metadata[key], list):
                            metadata[key].append(value)
                        else:
                            metadata[key] = [metadata[key], value]
                    else:
                        metadata[key] = value
                        
            logger.info(f"Successfully parsed RePEc metadata with {len(metadata)} fields")
            return metadata
            
        except Exception as e:
            logger.error(f"Error parsing RePEc metadata: {e}")
            return {}
            
    def parse_repec_metadata(self, content_string: str, select_keys=['DOI', 'File-URL', 'Handle', 'Number']) -> dict:
        """
        Parse RePEc metadata string into a dictionary of key-value pairs
        
        Args:
            content_string: RePEc metadata content as string
            
        Returns:
            List of Dictionary containing parsed metadata
        """
        entryMetadata=[]
                
        try:
            entries = re.split(r'Template-Type: ReDIF.+?(?=\n|$)', content_string.strip())[1:]
            # Split content into lines
            for entry in entries:
                metadata = {}
                lines = entry.strip().split('\n')
                for line in lines:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                        
                    # Parse RePEc format: Key: Value
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # Handle multi-line values (indented lines)
                        if (key in select_keys) and (key in metadata):
                            if isinstance(metadata[key], list):
                                metadata[key].append(value)
                            else:
                                metadata[key] = [metadata[key], value]
                        elif (key in select_keys):
                            metadata[key] = value
                        else:
                            None
                entryMetadata.append(metadata)

            logger.info(f"Successfully parsed RePEc metadata with {len(metadata)} fields")
            return entryMetadata
            
        except Exception as e:
            logger.error(f"Error parsing RePEc metadata: {e}")
            return {}
            
    def download_multiple_metadata_files(self) -> List[Tuple[str, str, dict, bool]]:
        """
        Download multiple RePEc metadata files and parse them into dictionaries
        
        Args:
            subdir: Remote subdirectory
            pattern: File pattern to match
            target_encoding: Desired output encoding (default: utf-8)
            
        Returns:
            List of tuples (filename, content_string, parsed_metadata_dict, success_status)
        """
        path=self.path
        file_pattern=self.file_pattern
        target_encoding=self.target_encoding
        if not self.ftp:
            logger.error("Not connected to FTP server")
            return []
            
        try:
            # Get list of files
            files = self.list_files()
            results = []
            
            for filename in files:
                logger.info(f"Processing {filename}...")
                
                # Download, convert, and parse
                success, content, metadata = self.download_and_parse_metadata(
                    filename, path, target_encoding
                )
                
                results.append((filename, content, metadata, success))
                
                if success:
                    logger.info(f"Successfully processed {filename}: {len(metadata)} metadata ")
                else:
                    logger.warning(f"Failed to process {filename}")
                    
            return results
            
        except Exception as e:
            logger.error(f"Error in download_multiple_metadata_files: {e}")
            return []
