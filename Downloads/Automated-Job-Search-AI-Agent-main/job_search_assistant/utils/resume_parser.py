"""
Resume Parser Module
--------------------
This module provides a robust `ResumeParser` class to extract structured information 
from PDF resumes. It uses a Hybrid Approach:
1.  **Regex**: For high-precision extraction of contact details (Email, Phone).
2.  **RAG (Retrieval Augmented Generation)**: Uses LangChain, FAISS, and OpenAI 
    to deeply analyze the resume text and answer specific data extraction questions 
    (Skills, Education, Experience).

Dependencies:
- langchain
- langchain-community
- openai
- faiss-cpu
- tiktoken
"""

import os
import re
import tempfile
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

# LangChain Imports - Updated for newer versions
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# Internal Imports
try:
    from config import OPENAI_API_KEY
except ImportError:
    # If config isn't found (e.g. running standalone), we expect env var
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- EMBEDDED EXTRACTOR ---
class ResumeKeywordExtractor:
    def __init__(self):
        self.skills_db = {
            "technical_skills": [
                "python", "java", "c++", "javascript", "typescript", "html", "css", "sql", "nosql",
                "git", "linux", "bash", "shell scripting", "react", "angular", "vue", "node.js"
            ],
            "data_science": [
                "pandas", "numpy", "scikit-learn", "matplotlib", "seaborn", "tensorflow", "keras",
                "pytorch", "opencv", "nlp", "computer vision", "deep learning", "machine learning",
                "data mining", "data wrangling", "big data", "tableau", "power bi", "dax"
            ],
            "devops_and_cloud": [
                "aws", "azure", "gcp", "google cloud", "cloud computing", "serverless",
                "lambda", "ec2", "s3", "dynamodb", "devops", "ci/cd", "jenkins", "github actions",
                "terraform", "ansible", "puppet", "chef", "kubernetes", "docker", "microservices"
            ],
            "web_development": [
                "django", "flask", "fastapi", "html5", "css3", "bootstrap", "tailwind",
                "rest api", "graphql", "websockets"
            ],
            "databases": [
                "mysql", "postgresql", "mongodb", "dynamodb", "redis", "elasticsearch", "sqlite"
            ],
            "soft_skills": [
                "project management", "agile", "scrum", "jira", "confluence", "leadership",
                "team management", "communication", "problem-solving", "critical thinking",
                "teamwork", "time management", "stakeholder management"
            ]
        }

    def extract_keywords(self, text: str) -> dict:
        """
        Extracts skills from text based on the internal database.
        Returns a dictionary of categories and found skills.
        """
        found_skills = {}
        text_lower = text.lower()

        for category, keywords in self.skills_db.items():
            found = []
            for keyword in keywords:
                # Use regex to find whole words/phrases to avoid partial matches (e.g., "go" in "google")
                pattern = r'(?<!\w)' + re.escape(keyword) + r'(?!\w)'
                if re.search(pattern, text_lower):
                    found.append(keyword.title()) # Capitalize for display
            
            if found:
                found_skills[category] = list(set(found)) # Remove duplicates
        
        return found_skills

