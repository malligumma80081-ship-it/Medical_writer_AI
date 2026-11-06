## I have plan to develop Medical_writer_AI in 50 days 

this is the project directory 
## mkdir medical write_AI
## cd medical write_AI
## python -m venv venv
## for Windows
venv/scripts/activate
## for Mac or Linax
source venv/bin/activate
## Install Package 
python -m pip install -r requirement.txt
## Application for running purpose for backend 
uvicorn app.main:app --reload
## Day-1
created basic file: like config.py
                         health.py
                         logging.py
                         main.py 
                         .env.example 
                         .env
                         requirement.txt
## day-2
created Postgrel SQL like: Model
                           DB 
                           pytest.ini
                           alembic
## Day-3 
created Jwt Aunthacation and Role based access
##  Day-4
integration with pdf file and docx files 

## Day-5 
created chunking file 
## Recommended initial configuration
## Setting	Value
## Target chunk size	500 tokens
## Maximum chunk size	650 tokens
## Minimum chunk size	80 tokens
## Overlap	75 tokens
## Splitting priority	Section → paragraph → sentence
## Metadata	Document ID, section, page

##  processing
Section detection → sentence-aware splitting → chunk overlap → token counting
## output
Structured chunks saved in PostgreSQL with source metadata
## Day-6 
created Embedding 
## Embedding generation
Each chunk → Numerical vector
          |
Chroma DB vector database
          |
Store vectors + document metadata
          |
Semantic retrieval

User question → Query embedding → Relevant evidence chunks
an embedding is numerical representation of text it allows a complete to compare the meaning of text rather then relaxing only on exact keyword match 

## Select an embedding model
## For today's local development, use BAAI/bge-small-en-v1.5.
## English-language embedding model.
## 384-dimensional vectors.
## Can run locally.
## Suitable for an initial retrieval prototype.
## Day-7 
## created RAG 
Understand today's architecture
## 1. User question
## "What were the primary efficacy outcomes?"
## 2. Query preprocessing
## Validate and normalize the question
## 3. Semantic retrieval
## Generate query embedding → Search Qdrant → Retrieve top 10
## 4. Reranking
## Reorder candidates by query-document relevance
## 5. Context assembly
## Select relevant chunks, deduplicate, preserve citations
## 6. Evidence package
## Source document + section + page + exact supporting text

What is reranking?
retrieved chunks using vector similarity. However, the closest embedding is not necessarily the most useful passage for a particular question.
Reranking evaluates the relationship between the question and each retrieved passage more directly.
## Stage	Purpose	Example
Retrieval 	        Find candidate passages quickly 	         Top 10 chunks
Reranking 	       Prioritize the most relevant candidates 	   Top 5 chunks
Context assembly	 Prepare evidence for the LLM	               Top 3–5 chunks

For example, a query about primary efficacy outcomes may initially retrieve both the Methods and Results sections. A reranker should prioritize the passage reporting the actual outcome results.

Today we will use a cross-encoder reranker. It evaluates a question and passage together, rather than embedding them independently.
## Configure today's retrieval settings
Start with these values and tune them using your own medical literature test set.
## Parameter	                      Initial value
Initial retrieval	                   15 chunks
Reranked results	                    5 chunks
Context limit	                      3,000 tokens
Minimum vector score	                 0.30
Reranker	                          BGE Reranker Base
Embedding model	                    BGE Small EN v1.5

The minimum vector score is an experimental filter, not a universal relevance threshold. We will need to calibrate it with real queries.
