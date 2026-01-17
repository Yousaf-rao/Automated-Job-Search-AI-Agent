import os
from dotenv import load_dotenv

# Load environment variables
# Load environment variables
load_dotenv(override=True)

# FIX: Prevent crash on Windows due to multiple OpenMP runtimes (FAISS/Torch conflict)
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")

# App Configuration
APP_TITLE = "Aura AI: Career Architect"
APP_ICON = "⚡"

# Premium High-Fidelity CSS Design
# Premium High-Fidelity CSS Design (Cream & Blue Theme)
CUSTOM_CSS = """
<style>
    /* -------------------------------------------------------------------------- */
    /*                                 FONTS & CORE                               */
    /* -------------------------------------------------------------------------- */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    :root {
        --bg-color: #0F172A; /* Slate 900 */
        --card-bg: #1E293B;  /* Slate 800 */
        --text-headline: #F8FAFC; /* Slate 50 */
        --text-body: #94A3B8; /* Slate 400 */
        --primary-blue: #3B82F6;
        --secondary-red: #EF4444; 
        --accent-gradient: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
        --glass-border: rgba(255, 255, 255, 0.1);
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.3);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.5);
    }

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
        color: var(--text-body) !important;
        background-color: var(--bg-color) !important;
    }

    /* -------------------------------------------------------------------------- */
    /*                             STREAMLIT OVERRIDES                            */
    /* -------------------------------------------------------------------------- */
    
    .stApp {
        background-color: var(--bg-color);
        background-image: none;
    }

    /* Hide standard header/footer */
    header {visibility: hidden;}
    footer {visibility: hidden;}

    /* Typography */
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-headline) !important;
        font-weight: 600 !important;
    }

    /* -------------------------------------------------------------------------- */
    /*                             COMPONENTS DESIGN                              */
    /* -------------------------------------------------------------------------- */

    /* -------------------------------------------------------------------------- */
    /*                             COMPONENTS DESIGN                              */
    /* -------------------------------------------------------------------------- */

    /* Custom Header Banner */
    .main-header {
        background: linear-gradient(135deg, #1E3A8A 0%, #172554 100%);
        padding: 24px 30px;
        border-radius: 12px;
        margin-bottom: 24px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
    }
    
    .main-header h1 {
        font-size: 2.2rem;
        margin: 0;
        background: linear-gradient(to right, #F8FAFC, #93C5FD);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: transparent;
        gap: 8px;
        border-bottom: 1px solid var(--glass-border);
        padding-bottom: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        color: var(--text-body);
        border: 1px solid transparent;
        border-radius: 6px;
        padding: 8px 16px;
        transition: all 0.2s ease;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(255, 255, 255, 0.05);
        color: white;
    }

    .stTabs [aria-selected="true"] {
        color: white !important;
        background-color: rgba(59, 130, 246, 0.1) !important;
        border: 1px solid rgba(59, 130, 246, 0.3) !important;
        border-bottom: 1px solid rgba(59, 130, 246, 0.3) !important;
    }
    
    /* Inputs & Selectboxes */
    .stTextInput > div > div > input, .stSelectbox > div > div {
        background-color: rgba(30, 41, 59, 0.6) !important; /* Semi-transparent Slate 800 */
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border-radius: 8px;
        backdrop-filter: blur(8px);
    }
    
    .stTextInput > div > div > input:focus, .stSelectbox > div > div:focus-within {
        border-color: var(--primary-blue) !important;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2) !important;
    }

    /* Dropdown alignment fix */
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: transparent !important;
        border: none !important;
        color: white !important;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(180deg, #1E293B 0%, #0F172A 100%) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        border-color: var(--primary-blue);
        box-shadow: 0 4px 8px rgba(59, 130, 246, 0.2);
        color: var(--primary-blue) !important;
    }

    /* Cards - LIQUID GLASS EFFECT */
    .glass-card {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
    }

    /* Hover Animation */
    .hover-effect {
        transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .hover-effect:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 24px -4px rgba(0, 0, 0, 0.4);
        border-color: rgba(59, 130, 246, 0.3);
    }

    /* MultiSelect Tags */
    .stMultiSelect [data-baseweb="tag"] {
        background-color: rgba(59, 130, 246, 0.2) !important;
        border: 1px solid rgba(59, 130, 246, 0.3);
        color: #93C5FD !important; /* Light Blue Text */
        border-radius: 6px;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: rgba(30, 41, 59, 0.4) !important;
        color: var(--text-headline) !important;
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 8px;
    }
    .streamlit-expanderContent {
        background-color: rgba(15, 23, 42, 0.4) !important;
        border: 1px solid rgba(255, 255, 255, 0.05);
        color: var(--text-body) !important;
    }
</style>
"""
