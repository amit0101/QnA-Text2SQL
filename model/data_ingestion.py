import os
import sys
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)


def read_pdf_file(file_path):
    loader = PyPDFLoader(file_path)
    pages = loader.load()
    print(str(len(pages)), "PDF pages loaded.")
    return pages


def ingest_data(data_directory, db):
    for root, _, files in os.walk(data_directory):
        for file in files:
            file_path = os.path.join(root, file)
            print("File path:", file_path)
            if file.endswith('.pdf'):
                pages = read_pdf_file(file_path)
                text_splitter = RecursiveCharacterTextSplitter(
                    separators=["\n\n", "\n", "•", " ", ""],
                    chunk_size=1500,
                    chunk_overlap=300,
                    length_function=len)
                splits = text_splitter.split_documents(pages)
                print(f"Indexing file: {file}...")
                index_data(splits, db)
            else:
                print(f"Not a PDF file. Ignoring: {file}...")
                continue
        print("Data ingestion completed.")


def index_data(splits, db):
    print("Length of splits:", str(len(splits)))
    db.add_documents(splits)
    db.persist()
    print("Collection count:", str(db._collection.count()))