class ResumeParser:
    """
    Parses resumes using a combination of Regex pattern matching and 
    LLM-based Retrieval Augmented Generation (RAG).
    """

    def __init__(self):
        """
        Initialize the ResumeParser with OpenAI components.
        """
        self.api_key = OPENAI_API_KEY
        
        # Initialize Keyword Extractor (Embedded)
        self.keyword_extractor = ResumeKeywordExtractor()

        if not self.api_key:
            logger.warning("OPENAI_API_KEY is missing. RAG features will not work.")
            self.llm = None
            self.embeddings = None
        else:
            try:
                # Initialize Embeddings
                self.embeddings = OpenAIEmbeddings(openai_api_key=self.api_key)
                # Initialize LLM
                self.llm = ChatOpenAI(
                    model_name="gpt-3.5-turbo", 
                    temperature=0.0, 
                    openai_api_key=self.api_key
                )
            except Exception as e:
                logger.error(f"Failed to initialize AI components: {e}")
                self.llm = None
                self.embeddings = None

    def save_upload_file(self, uploaded_file) -> str:
        """
        Save an uploaded file (from Streamlit) to a temporary location.
        
        Args:
            uploaded_file: The file object from Streamlit file_uploader.
            
        Returns:
            str: The absolute path to the saved temporary file.
        """
        try:
            # Create a temp file with the correct extension
            suffix = Path(uploaded_file.name).suffix
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                tmp_file.write(uploaded_file.getbuffer())
                return tmp_file.name
        except Exception as e:
            logger.error(f"Error saving uploaded file: {e}")
            raise e

    def _extract_contact_details(self, text: str) -> Dict[str, str]:
        """
        Extract contact details using Regex for high reliability.
        """
        details = {
            "email": None,
            "phone": None,
            "linkedin": None,
            "github": None,
            "portfolio": None
        }
        
        # Email Regex
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text)
        if email_match:
            details["email"] = email_match.group(0)

        # Phone Regex (Supports various formats like +1-555..., (555) 123-4567, etc.)
        # Simplified robust phone regex for general purpose finding
        phone_match = re.search(r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]', text)
        if phone_match:
            details["phone"] = phone_match.group(0).strip()
            
        # Links
        linkedin_match = re.search(r'(linkedin\.com/in/[a-zA-Z0-9_-]+)', text, re.IGNORECASE)
        if linkedin_match:
            details["linkedin"] = "https://www." + linkedin_match.group(0) if not linkedin_match.group(0).startswith("http") else linkedin_match.group(0)

        github_match = re.search(r'(github\.com/[a-zA-Z0-9_-]+)', text, re.IGNORECASE)
        if github_match:
            details["github"] = "https://www." + github_match.group(0) if not github_match.group(0).startswith("http") else github_match.group(0)

        return details

    def _extract_skills_rag(self, llm, retriever) -> Dict[str, List[str]]:
        """
        Extract and categorize skills using RAG via LCEL.
        """
        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)

        prompt_text = """
        You are an expert Resume Parser.
        Use the following pieces of context from the resume to answer the request.
        
        CONTEXT:
        {context}
        
        REQUEST:
        Extract all technical and soft skills from the resume.
        CRITICAL INSTRUCTION: Be extremely specific. Do NOT list broad categories.
        List specific tools, languages, and frameworks.

        Categorize them into the following valid JSON structure:
        {{
            "technical_skills": ["List specific programming languages and core technologies"],
            "devops_and_cloud": ["List specific DevOps tools, CI/CD pipelines, and Cloud services"],
            "web_development": ["List specific frameworks, libraries, and web technologies"],
            "databases": ["List specific database technologies"],
            "soft_skills": ["List specific interpersonal skills"]
        }}
        Return ONLY the JSON object. Do not add markdown formatting.
        """
        
        prompt = PromptTemplate.from_template(prompt_text)

        chain = (
            {"context": retriever | format_docs}
            | prompt
            | llm
            | StrOutputParser()
        )

        try:
            # Invoking with a context-relevant query
            response = chain.invoke("skills technical languages tools devops database")
            clean_json = response.replace("```json", "").replace("```", "").strip()
            import json
            return json.loads(clean_json)
        except Exception as e:
            logger.error(f"Error extracting skills via RAG: {e}")
            return {
                "technical_skills": [],
                "devops_and_cloud": [],
                "web_development": [],
                "databases": [],
                "soft_skills": []
            }

    def _extract_education_rag(self, llm, retriever) -> List[Dict[str, str]]:
        """
        Extract education history using RAG via LCEL.
        """
        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)
        
        # RESTORED PROMPT
        prompt_text = """
        You are an expert resume parser. Extract the education history from the provided context.
        
        INSTRUCTIONS:
        - Extract Degree, Institution, and Year.
        - Return a JSON list of objects: [{{"degree": "...", "institution": "...", "year": "..."}}]
        - If none found, return [].
        
        Context:
        {context}
        """
        prompt = PromptTemplate.from_template(prompt_text)
        
        chain = (
            {"context": retriever | format_docs}
            | prompt
            | llm
            | StrOutputParser()
        )

        try:
            response = chain.invoke("education university degree college school")
            clean_json = response.replace("```json", "").replace("```", "").strip()
            import json
            return json.loads(clean_json)
        except Exception as e:
            logger.error(f"Error extracting education via RAG: {e}")
            return []

    def _extract_experience_rag(self, llm, retriever) -> List[Dict[str, str]]:
        """
        Extract work experience using RAG via LCEL.
        """
        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)
        
        # RESTORED PROMPT
        prompt_text = """
        You are an expert resume parser. Extract the professional work experience from the provided context.
        
        INSTRUCTIONS:
        - Look for "Professional Experience", "Work History", etc.
        - Extract Job Title, Company, Duration, and Description.
        - Return a JSON list of objects: [{{"job_title": "...", "company": "...", "duration": "...", "description": "..."}}]
        - If none found, return [].
        
        Context:
        {context}
        """
        prompt = PromptTemplate.from_template(prompt_text)
        
        chain = (
            {"context": retriever | format_docs}
            | prompt
            | llm
            | StrOutputParser()
        )


        try:
            response = chain.invoke("work experience employment history jobs career")
            clean_json = response.replace("```json", "").replace("```", "").strip()
            import json
            return json.loads(clean_json)
        except Exception as e:
            logger.error(f"Error extracting experience via RAG: {e}")
            return []

    def _extract_skills_keywords(self, text: str) -> Dict[str, List[str]]:
        """
        Extract skills using the external ResumeKeywordExtractor for deeper matching.
        """
        if self.keyword_extractor:
            return self.keyword_extractor.extract_keywords(text)
            
        # Fallback if extractor fails to init (shouldn't happen)
        return {
            "technical_skills": [],
            "devops_and_cloud": [],
            "web_development": [],
            "databases": [],
            "soft_skills": []
        }

    def parse(self, file_path: str) -> Dict[str, Any]:
        """
        Main entry point to parse a resume PDF file.
        
        Args:
            file_path (str): Absolute path to the PDF file.
            
        Returns:
            Dict[str, Any]: Structured dictionary containing extracted resume data.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        parsed_data = {
            "contact_info": {},
            "skills": {},
            "education": [],
            "experience": [],
            "raw_text": ""
        }

        try:
            # 1. Load PDF
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            full_text = " ".join([doc.page_content for doc in documents])
            parsed_data["raw_text"] = full_text

            # 2. Regex Extraction (Contacts)
            parsed_data["contact_info"] = self._extract_contact_details(full_text)

            # 3. Keyword Extraction (Fast & Deterministic)
            # We run this always, as it provides a baseline of specific tools
            keyword_skills = self._extract_skills_keywords(full_text)

            # 4. RAG Extraction (Deep Analysis for Complex Fields)
            rag_skills = {}
            if self.llm and self.embeddings:
                # Text Splitter - Increased chunk size to keep sections together
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
                texts = text_splitter.split_documents(documents)
                
                # Create Vector Store
                docsearch = FAISS.from_documents(texts, self.embeddings)
                
                # Get Retriever
                retriever = docsearch.as_retriever()
                
                # Execute RAG Queries via LCEL Helpers
                logger.info("Extracting skills via RAG...")
                rag_skills = self._extract_skills_rag(self.llm, retriever)
                
                logger.info("Extracting education via RAG...")
                parsed_data["education"] = self._extract_education_rag(self.llm, retriever)
                
                logger.info("Extracting experience via RAG...")
                parsed_data["experience"] = self._extract_experience_rag(self.llm, retriever)
            
            else:
                logger.warning("LLM not initialized. Skipping RAG extraction steps.")
                parsed_data["education"] = []
                parsed_data["experience"] = []

            # 5. Merge Skills (Keywords + RAG)
            # We prioritize RAG but ensure keywords are present if RAG missed them
            final_skills = rag_skills.copy() if rag_skills else {k: [] for k in keyword_skills}
            
            for category, tools in keyword_skills.items():
                if category not in final_skills:
                    final_skills[category] = tools
                else:
                    # Union of sets to avoid duplicates
                    current_set = set(final_skills[category])
                    new_set = set(tools)
                    final_skills[category] = list(current_set.union(new_set))

            parsed_data["skills"] = final_skills

            return parsed_data

        except Exception as e:
            logger.error(f"Critical error parsing resume: {e}")
            return {"error": str(e)}

# Unit Test / Example Usage
if __name__ == "__main__":
    # Mocking usage if we had a dummy file
    parser = ResumeParser()
    if parser.llm:
        print("ResumeParser initialized successfully with AI.")
    else:
        print("ResumeParser initialized without AI.")
