import os, sys, traceback
import uvicorn
import logging
from pydantic import BaseModel
from fastapi import FastAPI, UploadFile, File, Request, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from parsing.parse import parse_data
from typing import Optional
import subprocess


logging.basicConfig(stream=sys.stdout, level=logging.INFO)

app = FastAPI(
    title="structure",
)

# Add CORS middleware
origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    print("Server starting up...")

class SchemaResponse(BaseModel):
    success: bool
    message: Optional[str] = None


@app.post("/schema", response_model=SchemaResponse)
async def schema(file: UploadFile = File(...)) -> SchemaResponse:
    allowed_extensions = ('openapi', 'json', 'yaml', 'yml')

    if file.filename.split('.')[-1].lower() not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Invalid file format. Only OpenAPI, JSON, and YAML files are allowed.")

    file_contents = await file.read()

    subprocess.run(["datamodel-codegen", "--input", "-", "--output", "models/model.py"], input=file_contents, check=True)

    return SchemaResponse(success=True, message="Uploaded file has been saved to models/model.py")


@app.post("/parser")
async def parser(file: UploadFile = File(...)) -> dict:
    """
    Uploads a document for parsing.

    Parameters:
    -----------
    file : 
        The file to be uploaded.
        Supported formats are all for now. Mainly tested on PDF and text. 

    Returns:
    --------
    dict
        A dictionary containing the status of the upload process. If the file is successfully uploaded and indexed,
        the message "File indexed" is returned. Otherwise, an error message is returned with the traceback.
    """
    
    logging.info("Uploading file...")
    try:
        # We parse the file 
        logging.info("Parsing document...")
        parsed_data =  await parse_data(file)

        return {'message' : parsed_data}
    
    except Exception as e:
        logging.error(traceback.format_exc())
        return {'message': 'Your file is in a wrong format. Please upload a PDF with OCR, a DOCX or Text document.' }


if __name__ == "__main__":
    logging.info("Running app...")
    uvicorn.run(app, host="0.0.0.0", port=8080)