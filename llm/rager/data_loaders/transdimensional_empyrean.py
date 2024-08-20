import io
import requests
import docx
from typing import List, Dict

# Ensure decorators are imported
if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

def clean_line(line: str) -> str:
    """
    Cleans up a line of text by stripping unwanted characters.
    """
    line = line.strip()
    line = line.strip('\uFEFF')
    return line

def read_faq(file_id: str) -> List[Dict[str, str]]:
    """
    Reads FAQ data from a Google Doc file and extracts questions and answers.

    Args:
        file_id (str): The Google Docs file ID.

    Returns:
        List[Dict[str, str]]: A list of dictionaries containing FAQ data.
    """
    url = f'https://docs.google.com/document/d/{file_id}/export?format=docx'
    
    response = requests.get(url)
    response.raise_for_status()
    
    with io.BytesIO(response.content) as f_in:
        doc = docx.Document(f_in)

    questions = []

    question_heading_style = 'heading 2'
    section_heading_style = 'heading 1'
    
    heading_id = ''
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
            if answer_text_so_far != '' and section_title != '' and question_title != '':
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
    if answer_text_so_far != '' and section_title != '' and question_title != '':
        questions.append({
            'text': answer_text_so_far,
            'section': section_title,
            'question': question_title,
        })

    return questions

@data_loader
def ingest_faq_data(*args, **kwargs) -> List[Dict[str, List[Dict[str, str]]]]:
    """
    Data loader function to fetch and structure FAQ documents from Google Docs.

    Args:
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.

    Keyword Args:
        faq_documents (Dict[str, str]): Dictionary mapping course names to Google Docs file IDs.

    Returns:
        List[Dict[str, List[Dict[str, str]]]]: List of dictionaries with course names and their documents.
    """
    faq_documents = kwargs.get('faq_documents', {
        'llm-zoomcamp': '1T3MdwUvqCL3jrh3d3VCXQ8xE0UqRzI3bfgpfBq3ZWG0',
    })
    
    documents = []

    for course, file_id in faq_documents.items():
        course_documents = read_faq(file_id)
        documents.append({'course': course, 'documents': course_documents})

    # Print the number of FAQ documents processed in Mage's output
    num_documents = len(documents)
    print(f"Total number of FAQ documents processed: {num_documents}")
    
    return documents

@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block and checking the number of FAQ documents imported.
    """
    assert output is not None, 'The output is undefined'
    assert isinstance(output, list), 'Output should be a list'
    assert len(output) > 0, 'Output list should not be empty'
    
    # Get the total number of FAQ documents processed
    total_documents = len(output)
    print(f"Total number of FAQ documents processed: {total_documents}")

    # Additional assertions can be added here based on specific expectations
    assert total_documents > 0, 'No FAQ documents were processed'
