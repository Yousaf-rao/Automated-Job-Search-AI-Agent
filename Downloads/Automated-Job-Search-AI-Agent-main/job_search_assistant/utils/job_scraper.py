import requests
from bs4 import BeautifulSoup
import time
import random
import re
from datetime import datetime, timedelta

class JobScraper:
    """Job scraper for multiple platforms."""
    
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        # Initialize platform-specific settings
        self.platforms = {
            "LinkedIn": {
                "base_url": "https://www.linkedin.com"
            },
            "Indeed": {
                "search_url": "https://www.indeed.com/jobs",
                "base_url": "https://www.indeed.com"
            },
            "Glassdoor": {
                "base_url": "https://www.glassdoor.com",
                "search_url": "https://www.glassdoor.com/Job/jobs.htm"
            },
            "Monster": {
                "search_url": "https://www.monster.com/jobs/search",
                "base_url": "https://www.monster.com"
            }
        }

    def search_jobs(self, keywords, location, platform="Indeed", count=5):
        """Search for jobs across selected platforms."""
        if platform == "LinkedIn":
            return self.search_linkedin(keywords, location, count)
        elif platform == "Indeed":
            return self.search_indeed(keywords, location, count)
        elif platform == "Glassdoor":
            return self.search_glassdoor(keywords, location, count)
        elif platform == "Monster":
            return self.search_monster(keywords, location, count)
        else:
            # Default to Indeed if platform unknown
            return self.search_indeed(keywords, location, count)

    def search_indeed(self, keywords, location, count=5):
        """
        Search Indeed for jobs.
        Note: Since Indeed blocks most scrapers, this generates realistic mock data
        while providing a valid search URL for the user to visit.
        """
        try:
            # Format search parameters correctly for Indeed
            keyword_param = keywords.replace(" ", "+")
            location_param = location.replace(" ", "+")
            
            # Create search URL
            search_url = f"https://www.indeed.com/jobs?q={keyword_param}&l={location_param}&sort=date"
            
            # Create fallback job listings (Mock Data as per screenshots)
            jobs = []
            
            company_names = ["Microsoft", "Amazon", "Google", "Apple", "Meta", "Netflix", "Tesla", "IBM"]
            job_types = ["Full-time", "Contract", "Permanent", "Remote", "Hybrid"]
            
            for i in range(min(count, 10)):
                # Generate realistic fake job listings
                job = {
                    "title": f"{keywords} - {random.choice(['Senior', 'Junior', 'Lead', 'Principal'])}",
                    "company": random.choice(company_names),
                    "location": location,
                    "platform": "Indeed",
                    "link": search_url, # Pointing to the main search results as deep linking is hard without real scraping
                    "posted_date": (datetime.now() - timedelta(days=random.randint(0, 7))).strftime("%Y-%m-%d"),
                    "description": f"Exciting opportunity for a {keywords} at a leading tech company. Apply now to join our team!",
                    "salary": f"${random.randint(80, 180)}k - ${random.randint(190, 250)}k a year"
                }
                jobs.append(job)
                
            return jobs
            
        except Exception as e:
            print(f"Error searching Indeed: {e}")
            return []

    def search_linkedin(self, keywords, location, count=5):
        """Mock LinkedIn search."""
        return self._generate_mock_jobs(keywords, location, "LinkedIn", count)

    def search_glassdoor(self, keywords, location, count=5):
        """Mock Glassdoor search."""
        return self._generate_mock_jobs(keywords, location, "Glassdoor", count)

    def search_monster(self, keywords, location, count=5):
        """Mock Monster search."""
        return self._generate_mock_jobs(keywords, location, "Monster", count)

    def _generate_mock_jobs(self, keywords, location, platform, count):
        """Helper to generate mock data for other platforms."""
        jobs = []
        companies = ["Startup Inc", "Tech Corp", "Data Systems", "Cloud Solutions", "AI Frontiers"]
        
        for i in range(min(count, 5)):
            job = {
                "title": f"{keywords}",
                "company": random.choice(companies),
                "location": location,
                "platform": platform,
                "link": f"https://www.{platform.lower()}.com/jobs",
                "posted_date": datetime.now().strftime("%Y-%m-%d"),
                "description": f"Great job opportunity on {platform}.",
                "salary": "Competitive"
            }
            jobs.append(job)
        return jobs
