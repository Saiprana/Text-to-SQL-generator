from langchain.agents import create_sql_agent
from langchain.utilities import SQLDatabase
from langchain import OpenAI
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
import os

# from langchain.agents import AgentExecutor
from langchain.agents.agent_types import AgentType

username = "postgres"
password = "1234"
host = "localhost"
port = "5432"
mydatabase = "foot_ball"

os.environ["OPENAI_API_KEY"] = ""

pg_uri = f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{mydatabase}"
db = SQLDatabase.from_uri(pg_uri)

agent_executor = create_sql_agent(
    llm=OpenAI(temperature=0),
    toolkit=SQLDatabaseToolkit(db=db, llm=OpenAI(temperature=0)),
    verbose=True,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
)

agent_executor.run(
    "Did Manchester City have a player who scored 3 goals in a single game during 2018 season"
)