import json
import os
import datetime
import hashlib
from typing import List, Dict, Any, Optional

# =================================================================================================
# CUSTOM ENCODER FOR DATE AND TIME
# =================================================================================================
def date_time_encoder(obj: Any) -> Any:
    """
    Custom encoder function to handle datetime objects during JSON serialization.
    This ensures that any datetime or date object is converted to a string format (ISO 8601).
    
    Args:
        obj (Any): The object to encode.
        
    Returns:
        str: ISO formatted string if obj is a datetime/date.
    Raises:
        TypeError: If the object is not a date/time and not serializable.
    """
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} is not serializable")


class JobStorage:
    """
    Manages the persistent storage of job postings using local JSON files.
    
    This class is designed to:
    1. Save job details safely without data loss.
    2. Handle date and time conversions automatically.
    3. Generate unique filenames to prevent overwriting.
    4. Provide easy access to saved jobs.
    """

    def __init__(self, directory: str = "saved_jobs"):
        """
        Initialize the storage system.
        
        Args:
            directory (str): The name of the directory where saved jobs will be stored.
                             Defaults to "saved_jobs".
        """
        self.directory = directory
        # Ensure the directory exists immediately upon initialization
        self._ensure_directory()

    # =============================================================================================
    # DIRECTORY MANAGEMENT
    # =============================================================================================
    def _ensure_directory(self):
        """
        Creates the storage directory if it does not already exist.
        This prevents 'FileNotFoundError' when trying to save files.
        """
        if not os.path.exists(self.directory):
            try:
                os.makedirs(self.directory)
                print(f"[SUCCESS] Created directory for saved jobs: {self.directory}")
            except OSError as e:
                print(f"[ERROR] Failed to create directory {self.directory}: {e}")

    # =============================================================================================
    # FILE NAMING AND HANDLING
    # =============================================================================================
    def _generate_unique_filename(self, job: Dict) -> str:
        """
        Generates a unique filename based on the job's company, title, and current timestamp.
        
        This prevents overwriting if a user saves the same job multiple times or 
        multiple jobs have similar titles.
        
        Args:
            job (Dict): The job data dictionary containing 'company' and 'title'.
            
        Returns:
            str: A formatted, unique filename (e.g., "Google_Software_Eng_20231025_123456_abc.json")
        """
        # Extract basic info, defaulting to 'Unknown' if missing
        company = job.get('company', 'UnknownCompany').replace(' ', '_')
        title = job.get('title', 'UnknownRole').replace(' ', '_')
        
        # Get current timestamp string (YearMonthDay_HourMinuteSecond)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create a short has of the unique link or ID to ensure absolute uniqueness
        # We use MD5 on the link/id (or timestamp if neither exists)
        unique_identifier = job.get('link', '') or job.get('id', '') or str(datetime.datetime.now())
        short_hash = hashlib.md5(unique_identifier.encode()).hexdigest()[:6]
        
        # Clean the filename: Only keep alphanumeric characters, underscores, or hyphens
        # This prevents invalid characters in file paths on Windows/Linux
        safe_company = "".join([c for c in company if c.isalnum() or c in ('_', '-')])
        safe_title = "".join([c for c in title if c.isalnum() or c in ('_', '-')])
        
        # Combine parts into final filename
        filename = f"{safe_company}_{safe_title}_{timestamp}_{short_hash}.json"
        return filename

    # =============================================================================================
    # DATA PROCESSING HELPER
    # =============================================================================================
    def _process_job_data(self, job: Dict) -> Dict:
        """
        Processes the job dictionary to ensure all data is format-safe.
        Specifically handles date/time fields by converting them to strings 
        if the JSON encoder misses them (double-check mechanism).
        
        Args:
            job (Dict): The original job data.
            
        Returns:
            Dict: A processed copy of the job data.
        """
        # Create a shallow copy to avoid modifying the original dictionary 
        # that might be used elsewhere in the app (avoids "dictionary changed size during iteration" errors)
        processed_job = job.copy()
        
        # Explicitly check for 'saved_at' and ensure it's present
        if 'saved_at' not in processed_job:
            # Add timestamp if missing
            processed_job['saved_at'] = datetime.datetime.now()
            
        return processed_job

    # =============================================================================================
    # SAVE FUNCTION
    # =============================================================================================
    def save_job(self, job: Dict) -> bool:
        """
        Saves a job posting to a local JSON file.
        
        Steps performed:
        1. Process/Copy data to ensure safety (add timestamps, avoid mutation).
        2. Generate a unique filename.
        3. Write the data to disk using the custom date_time_encoder.
        
        Args:
            job (Dict): The dictionary containing job details.
            
        Returns:
            bool: True if save was successful, False otherwise.
        """
        try:
            # 1. Process the data (add timestamps, copy dict)
            job_data = self._process_job_data(job)
            
            # 2. Generate unique filename
            filename = self._generate_unique_filename(job_data)
            
            # 3. Add the filename to the data itself so we can find/remove it later easily
            job_data['_storage_filename'] = filename
            
            # 4. Construct full file path
            file_path = os.path.join(self.directory, filename)
            
            # 5. Write to file
            # We use 'utf-8' encoding to support special characters
            # We use 'default=date_time_encoder' to handle any datetime objects
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(job_data, f, indent=4, default=date_time_encoder)
                
            print(f"[SAVED] Job successfully saved to: {file_path}")
            return True

        except Exception as e:
            # Catch any errors (e.g., permission issues, disk full)
            print(f"[ERROR] Could not save job: {e}")
            return False

    # =============================================================================================
    # LOAD FUNCTION
    # =============================================================================================
    def get_saved_jobs(self) -> List[Dict]:
        """
        Loads all saved jobs from the 'saved_jobs' directory.
        
        It iterates through every .json file in the directory, reads it,
        and returns a list of job dictionaries.
        
        Returns:
            List[Dict]: A list of loaded job postings, sorted by newest first.
        """
        loaded_jobs = []
        
        # Safety check: if directory was deleted effectively
        if not os.path.exists(self.directory):
            return []
            
        # Iterate over all files in the directory
        for filename in os.listdir(self.directory):
            if filename.endswith(".json"):
                file_path = os.path.join(self.directory, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        job_data = json.load(f)
                        
                        # Ensure we know which file this data came from (critical for deletion)
                        job_data['_storage_filename'] = filename 
                        loaded_jobs.append(job_data)
                        
                except json.JSONDecodeError:
                    print(f"[WARNING] Skipping corrupted file: {filename}")
                except Exception as e:
                    print(f"[ERROR] Failed to load {filename}: {e}")
                    
        # Sort the jobs by 'saved_at' date in descending order (newest first)
        # We use .get(..., '') to avoid errors if 'saved_at' is somehow missing
        loaded_jobs.sort(key=lambda x: x.get('saved_at', ''), reverse=True)
        
        return loaded_jobs

    # =============================================================================================
    # REMOVE FUNCTION
    # =============================================================================================
    def remove_job(self, job_identifier: Dict) -> bool:
        """
        Deletes a saved job file from the disk.
        
        Args:
            job_identifier (Dict): The job dictionary to remove. 
                                   Must contain '_storage_filename'.
        
        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        # Attempt to retrieve the filename we stored during save/load
        filename = job_identifier.get('_storage_filename')
        
        if filename:
            file_path = os.path.join(self.directory, filename)
            
            # Check if file exists before trying to delete
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    print(f"[REMOVED] Job file deleted: {file_path}")
                    return True
                except OSError as e:
                    print(f"[ERROR] Could not delete file {file_path}: {e}")
                    return False
        
        print("[WARNING] Could not remove job. Identifier missing '_storage_filename'.")
        return False
