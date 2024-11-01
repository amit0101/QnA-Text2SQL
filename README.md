# RAG Personal QnA on Text2SQL papers

#### Steps to run this repo locally with Docker:

Clone this repo

```sh
git clone https://github.com/amit0101/QnA-Text2SQL.git
```

Change to main directory

```sh
cd QnA-Text2SQL
```

Add your OpenAI API key to .env file
`OPENAI_API_KEY="YOUR_KEY"`

##### For FastAPI server

Run docker build
```sh
docker-compose up --build
```

Open a new terminal

Start a chat with
```sh
curl -X POST http://localhost:8000/start_new_conversation
```
which provides a `session_id`

Ask a question with
```sh
curl -X POST http://localhost:8000/ask_question -H "Content-Type: application/json" -d '{"question": "What is Text2SQL?", "session_id": "YOUR_SESSION_ID"}'
```

(Starting a new chat clears existing session)

##### For Streamlit interface

In Dockerfile, comment out the command to run Streamlit

```sh
CMD ["sh", "-c", "streamlit run app.py --server.port=8501 --server.address=0.0.0.0"]
```

Run docker build
```sh
docker-compose up --build
```

Access the Streamlit app at https://localhost:8501

NOTE: The PDF files have already been indexed and stored into the ChromaDB object. To add more files or any new files to the vector database, empty the contents of `db` and `chroma` folders, run `python model/rag_model.py` and then rerun the Docker commmand.

#### Solution approach

- **Data Ingestion**: The documents are indexed into collections with a chunk size of 1500 characters (with an overlap of 300) and the same is stored as a persistent db into a chromadb object.
- **RAG model querying**: The RAG model is set up through embeddings on the db collections. Upon querying with a question the model is retrieved for the relevant chunks and passed on the conversation history aware LLM to process and answer the questions.
- **Model version**: `gpt-4-turbo` for chat and `text-embedding-ada-002` for embeddings.
- **Model Evaluation**: As a quick approach to demonstrate evaluation for the RAG model, a script is included to calculate BertScore on a small sample of answers to questions with different levels of difficulty. The validation script can be run to print the performance scores with `python model/model_evaluation.py`.

BERT score metrics:
```sh
{'precision': 0.3177162706851959, 'recall': 0.49321022629737854, 'f1': 0.4032721221446991}
```

QnA set used for evaluation:

```sh
{
  "questions": [
    {
      "difficulty": "simple",
      "question": "What is the primary goal of a text-to-SQL system?",
      "reference_answer": "The primary goal of a text-to-SQL system is to transform natural language questions into structured SQL statements that accurately represent the user's intent, allowing seamless interaction with databases.",
      "rag_answer": "The primary goal of a text-to-SQL system is to translate natural language queries into structured query language (SQL) that can be executed on a database. These systems aim to automate the process of querying databases using natural language, reducing the barrier for non-experts to access and retrieve information from databases efficiently. The ultimate objective is to enable users to interact with databases in a more intuitive and user-friendly manner."
    },
    {
      "difficulty": "simple",
      "question": "Which two datasets are most commonly used for training and evaluating neural text-to-SQL systems?",
      "reference_answer": "The two most commonly used datasets are WikiSQL and Spider.",
      "rag_answer": "The two most commonly used datasets for training and evaluating neural text-to-SQL systems are WikiSQL and Spider. These datasets are large-scale, multi-domain benchmarks that have made it possible to compare different systems easily and effectively."
    },
    {
      "difficulty": "medium",
      "question": "How does prompt design influence the performance of large language models in the text-to-SQL task?",
      "reference_answer": "Prompt design is critical because the inclusion of schema information and structured SQL data can significantly improve the model's performance. For example, adding database schema and SELECT statements improved Codex's execution accuracy, demonstrating that prompt components help LLMs better understand the database structure.",
      "rag_answer": "Prompt design significantly influences the performance of large language models (LLMs) in the text-to-SQL task. The effectiveness of prompt templates, such as DDL/SimpleDDL prefix, MD/HTML/Coding infix, and Complete/Chat postfix, impacts the model's ability to generate accurate SQL queries. Investigating unified prompt templates can help determine optimal prompt constructions and improve LLM performance in text-to-SQL tasks."
    },
    {
      "difficulty": "medium",
      "question": "What are some common types of ambiguity that text-to-SQL systems need to handle when processing natural language queries?",
      "reference_answer": "Common types of ambiguity include lexical ambiguity (e.g., polysemy like 'Paris' as a city or person), syntactic ambiguity (e.g., 'Find all German movie directors' could mean directors of German movies or directors from Germany), semantic ambiguity (e.g., 'Are Brad and Angelina married?' could mean to each other or separately), and context-dependent ambiguity (e.g., the term 'top' may vary in meaning based on context, such as 'top movie' by ratings or 'top scorer' by goals).",
      "rag_answer": "Text-to-SQL systems need to handle lexical ambiguity, where a single word can have multiple meanings (e.g., \"Paris\" as a city or a person), and syntactic ambiguity, where a sentence can have multiple interpretations based on its structure (e.g., \"Find all German movie directors\" can be parsed in different ways). These types of ambiguity in natural language queries pose challenges for accurately translating them into SQL queries."
    },
    {
      "difficulty": "hard",
      "question": "Explain how in-context learning enables LLMs to perform text-to-SQL tasks without fine-tuning.",
      "reference_answer": "In-context learning allows LLMs to perform text-to-SQL tasks by providing a prompt that includes a task instruction, a natural language question, and optional examples. The LLM uses these examples to learn the mapping between NLQ and SQL on-the-fly, allowing it to generate SQL queries without being explicitly fine-tuned on a large text-to-SQL dataset. This technique leverages the model's pre-existing knowledge and can perform well, especially with strategically designed prompts.",
      "rag_answer": "In-context learning allows pretrained LLMs to perform text-to-SQL tasks by providing zero or a few training examples as demonstrations, without the need for fine-tuning. This approach leverages the advanced reasoning capabilities of LLMs to directly infer the relationship between natural language questions and SQL queries from a database. By using task instructions and test questions with corresponding databases, LLMs can demonstrate their text-to-SQL capabilities without requiring extensive fine-tuning on specific datasets."
    },
    {
      "difficulty": "hard",
      "question": "What are the main challenges faced by traditional learning-based text-to-SQL methods compared to LLM-based approaches?",
      "reference_answer": "Traditional learning-based text-to-SQL methods struggle with issues like vocabulary gaps, schema ambiguity, and implicit join operations. These methods often require extensive feature engineering and are less flexible in handling diverse and complex queries. In contrast, LLM-based approaches benefit from advanced reasoning and in-context learning capabilities, which enable them to generalize across different domains and handle complex SQL generation tasks without extensive manual intervention.",
      "rag_answer": "Traditional learning-based text-to-SQL methods face challenges in producing valid SQL statements due to difficulties in schema linking and skeleton parsing. They also struggle with lower accuracy rates, with the highest on the Spider leaderboard being 79.9%. In contrast, LLM-based approaches leverage advancements in LLMs for improved performance, zero-shot reasoning, and domain generalization capabilities."
    }
  ]
}
```


