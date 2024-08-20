import io
import requests
import docx
from typing import List, Dict
from mage_ai.data_preparation.decorators import data_loader, test

def clean_line(line: str) -> str:
    """
    Clean the given line by stripping leading/trailing whitespace and BOM characters.

    Args:
        line (str): The line of text to clean.

    Returns:
        str: The cleaned line of text.
    """
    line = line.strip()
    line = line.strip('\uFEFF')  # Remove Byte Order Mark if present
    return line

@data_loader
def read_faq() -> List[Dict[str, str]]:
    """
    Read FAQ data from a Google Doc and format it into a list of questions and answers.

    Returns:
        List[Dict[str, str]]: A list of dictionaries with FAQ details.
    """
    file_id = '1qZjwHkvP0lXHiE4zdbWyUXSVfmVGzougDD6N37bat3E'
    url = f'https://docs.google.com/document/d/{file_id}/export?format=docx'
    
    response = requests.get(url)
    response.raise_for_status()
    
    with io.BytesIO(response.content) as f_in:
        doc = docx.Document(f_in)

    questions = []

    question_heading_style = 'heading 2'
    section_heading_style = 'heading 1'
    
    section_title = ''
    question_title = ''
    answer_text_so_far = ''
    
    for p in doc.paragraphs:
        style = p.style.name.lower()
        p_text = clean_line(p.text)
        
        if len(p_text) == 0:
            continue

        if style == section_heading_style:
            section_title = p_text
            continue

        if style == question_heading_style:
            answer_text_so_far = answer_text_so_far.strip()
            if answer_text_so_far and section_title and question_title:
                questions.append({
                    'text': answer_text_so_far,
                    'section': section_title,
                    'question': question_title,
                })
                answer_text_so_far = ''

            question_title = p_text
            continue
        
        answer_text_so_far += '\n' + p_text

    answer_text_so_far = answer_text_so_far.strip()
    if answer_text_so_far and section_title and question_title:
        questions.append({
            'text': answer_text_so_far,
            'section': section_title,
            'question': question_title,
        })

    return questions

@data_loader
def ingest_documents() -> List[Dict[str, any]]:
    """
    Ingest documents by reading FAQ data and formatting it.

    Returns:
        List[Dict[str, any]]: A list of documents with course and FAQ details.
    """
    documents = []
    course_documents = read_faq()
    documents.append({'course': 'llm-zoomcamp', 'documents': course_documents})
    return documents

@test
def test_output(output: List[Dict[str, any]], *args) -> None:
    """
    Test the output of the ingest_documents function.

    Args:
        output (List[Dict[str, any]]): The output from ingest_documents.
    """
    assert output is not None, 'The output is undefined'
    assert isinstance(output, list), 'Output should be a list'
    assert all(isinstance(doc, dict) for doc in output), 'Each item in output should be a dictionary'
    assert 'course' in output[0], 'The output should contain a "course" key'
    assert 'documents' in output[0], 'The output should contain a "documents" key'
