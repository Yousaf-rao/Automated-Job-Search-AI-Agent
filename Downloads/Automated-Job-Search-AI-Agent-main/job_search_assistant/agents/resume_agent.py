import os
from langchain_community.chat_models import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from config import OPENAI_API_KEY
from langchain_core.output_parsers import StrOutputParser

class ResumeAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            temperature=0.0,
            model_name="gpt-3.5-turbo",
            openai_api_key=OPENAI_API_KEY
        )

    def analyze_resume(self, resume_text):
        """
        Analyzes the resume text and provides structured feedback.
        """
        prompt_template = """
        You are an expert Career Coach and Resume Analyst. 
        Your task is to analyze the following resume text.

        RESUME TEXT:
        {resume_text}

        Please provide a detailed analysis in the following structured format (Markdown):

        ### 1. Executive Summary
        A brief overview of the candidate's profile (2-3 sentences).

        ### 2. Key Strengths
        - [Strength 1]
        - [Strength 2]
        - [Strength 3]

        ### 3. Areas for Improvement
        - [Weakness 1]: [Suggestion]
        - [Weakness 2]: [Suggestion]

        ### 4. Recommendation
        A concise final verdict on whether this resume is ready for job applications.
        """

        prompt = PromptTemplate(
            input_variables=["resume_text"],
            template=prompt_template
        )

        # Using LCEL (LangChain Expression Language)
        chain = prompt | self.llm | StrOutputParser()
        response = chain.invoke({"resume_text": resume_text})
        return response
