import requests
from minsearch import Index
from sqlitesearch import TextSearchIndex
from abc import ABC, abstractmethod
import os
def load_faq_data():
    docs_url = "https://datatalks.club/faq/json/courses.json";
    response = requests.get(docs_url)
    course_raw = response.json()

    url_prefix = "https://datatalks.club/faq"
    documents = []

    for course in course_raw:
        course_url = f"{url_prefix}{course['path']}"
        course_res = requests.get(course_url)
        course_res.raise_for_status()
        data = course_res.json()
        documents.extend(data)
    return documents

class IndexBuilder(ABC):
    @abstractmethod
    def build_index(self,documents):
        pass
    def get_index(self):
        pass
    def search_index(self,question):
        pass

class MinSearchIndex(IndexBuilder):
    def __init__(self):
        self.index = None
    def build_index(self,documents):
        self.index = Index(
            text_fields = ['question','section','answer'],
            keyword_fields = ['course']
        )
        self.index.fit(documents)
    def search_index(self,question,course=None):
        boost_dict = {'question' : 3.0 , 'section' : 0.75}
        filter_dict = {'course' : course}
        res = self.index.search(
            question,
            boost_dict=boost_dict,
            filter_dict=filter_dict,
            num_results=5,
        )
        return res
    def get_index(self):
        return self.index

class SqliteIndex(IndexBuilder):
    def __init__(self):
        self.index = None
    def build_index(self,documents):
        if os.path.exists('faq.db'):
            os.remove('faq.db')
        self.index = TextSearchIndex(
            text_fields = ['question','section','answer'],
            keyword_fields = ['course'],
            db_path = 'faq.db'
        )
        for doc in documents:
            self.index.add(doc)
    def search_index(self,question,course=None):
        search_result = self.index.search(
            question,
            num_results=5
        )
        return search_result
    def get_index(self):
        return self.index
    def close_index(self):
        self.index.close()
    
