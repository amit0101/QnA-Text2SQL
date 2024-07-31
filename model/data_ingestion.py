import os
import sys
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

def read_text_file(file_path):
    loader = TextLoader(file_path)
    documents = loader.load()
    print(str(len(documents)), "text documents read.")
    return documents

def read_pdf_file(file_path):
    loader = PyPDFLoader(file_path)
    pages = loader.load()
    print(str(len(pages)), "PDF pages loaded.")
    return pages

def read_md_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        md_text = file.read()
        print(str(len(md_text)), "markdown characters read.")
    return md_text

def ingest_data(data_directory, db):
    for root, _, files in os.walk(data_directory):
        for file in files:
            file_path = os.path.join(root, file)
            print("File path:", file_path)
            if file.endswith('.txt'):
                documents = read_text_file(file_path)
                print(f"Read text from {file}: {documents[:100]}...")
                text_splitter = RecursiveCharacterTextSplitter(
                    separators=["\n\n", "\n", "•", " ", ""],
                    chunk_size=1000,
                    chunk_overlap=100,
                    length_function=len)
                splits = text_splitter.split_documents(documents)
            elif file.endswith('.MD'):
                text = read_md_file(file_path)
                print(f"Read text from {file}: {text[:100]}...")
                markdown_splitter = MarkdownHeaderTextSplitter(
                    headers_to_split_on=[
                        ("#", "Header 1"),
                        ("##", "Header 2"),
                        ("##", "Header 3"),
                        ("####", "Header 4")
                    ]
                )
                splits = markdown_splitter.split_text(text)
                print("MD splits:", splits)
            elif file.endswith('.pdf'):
                pages = read_pdf_file(file_path)
                text_splitter = RecursiveCharacterTextSplitter(
                    separators=["\n\n", "\n", "•", " ", ""],
                    chunk_size=1500,
                    chunk_overlap=300,
                    length_function=len)
                splits = text_splitter.split_documents(pages)
            else:
                continue
            print(f"Indexing file: {file}...")
            index_data(splits, db)
        print("Data ingestion completed.")

def index_data(splits, db):
    print("Length of splits:", str(len(splits)))
    db.add_documents(splits)
    db.persist()
    print("Collection count:", str(db._collection.count()))
