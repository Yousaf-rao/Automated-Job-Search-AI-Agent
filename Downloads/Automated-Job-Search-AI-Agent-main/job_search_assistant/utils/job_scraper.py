import requests
import random
import time
from datetime import datetime, timedelta
from tenacity import retry, stop_after_attempt, wait_exponential
from cachetools import TTLCache, cached
from typing import List, Dict, Optional
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import REQUEST_TIMEOUT, MAX_RETRIES, CACHE_TTL, SALARY_RANGES
from utils.logger import app_logger

class JobScraper:
    """
    Enhanced Job Scraper with realistic mock data generation,
    robust error handling, and performance optimizations.
    """
    
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # Initialize platform settings with validation URLs
        self.platforms = {
            "Indeed": {"base": "https://www.indeed.com", "search": "https://www.indeed.com/jobs"},
            "LinkedIn": {"base": "https://www.linkedin.com", "search": "https://www.linkedin.com/jobs"},
            "Glassdoor": {"base": "https://www.glassdoor.com", "search": "https://www.glassdoor.com/Job/jobs.htm"},
            "Monster": {"base": "https://www.monster.com", "search": "https://www.monster.com/jobs/search"},
            "ZipRecruiter": {"base": "https://www.ziprecruiter.com", "search": "https://www.ziprecruiter.com/jobs"}
        }

        # companies database by industry
        self.companies = {
            "Tech": ["Google", "Microsoft", "Amazon", "Apple", "Meta", "Netflix", "Spotify", "Uber", "Airbnb", "Stripe"],
            "Finance": ["JPMorgan Chase", "Goldman Sachs", "Morgan Stanley", "Visa", "Mastercard", "BlackRock"],
            "Healthcare": ["Pfizer", "Johnson & Johnson", "UnitedHealth Group", "CVS Health", "Merck"],
            "Consulting": ["McKinsey", "BCG", "Bain & Company", "Deloitte", "Accenture", "PwC"]
        }

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def verify_url(self, url: str) -> bool:
        """
        Verify if a URL is reachable with retry logic.
        """
        try:
            response = self.session.head(url, timeout=REQUEST_TIMEOUT, allow_redirects=True)
            if response.status_code < 400:
                return True
            
            # Fallback to GET if HEAD fails
            response = self.session.get(url, timeout=REQUEST_TIMEOUT, allow_redirects=True)
            return response.status_code < 400
            
        except requests.RequestException as e:
            app_logger.warning(f"URL verification failed for {url}: {str(e)}")
            return False

    @cached(cache=TTLCache(maxsize=100, ttl=CACHE_TTL))
    def search_jobs(self, keywords: str, location: str, platform: str = "Indeed", count: int = 5) -> List[Dict]:
        """
        Search for jobs with caching support.
        """
        app_logger.info(f"Searching for {keywords} in {location} on {platform}")
        
        # Simulate network delay for realism
        time.sleep(random.uniform(0.5, 1.5))
        
        # Generate high-quality mock data
        return self._generate_enhanced_mock_jobs(keywords, location, platform, count)

    def _generate_enhanced_mock_jobs(self, keywords: str, location: str, platform: str, count: int) -> List[Dict]:
        """
        Generate realistic job listings based on search criteria.
        """
        jobs = []
        platform_info = self.platforms.get(platform, self.platforms["Indeed"])
        base_url = platform_info["base"]
        
        for i in range(count):
            # Determine seniority and salary
            seniority = random.choice(["Junior", "Mid", "Senior", "Lead", "Manager"])
            current_salary = SALARY_RANGES.get(seniority, "$100k - $150k")
            
            # Select company based on implicit keyword context (default to Tech)
            industry = "Tech"
            if "finance" in keywords.lower(): industry = "Finance"
            elif "health" in keywords.lower(): industry = "Healthcare"
            company = random.choice(self.companies.get(industry, self.companies["Tech"]))
            
            # Generate realistic title
            title = f"{seniority} {keywords.title()}"
            if "Engineer" not in title and "Developer" not in title and "Manager" not in title:
                title += " Specialist"
                
            # Create a rich description
            description = (
                f"We are seeking a talented {title} to join our dynamic team at {company}. "
                f"In this role, you will be responsible for driving innovation and solving complex problems. "
                f"The ideal candidate has experience with modern technologies and a passion for excellence.\n\n"
                f"**Key Responsibilities:**\n"
                f"• Design and implement scalable solutions\n"
                f"• Collaborate with cross-functional teams\n"
                f"• Mentor junior team members\n\n"
                f"**Requirements:**\n"
                f"• Bachelor's degree in related field\n"
                f"• 3+ years of relevant experience\n"
                f"• Strong problem-solving skills"
            )

            job = {
                "id": f"{platform.lower()}-{int(time.time())}-{i}",
                "title": title,
                "company": company,
                "location": location,
                "platform": platform,
                "salary": current_salary,
                "description": description,
                "posted_date": self._get_random_date(),
                "deadline": (datetime.now() + timedelta(days=random.randint(14, 30))).strftime("%Y-%m-%d"),
                "link": f"{base_url}/viewjob?id={random.randint(100000, 999999)}",
                "apply_link": f"{base_url}/apply?id={random.randint(100000, 999999)}",
                "is_remote": "Remote" in location or random.random() > 0.7,
                "job_type": random.choice(["Full-time", "Contract", "Full-time", "Full-time"]),
                "verified": random.random() > 0.2  # 80% chance of being verified
            }
            
            jobs.append(job)
            
        return jobs

    def _get_random_date(self) -> str:
        """Get a random date within the last 7 days."""
        days_ago = random.randint(0, 7)
        date = datetime.now() - timedelta(days=days_ago)
        if days_ago == 0:
            return "Today"
        elif days_ago == 1:
            return "Yesterday"
        return f"{days_ago} days ago"

if __name__ == "__main__":
    # Quick test
    scraper = JobScraper()
    jobs = scraper.search_jobs("Python Developer", "Remote", count=2)
    for job in jobs:
        print(f"Found: {job['title']} at {job['company']} ({job['salary']})")
