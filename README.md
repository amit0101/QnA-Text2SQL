# RAG Personal QnA on Amit

#### Steps to run this repo locally with Docker:

Clone this repo

`git clone https://github.com/amit0101/QnA-Text2SQL.git`

Change to main directory

`cd QnA-Text2SQL`

Add your OpenAI API key to .env file
`OPENAI_API_KEY=""`

Run docker build
`docker-compose up --build`

Access the Streamlit app at https://localhost:8501

NOTE: The PDF files have already been indexed and stored into the ChromaDB object. To add more files or any new files to the vector database, empty the contents of `db` and `chroma` folders, run `python model/rag_model.py` and then rerun the Docker commmand.


