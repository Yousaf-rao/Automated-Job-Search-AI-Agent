import re
from typing import Dict, List, Set, Union

class ResumeKeywordExtractor:
    """
    A utility class to extract relevant technical keywords, skills, and job titles 
    from a resume. This class uses predefined lists of technical terms to identify 
    matches in the resume text or data structure.
    
    Designed to be beginner-friendly with extensive comments.
    """

    def __init__(self):
        """
        Initialize the extractor with comprehensive lists of technical keywords.
        These lists are categorized to help organize the extracted information.
        """
        
        # 1. Job Titles: Common titles to look for in the candidate's history or objective.
        self.job_titles = [
            "software engineer", "software developer", "web developer",
            "frontend developer", "backend developer", "full stack developer",
            "data scientist", "data analyst", "forntend developer",
            "machine learning engineer", "devops engineer", "site reliability engineer",
            "cloud engineer", "system administrator", "database administrator",
            "qa engineer", "mobile developer", "game developer",
            "product manager", "project manager", "business analyst"
        ]

        # 2. Languages: Programming and scripting languages.
        self.languages = [
            "python", "java", "javascript", "typescript", "c++", "c#", "ruby",
            "go", "rust", "swift", "kotlin", "php", "scala", "perl", "r",
            "html", "css", "sql", "bash", "shell", "matlab", "dart", "lua", "objective-c",
            "assembly", "vba", "haskell"
        ]

        # 3. Frameworks & Libraries: Tools used for specific tasks (Web, AI, etc.)
        self.frameworks = [
            # Web
            "react", "angular", "vue", "django", "flask", "spring", "express",
            "rails", "laravel", "asp.net", "bootstrap", "jquery", "fastapi",
            "tailwind", "next.js", "node.js", "svelte", "backbone.js", "ember.js",
            # AI / Data Science
            "tensorflow", "pytorch", "keras", "scikit-learn", "pandas", "numpy",
            "matplotlib", "seaborn", "nltk", "spacy", "opencv", "hugging face", 
            "langchain", "openai", "scipy", "plotly"
        ]

        # 4. Platforms & Operations: Cloud providers, OS, and DevOps tools.
        self.platforms = [
            "aws", "azure", "gcp", "google cloud", "heroku", "docker",
            "kubernetes", "jenkins", "gitlab", "github", "bitbucket", "linux",
            "windows", "mac", "ios", "android", "vercel", "netlify",
            "digitalocean", "firebase", "elasticsearch", "kafka", "redis",
            "terraform", "ansible", "circleci", "travis ci"
        ]

        # 5. Concepts: General technical concepts and methodologies.
        self.concepts = [
            "api", "rest", "graphql", "microservices", "ci/cd", "agile", "scrum",
            "devops", "testing", "unit testing", "integration testing", "git",
            "version control", "database", "sql", "nosql", "machine learning",
            "deep learning", "nlp", "object oriented programming", "oop",
            "system design", "algorithms", "data structures", "distributed systems",
            "cloud computing", "serverless", "security", "encryption"
        ]

        # 6. Stopwords: Words to ignore when processing text to reduce noise.
        # These are common non-technical words often found in resumes.
        self.resume_stopwords = [
            "resume", "curriculum", "vitae", "cv", "objective", "summary",
            "experience", "education", "skills", "references", "projects",
            "achievements", "responsibilities", "phone", "email", "address",
            "linkedin", "github", "portfolio", "website", "date",
            "both", "each", "few", "more", "most", "other", "some", "such",
            "no", "nor", "not", "only", "own", "same", "so", "than", "too",
            "very", "s", "t", "can", "will", "just", "don", "should", "now",
            "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you",
            "your", "yours", "yourself", "yourselves", "he", "him", "his",
            "himself", "she", "her", "hers", "herself", "it", "its", "itself",
            "they", "them", "their", "theirs", "themselves", "what", "which",
            "who", "whom", "this", "that", "these", "those", "am", "is", "are",
            "was", "were", "be", "been", "being", "have", "has", "had", "having",
            "do", "does", "did", "doing", "a", "an", "the", "and", "but", "if",
            "or", "because", "as", "until", "while", "of", "at", "by", "for",
            "with", "about", "against", "between", "into", "through", "during",
            "before", "after", "above", "below", "to", "from", "up", "down",
            "in", "out", "on", "off", "over", "under", "again", "further",
            "then", "once", "here", "there", "when", "where", "why", "how",
            "all", "any"
        ]

    def extract_keywords(self, resume_data: Union[Dict, str], max_keywords: int = 15) -> Dict[str, List[str]]:
        """
        Extract the most relevant keywords from resume data for job searching.
        
        Args:
            resume_data (dict or str): The parsed resume data containing fields 
                                       like skills, experience, etc., or raw text.
            max_keywords (int): The maximum number of keywords to return (not strictly enforced 
                                across all categories, but good for limiting).
            
        Returns:
            dict: A dictionary with categorized extracted keywords.
        """
        
        # Initialize an empty dictionary to hold our results
        extracted_info = {
            "tech_stack": [],
            "job_titles": [],
            "soft_skills": [],  # Included for completeness
            "concepts": []
        }
        
        # Initialize text variable to combine all relevant text sources
        full_text = ""

        # --- STEP 1: PREPARE TEXT ---
        # If the input is a dictionary (from our parser), extract text from specific fields.
        if isinstance(resume_data, dict):
            # 1. Get raw text if available
            full_text += resume_data.get("raw_text", "") + " "
            
            # 2. Get skills list and join them
            skills = resume_data.get("skills", {})
            if isinstance(skills, dict):
                # Flatten the skills dictionary into a single string
                for cat, items in skills.items():
                    if isinstance(items, list):
                        full_text += " ".join(items) + " "
            
            # 3. Get experience descriptions
            experience_list = resume_data.get("experience", [])
            for exp in experience_list:
                if isinstance(exp, dict):
                    full_text += exp.get("description", "") + " "
                    full_text += exp.get("job_title", "") + " "
        
        # If input is just a string, use it directly
        elif isinstance(resume_data, str):
            full_text = resume_data
            
        # Convert to lowercase for consistent matching
        text_lower = full_text.lower()
        
        # --- STEP 2: EXTRACT KEYWORDS ---
        # We will check if tokens from our lists exist in the resume text.
        
        # Helper function to find matches
        def find_matches(source_list: List[str]) -> List[str]:
            matches = []
            for item in source_list:
                # Use regex \b boundary to match exact words (e.g., "java" but not "javascript")
                if re.search(r'\b' + re.escape(item) + r'\b', text_lower):
                    matches.append(item)
            return list(set(matches)) # Remove duplicates

        # Extract strictly from our lists
        found_languages = find_matches(self.languages)
        found_frameworks = find_matches(self.frameworks)
        found_platforms = find_matches(self.platforms)
        found_concepts = find_matches(self.concepts)
        found_titles = find_matches(self.job_titles)

        # --- STEP 3: FORMAT THE OUTPUT ---
        # Combine technical skills into 'tech_stack'
        extracted_info["tech_stack"] = found_languages + found_frameworks + found_platforms
        
        extracted_info["concepts"] = found_concepts
        extracted_info["job_titles"] = found_titles

        # --- STEP 4: SUGGESTIONS BASED ON KEYWORDS ---
        # If we didn't find specific titles, we can guess based on skills.
        if not extracted_info["job_titles"]:
            if "python" in found_languages and ("pandas" in found_frameworks or "tensorflow" in found_frameworks):
                extracted_info["job_titles"].append("Data Scientist")
            elif "react" in found_frameworks or "angular" in found_frameworks:
                extracted_info["job_titles"].append("Frontend Developer")
            elif "django" in found_frameworks or "node.js" in found_frameworks:
                extracted_info["job_titles"].append("Backend Developer")

        return extracted_info

    def get_search_query(self, extracted_keywords: Dict[str, List[str]]) -> str:
        """
        Generates a search query string for job portals based on extracted keywords.
        
        Args:
            extracted_keywords (dict): The result from extract_keywords().
            
        Returns:
            str: A formatted search query string (e.g., "Python AND Django AND AWS").
        """
        # Prioritize Job Titles first
        query_parts = []
        
        if extracted_keywords["job_titles"]:
            # Take the first matched job title
            query_parts.append(f'"{extracted_keywords["job_titles"][0]}"')
        
        # Add top 2-3 technical skills
        # We process 'tech_stack' to pick the most distinct ones
        tech_stack = extracted_keywords.get("tech_stack", [])
        
        # Pick up to 3 skills
        for i in range(min(3, len(tech_stack))):
           query_parts.append(tech_stack[i].title())
           
        return " ".join(query_parts)

# --- DEBUG / TESTING ---
if __name__ == "__main__":
    extractor = ResumeKeywordExtractor()
    
    # Mock data to simulate parsed resume
    mock_resume_data = {
        "raw_text": "Experienced Software Engineer skilled in Python, Django, and AWS. Familiar with CI/CD and Agile methodologies.",
        "skills": {
            "tech": ["Python", "JavaScript"]
        },
        "experience": [
            {
                "job_title": "Backend Developer",
                "description": "Built microservices using Flask and Docker."
            }
        ]
    }
    
    print("--- Testing Keyword Extraction ---")
    keywords = extractor.extract_keywords(mock_resume_data)
    
    print("\nExtracted Keywords:")
    for category, items in keywords.items():
        print(f"{category.upper()}: {', '.join(items)}")
        
    print("\nGenerated Search Query:")
    print(extractor.get_search_query(keywords))
