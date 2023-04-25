
from typing import List
import fitz
from pydantic import BaseModel
from langchain.text_splitter import CharacterTextSplitter
from fastapi import UploadFile


class Document(BaseModel):
    page_content: str
    metadata: dict



def chunk_by_tokens(documents) -> List[str]:
    """
    Chunks the data

    Parameters:
    -----------
    text : str
        The string to be tokenized.

    Returns:
    --------
    text : List[str]
        Chunks that meet the max token length requirement.
    """
    text_splitter = CharacterTextSplitter.from_tiktoken_encoder(chunk_size=1500, chunk_overlap=0)
    pages = [doc.page_content for doc in documents]
    # join the pages
    data = " ".join(pages)
    chunks = text_splitter.split_text(data)
    return chunks



def generate_chunks(file: UploadFile)  -> List[str]:
    """
    Parses a file and returns a dictionary containing the parsed data.

    Parameters:
    -----------
    path : str
        The path to the file to be parsed.

    Returns:
    --------
    dict
        A dictionary containing the parsed data.
    """
    doc = fitz.open(stream=file.file.read(), filetype="pdf")
    # Using Langchain Document in case we need to change anything in the future. 
    docs = [
        Document(
            page_content=page.get_text().encode("utf-8"),
            metadata=dict(
                {
                    "source": file.filename,
                    "file_path": file.filename,
                    "page_number": page.number + 1,
                    "total_pages": len(doc),
                },
                **{
                    k: doc.metadata[k]
                    for k in doc.metadata
                    if type(doc.metadata[k]) in [str, int]
                }
            ),
        )
        for page in doc
    ]
    # check if each length of the doc is below 2000 tokens 
    return chunk_by_tokens(docs)
