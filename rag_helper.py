from abc import ABC, abstractmethod
from google import genai
from google.genai import types

SYSTEM_PROMPT = """
Your task is to answer questions from the course participants
based on the provided context.

Use the context to find relevant information and provide accurate
answers. If the answer is not found in the context,
respond with "I don't know."
"""

PROMPT_TEMPLATE = """
QUESTION: 
{question}

CONTEXT:
{context}
""".strip()


class LLM_Provider(ABC):
    @abstractmethod
    def generate_response(self,model :str,system_prompt: str,user_prompt : str) -> str:
        pass

class GeminiLLM(LLM_Provider):
    def __init__(self,client):
        self.client = client
    def generate_response(self,model: str,system_prompt : str, user_prompt : str) -> str:
        response = self.client.models.generate_content(
            model= model,
            contents = user_prompt,
            config = types.GenerateContentConfig(
                system_instruction=system_prompt, 
                temperature=0.0 
            )
        )
        return response.text

class RAGMinSearch:
    def __init__(
        self,
        index,
        llm_provider,
        system_prompt = SYSTEM_PROMPT,
        user_prompt  = PROMPT_TEMPLATE,
        course = 'llm-zoomcamp',
        model='gemini-2.5-flash',
    ):
        # We can modify these fields
        self.index = index
        self.llm_provider = llm_provider
        # These two fields cannot be modified cause we want to scale this project not only for FAQ
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt

        self.course = course
        self.model = model

    def search(self,question):
        return self.index.search_index(question,self.course)

    def build_context(self,search_result):
        lines = []
        for item in search_result:
            lines.append("Section: " + item['section'])
            lines.append("Q: " + item['question'])
            lines.append("A: " + item['answer'])
            lines.append("")
        return "\n".join(lines)

    def build_prompt(self,question, search_result):
        context =  self.build_context(search_result)
        return self.user_prompt.format(
            question=question,
            context=context
        )
    
    def rag_response(self,question):
        search_result = self.search(question)
        final_prompt = self.build_prompt(question,search_result)
        return self.llm_provider.generate_response(self.model,self.system_prompt,final_prompt)

        
class RAGSQLiteSearch(RAGMinSearch):
    def search(self,question):
        return self.index.search_index(question)




    