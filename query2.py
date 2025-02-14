from langchain import OpenAI, SQLDatabase

from langchain_experimental.sql import SQLDatabaseChain
import os
import psycopg2
os.environ["OPENAI_API_KEY"] = ""
username = "postgres"
password = "1234"
host = "localhost"
port = "5432"
mydatabase = "foot_ball"

pg_uri = f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{mydatabase}"
db = SQLDatabase.from_uri(pg_uri)


llm = OpenAI(temperature=0, verbose=True)

db_chain = SQLDatabaseChain(llm=llm, database=db, verbose=True, top_k=3)

question = "how many leagues are there?"

db_chain.run("how many rows are there?")
