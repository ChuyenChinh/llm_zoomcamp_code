import requests
from minsearch import Index

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

def build_index(documents):
    index = Index(
        text_fields = ['question','answer','section'],
        keyword_fields = ['course']
    )
    index.fit(documents)
    return index
