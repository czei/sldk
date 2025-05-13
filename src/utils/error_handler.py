"""
Error handling utility for logging errors and debug information.
Copyright 2024 3DUPFitters LLC
"""
import os
import traceback

try:
    import storage
    STORAGE_AVAILABLE = True
except (ImportError, AttributeError):
    STORAGE_AVAILABLE = False

class ErrorHandler:
    """
    Centralized error handling and logging facility.
    Handles writing to log files with fallback to console output.
    """
    
    def __init__(self, file_name):
        """
        Initialize the error handler with read-only filesystem detection
        
        Args:
            file_name: The name of the log file
        """
        self.fileName = file_name
        # Start with the assumption that the filesystem is read-only
        # We'll only set it to writable if we can successfully write to it
        self.is_readonly = True
        
        # First check if we can directly detect read-only status via storage module
        if STORAGE_AVAILABLE:
            try:
                self.is_readonly = storage.getmount('/').readonly
                print(f"Filesystem read-only status from storage: {self.is_readonly}")
                # If storage says it's read-only, trust that and skip the write test
                if self.is_readonly:
                    print("Filesystem is read-only according to storage module")
                    print(f"ErrorHandler initialized - read-only filesystem")
                    return
            except (AttributeError, OSError):
                # Continue with write test if storage check fails
                print("Storage module check failed, will try write test")
        
        # Regardless of storage module results, always verify by attempting to write
        # This is the most reliable test
        try:
            # Try to write to an existing file first (append mode)
            if self.file_exists(file_name):
                with open(self.fileName, 'a') as file:
                    file.write('')  # Try to append nothing
                self.is_readonly = False
            # If file doesn't exist, try to create it
            else:
                with open(self.fileName, 'w') as file:
                    file.write('')  # Try to create an empty file
                self.is_readonly = False
        except OSError as e:
            # If any error occurs during write/create, filesystem is read-only
            self.is_readonly = True
            print(f"Write test failed: {str(e)}")
        
        # Log system state at initialization based on final determination
        print(f"ErrorHandler initialized - {'read-only' if self.is_readonly else 'writable'} filesystem")

    @staticmethod
    def filter_non_ascii(text):
        """
        Filter out non-ASCII characters from a string
        
        Args:
            text: The text to filter
            
        Returns:
            A string with only ASCII characters
        """
        if text is None:
            return ""
        return "".join(c for c in str(text) if ord(c) < 128)

    @staticmethod
    def file_exists(file_name):
        """
        Check if a file exists
        
        Args:
            file_name: The name of the file to check
            
        Returns:
            True if the file exists, False otherwise
        """
        file_exists = True
        try:
            status = os.stat(file_name)
        except OSError:
            file_exists = False
        return file_exists

    def error(self, e, str_description):
        """
        Log an error with a description and stack trace

        Args:
            e: The exception that occurred
            str_description: A description of the error
        """
        # Handle the case where e is None (no exception but error message)
        if e is None:
            except_str = str_description
            st_str = ""
        else:
            except_str = str_description + ":" + str(e)
            try:
                st = traceback.format_exception(e)
                st_str = "stack trace:"
                for line in st:
                    st_str = st_str + line
            except Exception:
                # Fallback for cases where traceback.format_exception fails
                st_str = "stack trace unavailable"

        # Filter out non-ASCII characters to prevent UnicodeEncodeError
        filtered_except_str = self.filter_non_ascii(except_str)
        filtered_st_str = self.filter_non_ascii(st_str)

        # Always print errors to console for visibility
        print(filtered_except_str)
        if st_str:
            print(filtered_st_str)

        # Only attempt to write to file if filesystem is writable
        if not self.is_readonly:
            try:
                with open(self.fileName, 'a') as file:
                    file.write(filtered_except_str + "\n")
                    if st_str:
                        file.write(filtered_st_str + "\n")
            except OSError:
                # If write fails unexpectedly, update readonly state
                self.is_readonly = True
                # Only print this message once when we first detect a failure
                print("Filesystem detected as read-only, logs will be displayed on console only")

    def debug(self, message):
        """
        Log a debug message
        
        Args:
            message: The debug message to log
        """
        print(message)
        self.write_to_file(message)

    def write_to_file(self, message):
        """
        Write a message to the log file
        
        Args:
            message: The message to write
        """
        # Only attempt to write if filesystem is writable
        if self.is_readonly:
            # In read-only mode, we'll just print to console without error messages
            # We don't print "Error writing to log file" as that confuses users
            return
            
        try:
            # Filter out non-ASCII characters to prevent UnicodeEncodeError
            filtered_message = self.filter_non_ascii(message)
            
            with open(self.fileName, 'a') as file:
                file.write(filtered_message + "\n")
        except OSError:
            # If write fails unexpectedly, update readonly state
            self.is_readonly = True
            # Only print this message once when we first detect a failure
            print("Filesystem detected as read-only, logs will be displayed on console only")

    def info(self, message):
        """
        Log an informational message
        
        Args:
            message: The informational message to log
        """
        print(message)
        self.write_to_file(message)