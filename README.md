## I have plan to develop Medical_writer_AI in 50 days 

this is the project directory 
mkdir medical write_AI
cd medical write_AI
python -m venv venv
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
##  processing
Section detection → sentence-aware splitting → chunk overlap → token counting
## output
Structured chunks saved in PostgreSQL with source metadata
## Day-6 
created Embedding 
an embedding is numerical representation of text it allows a complete to compare the meaning of text rather then relaxing only on exact keyword match 
## Day-7 
created RAG 
