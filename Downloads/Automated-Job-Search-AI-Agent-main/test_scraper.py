"""
Test script for JobScraper URL verification functionality.
"""
import sys
sys.path.append(r'c:\Users\Friends shop\Downloads\Automated-Job-Search-AI-Agent-main')

from job_search_assistant.utils.job_scraper import JobScraper

def test_url_verification():
    """Test the verify_url method."""
    print("=" * 60)
    print("Testing URL Verification Functionality")
    print("=" * 60)
    
    scraper = JobScraper()
    
    # Test 1: Valid URL
    print("\n[Test 1] Verifying valid URL (https://www.google.com)...")
    result = scraper.verify_url("https://www.google.com")
    print(f"Result: {'✓ PASS' if result else '✗ FAIL'} - URL is {'reachable' if result else 'not reachable'}")
    
    # Test 2: Invalid URL (404)
    print("\n[Test 2] Verifying invalid URL (non-existent page)...")
    result = scraper.verify_url("https://www.google.com/this-page-definitely-does-not-exist-12345")
    print(f"Result: {'✓ PASS' if not result else '✗ FAIL'} - URL correctly identified as {'not reachable' if not result else 'reachable'}")
    
    # Test 3: Indeed base URL
    print("\n[Test 3] Verifying Indeed base URL...")
    result = scraper.verify_url("https://www.indeed.com")
    print(f"Result: {'✓ PASS' if result else '✗ FAIL'} - URL is {'reachable' if result else 'not reachable'}")
    
    # Test 4: Completely invalid domain
    print("\n[Test 4] Verifying completely invalid domain...")
    result = scraper.verify_url("https://this-domain-does-not-exist-xyz123.com")
    print(f"Result: {'✓ PASS' if not result else '✗ FAIL'} - URL correctly identified as {'not reachable' if not result else 'reachable'}")
    
    print("\n" + "=" * 60)

def test_search_indeed():
    """Test the search_indeed method with URL verification."""
    print("\n" + "=" * 60)
    print("Testing Indeed Search with URL Verification")
    print("=" * 60)
    
    scraper = JobScraper()
    
    print("\n[Test] Searching for 'Python Developer' in 'Remote'...")
    jobs = scraper.search_jobs("Python Developer", "Remote", platform="Indeed", count=3)
    
    if jobs:
        print(f"\n✓ Successfully retrieved {len(jobs)} job listings")
        print(f"\nFirst job details:")
        print(f"  Title: {jobs[0]['title']}")
        print(f"  Company: {jobs[0]['company']}")
        print(f"  Location: {jobs[0]['location']}")
        print(f"  Platform: {jobs[0]['platform']}")
        print(f"  Link: {jobs[0]['link']}")
        print(f"  Posted: {jobs[0]['posted_date']}")
    else:
        print("✗ No jobs retrieved")
    
    print("\n" + "=" * 60)

def test_all_platforms():
    """Test URL verification across all platforms."""
    print("\n" + "=" * 60)
    print("Testing All Platforms with URL Verification")
    print("=" * 60)
    
    scraper = JobScraper()
    platforms = ["Indeed", "LinkedIn", "Glassdoor", "Monster"]
    
    for platform in platforms:
        print(f"\n[{platform}] Searching for 'Software Engineer' in 'New York'...")
        jobs = scraper.search_jobs("Software Engineer", "New York", platform=platform, count=2)
        
        if jobs:
            print(f"  ✓ Retrieved {len(jobs)} jobs")
            print(f"  Link: {jobs[0]['link']}")
        else:
            print(f"  ✗ No jobs retrieved")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    print("\n🚀 Starting JobScraper Tests...\n")
    
    # Run all tests
    test_url_verification()
    test_search_indeed()
    test_all_platforms()
    
    print("\n✅ All tests completed!\n")
