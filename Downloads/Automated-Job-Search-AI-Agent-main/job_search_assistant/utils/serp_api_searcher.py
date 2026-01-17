"""
Serp API Searcher Module
------------------------
This module handles job searching functionality using the SerpAPI Google Jobs engine.
It allows searching for jobs based on keywords, location, and optional platform filters.

Key Features:
- Real-time job search using SerpAPI.
- Advanced filtering: Platform (e.g., LinkedIn), Date (e.g., past 7 days).
- Robustness: Automatic pagination to fetch all requested results and retry logic for network stability.
- Data Extraction: Detailed job info including Salary, Job Type, and smart Apply Link resolution.
- Logging: Standard logging for production-grade observability.
"""

import os
import requests
import json
import time
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SerpApiSearcher:
    """
    A class to interact with SerpAPI for searching jobs.
    
    Attributes:
        api_key (str): The API key for SerpAPI.
        base_url (str): The base URL for SerpAPI search queries.
    """

    def __init__(self):
        """
        Initialize the SerpApiSearcher.
        
        Retrieves the 'SERPAPI_KEY' from environment variables.
        """
        self.api_key = os.getenv("SERPAPI_KEY") or os.getenv("SERP_API_KEY")
        
        if not self.api_key:
            logger.warning("SERPAPI_KEY not found in environment variables. Search functionalities will fail.")
        
        self.base_url = "https://serpapi.com/search"

    def _make_request(self, params: Dict[str, Any], retries: int = 3) -> Optional[Dict[str, Any]]:
        """
        Helper method to make API requests with retry logic.
        """
        for attempt in range(retries):
            try:
                response = requests.get(self.base_url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                if "error" in data:
                    logger.error(f"SerpAPI Error: {data['error']}")
                    return None
                    
                return data
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request failed (Attempt {attempt + 1}/{retries}): {e}")
                time.sleep(2 * (attempt + 1)) # Exponential backoff
        
        logger.error("Max retries reached. Request failed.")
        return None

    def search_jobs(self, 
                   query: str, 
                   location: str = "", 
                   platform: str = None, 
                   count: int = 5, 
                   days: int = 7) -> List[Dict[str, Any]]:
        """
        Search for jobs using SerpAPI Google Jobs engine with pagination and robust filtering.

        Args:
            query (str): The job title or keywords.
            location (str): The geographic location.
            platform (str, optional): Specific platform to filter by (e.g., "LinkedIn").
            count (int): The target number of results.
            days (int): Date range (default 7).

        Returns:
            List[Dict[str, Any]]: A list of standardized job dictionaries.
        """
        
        full_query = f"{query} {location}".strip()
        
        # Date filter mapping
        date_filter = "date_posted:week"
        if days <= 1:
            date_filter = "date_posted:today"
        elif days > 7:
            date_filter = "date_posted:month"
            
        base_params = {
            "engine": "google_jobs",
            "q": full_query,
            "google_domain": "google.com",
            "gl": "us",
            "hl": "en",
            "api_key": self.api_key,
            "chips": date_filter,
        }

        logger.info(f"Searching for: '{full_query}' | Platform: {platform} | Target Count: {count}")

        normalized_jobs = []
        start_offset = 0
        
        # Pagination Loop
        while len(normalized_jobs) < count:
            # Calculate how many to fetch in this batch (API usually limits to ~10)
            # We ask for 10 at a time to be safe and paginate
            batch_size = 10 
            
            params = base_params.copy()
            params["start"] = start_offset
            params["num"] = batch_size

            data = self._make_request(params)
            
            if not data:
                break

            jobs_results = data.get("jobs_results", [])
            
            if not jobs_results:
                logger.info("No more results found.")
                break
                
            logger.info(f"Fetched {len(jobs_results)} raw results from offset {start_offset}")

            for job in jobs_results:
                if len(normalized_jobs) >= count:
                    break

                # --- EXTRACT KEY DETAILS ---
                title = job.get("title", "No Title")
                company_name = job.get("company_name", "Unknown Company")
                location_str = job.get("location", "Remote/Unknown")
                description = job.get("description", "No description available.")
                
                # --- APPLY LINK RESOLUTION ---
                apply_options = job.get("apply_options", [])
                platform_detected = "Unknown"
                valid_apply_link = None
                
                # Check apply options for platform match
                found_match_platform = False
                for option in apply_options:
                    opt_title = option.get("title", "").lower()
                    opt_link = option.get("link", "")
                    
                    if platform:
                        if platform.lower() in opt_title:
                            valid_apply_link = opt_link
                            platform_detected = option.get("title")
                            found_match_platform = True
                            break
                    else:
                        # Default to first option if no preference
                        if not valid_apply_link:
                            valid_apply_link = opt_link
                            platform_detected = option.get("title")
                
                # Filter Logic
                if platform and not found_match_platform:
                    continue

                # Fallbacks for Apply Link
                if not valid_apply_link:
                    valid_apply_link = job.get("related_links", [{}])[0].get("link", "")
                if not valid_apply_link:
                    valid_apply_link = job.get("share_link") or f"https://www.google.com/search?q={job.get('job_id')}"

                # --- SALARY EXTRACTION ---
                # Salary is often in 'detected_extensions' -> 'salary' or sometimes top level
                salary = "Not specified"
                extensions = job.get("detected_extensions", {})
                if "salary" in extensions:
                    salary = extensions["salary"]
                
                # --- JOB TYPE EXTRACTION ---
                job_type = "Unspecified"
                if "schedule_type" in extensions:
                     job_type = extensions["schedule_type"]
                elif "work_from_home" in extensions:
                     job_type = "Remote"

                # --- SNIPPET CREATION ---
                snippet = description[:200] + "..." if len(description) > 200 else description

                job_entry = {
                    "id": job.get("job_id"),
                    "title": title,
                    "company": company_name,
                    "location": location_str,
                    "platform": platform_detected,
                    "job_type": job_type,
                    "salary": salary,
                    "date_posted": extensions.get("posted_at", "Recently"),
                    "apply_link": valid_apply_link,
                    "description": description,
                    "snippet": snippet,
                    "source": "Google Jobs via SerpAPI"
                }

                # Deduplication check
                if not any(j['id'] == job_entry['id'] for j in normalized_jobs):
                    normalized_jobs.append(job_entry)
            
            # Prepare for next page
            start_offset += len(jobs_results)
            
            # Safety break if we aren't getting new results to avoid infinite loops
            if len(jobs_results) == 0:
                break
                
        logger.info(f"Total jobs found after filtering and pagination: {len(normalized_jobs)}")
        return normalized_jobs

# Example Usage
if __name__ == "__main__":
    searcher = SerpApiSearcher()
    if searcher.api_key:
        print("Testing Enhanced SerpApiSearcher...")
        results = searcher.search_jobs(query="Software Engineer", location="Austin", count=12) # Testing pagination > 10
        print(f"Retrieved {len(results)} jobs.")
        if results:
            print(json.dumps(results[0], indent=2))
    else:
        print("Skipping test run (No API Key).")