from fastapi import FastAPI, File, UploadFile
# minimal example
#import re
import pymupdf
import spacy


app = FastAPI()

@app.post("/v1/extract-sentences")
async def extract_sentences(pdf_file: UploadFile = File(...)):
    content = await pdf_file.read()

    # define output path for the text file
    output_path = f"data/{pdf_file.filename.replace('.pdf', '.txt')}"

    doc = pymupdf.open(stream=content, filetype="pdf") # open the PDF file from the uploaded content
    out = open(output_path, "w+b") # open the output file in write-binary mode
    text = ""
    for page in doc:
        text = page.get_text().encode("utf-8") # read the text from the PDF page and encode it to UTF-8
        out.write(text) # write the text to the output file
    out.seek(0)  # Move the file pointer back to the beginning of the file

    # minimal example
    # sentences = re.split(r'(?<=[.!?])\s+', out.read().decode("utf-8"))
    
    # with spacy
    nlp = spacy.load("en_core_web_sm")
    doc_spacy = nlp(out.read().decode("utf-8"))
    sentences = [sent.text.strip() for sent in doc_spacy.sents]

    out.close()
    doc.close()
    
    return {"sentences": sentences}   