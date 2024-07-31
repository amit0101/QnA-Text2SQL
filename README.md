# RAG Personal QnA on Amit

#### Steps to run this repo locally with Docker:

Clone this repo

`git clone https://github.com/amit0101/rag-personal-qna.git`

Change to main directory

`cd rag-personal-qna`

Add your OpenAI API key to .env file
`OPENAI_API_KEY=""`

Run docker build
`docker-compose up --build`

Access the Streamlit app at https://localhost:8501

NOTE: On first run, it takes a few seconds for the vector store to index the files. To add more files to the vector database, empty the contents of `db` folder and rerun the Docker commmand.


