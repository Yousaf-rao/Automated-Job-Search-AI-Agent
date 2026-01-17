# 🚀 Automated Job Search AI Agent

**Career Architect v1.0** - A premium, AI-powered career assistant that helps you optimize your resume, find the perfect jobs, and prepare for interviews.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-green?style=for-the-badge&logo=openai)
![LangChain](https://img.shields.io/badge/LangChain-Integration-blueviolet?style=for-the-badge)

## ✨ Features

### 📄 AI Resume Parsing (RAG-Enhanced)
- **Deep Analysis**: Uses Retrieval Augmented Generation (RAG) to understand the context of your resume, not just keywords.
- **Smart Extraction**: Accurately extracts Contact Info, Education, Experience, and Skills.
- **Skill Matrix**: Automatically categorizes skills into Technical, DevOps/Cloud, Web, Databases, and Soft Skills.
- **Visual Results**: Displays parsed data in a beautiful, premium iOS-style UI with timeline cards and skill badges.

### 🔍 Smart Job Search
- **Multi-Platform**: Searches LinkedIn, Indeed, Glassdoor, and ZipRecruiter via SerpApi.
- **Advanced Filtering**: Filter by location, job headers, and date posted.
- **Real-Time Data**: Fetches the latest job listings matching your profile.

### 💾 Saved Jobs
- **Persistent Storage**: Save interesting job opportunities to a dedicated list.
- **Easy Management**: View, apply, or remove saved jobs anytime.

### 🎨 Premium UI/UX
- **Cream & Blue Theme**: A professional, high-fidelity aesthetic using Cream (`#FDFBF7`) and Deep Blue accents.
- **Platform Cards**: Interactive, clickable cards for selecting job search platforms (LinkedIn, Indeed, etc.).
- **Glassmorphism Design**: Modern, clean cards with frosted glass effects for a premium feel.
- **Interactive Components**: Smooth hover effects, pill-shaped tabs, and responsive layouts.
- **Optimized Typography**: Uses 'Inter' font for maximum readability.

## 🛠️ Installation

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/Yousaf-rao/Automated-Job-Search-AI-Agent.git
    cd Automated-Job-Search-AI-Agent
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r job_search_assistant/requirements.txt
    ```

3.  **Configure Environment**
    Create a `.env` file in `job_search_assistant/` with your API keys:
    ```env
    OPENAI_API_KEY=your_openai_api_key
    SERPAPI_API_KEY=your_serpapi_api_key
    ```

4.  **Run the Application**
    ```bash
    cd job_search_assistant
    streamlit run app.py
    ```

## 📂 Project Structure

```
Automated-Job-Search-AI-Agent/
├── job_search_assistant/
│   ├── agents/                 # AI Agent Logic (Resume, Interview)
│   ├── utils/                  # Core Utilities (Parser, Searcher, Storage)
│   │   ├── resume_parser.py    # RAG & Regex Parsing Logic
│   │   ├── serp_api_searcher.py# Job Search Integration
│   │   └── ...
│   ├── app.py                  # Main Streamlit Application
│   ├── config.py               # Configuration & UI Styling
│   └── requirements.txt        # Project Dependencies
├── .gitignore
└── README.md
```

## 🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.
