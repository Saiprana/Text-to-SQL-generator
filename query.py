from langchain import OpenAI, SQLDatabase
import streamlit as st
from langchain_experimental.sql import SQLDatabaseChain
import os
from langchain.schema.output_parser import StrOutputParser
from langchain import hub
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

# PROMPT = """
# Given an input question, first create a syntactically correct postgresql query to run. Do not use alias names for the tables and use double quotes on column names in JOIN condition
# homeProbability and awayProbability means winning percentage for the home team  and away team respectively in a particular game.
# deep column in teamstats table is the number of passes made in the opponents box. While returning the answer, use names instead of ID's.
# The question: {question}
# """
prompt = hub.pull("rlm/text-to-sql")
# prompt = """Given an input question, first create a syntactically correct postgresql query to run.
#
# Context:
# 1. Here is general context on soccer matches:
# If the home team has more goals than the away team, then the home team won the game.
# If the away team has more goals than the home team, then the away team won the game.
# If the teams goals are the same, then the teams tied.
#
# 2. Here is context on the appearances table:
# goals are how many goals the player scored.
# ownGoals are when a player scores on their own net, and the goal counts for the other team.
# xGoals is the expected amount of goals scored.
# xAssists is the expected amount of assists, not the actual amount.
# time is how many minutes a player played in that game.
#
# 3. Here is context on the leagues table:
# name is the accecpted form of league name, and understatNotation is a different notation for the league name.
#
# 4. Here is context on the shots table:
# shooterID is the playerID of the player who performed the shot.
# assisterID is the playerID of the player who assisted the shot.
# minute is the minute of the game that the shot was performed in.
# lastAction is the action right before the shot was performed.
# xGoal is the calculated percent chance that a goal was to be scored from that shot - the scale is from 0 to 1, and the closer to 1 the number is, the more the higher chance the shot should have been a goal.
#
# 5. Here is context on the teamstats table:
# location 'h' means the team was playing at home, and location 'a' means the team was playing away from their home stadium.
# xGoals is the amount of goals the team was expected to score in the game.
# deep is the number of passes made in the opponents box.
# ppda is the amount of passes allowed per defensive action in opposition half
# result refers to that teams result for the game, and a 'W' means win, 'L' means a loss, and 'D' means a draw.
#
# 6. Here is context on the games table:
# homeProbability is the projected percentage that the game results in a win for the home team.
# drawProbability is the projected percentage that the game results in a tie.
# awayProbability is the projected percentage that the game results in a win for the away team.
# B365H is the betting odds for the home team to win the game.
# B365D is the betting odds for the game to result in a draw.
# B365A is the betting odds for the away team to win the game.
#
# 7. Here is additional context regarding query and final output construction:
# Always use double quotes when referencing a column in the SELECT statement.
# In the SELECT statement, use the table reference for that column.
# Use double quotes on column names in JOIN condition.
# Use team names instead of team ids.
#
# Let's think step by step.
#
# Question: {query}
#
# Answer: """


db_chain = SQLDatabaseChain.from_llm(llm=llm, db=db, verbose=True, top_k=3, return_intermediate_steps = True)

# question = "Give the query to find the number of games that are played in different leagues"
# question = "Give the names of teams who played in season 2015"
# question = "Give us a query to find the top 3 league names with the highest average goal scored per game. Do not use alias names for the tables"
# use db_chain.run(question) instead if you don't have a prompt
# question = "Give us a query to find the top 3 leagues with the highest average goal scored per game"
# question = "Give us a query to find me a player from Manchester City who scored 3 goals in a single game during 2018 season"
# question = "Give us a query to find the goal keeper with the most appearances for Liverpool"
# question = " Give us a query to find the highest win % that Liverpool has in a single game"
# question = "Give us a query to find the game with the most passes made in the opponents box"
# question = "Give me information about the game with most passes made in the opponents box?."
# and return the game and the year in which the game was played

# Create chain with LangChain Expression Language
inputs = {
    "table_info": lambda x: db.get_table_info(),
    "input": lambda x: x["question"],
    "few_shot_examples": lambda x: "",
    "dialect": lambda x: db.dialect,
}
sql_response = (
    inputs
    | prompt
    | llm.bind(stop=["\nSQLResult:"])
    | StrOutputParser()
)

# Call with a given question
res = sql_response.invoke({"question": "Give the query to find the number of games that are played in different leagues"})
print(res)
# result1, result2 = db_chain.run(PROMPT.format(question=question))
# print("Result1", result1)
# print("Result2", result2)
# print("Result:",output1)
# print("Output2:",output2)
# print(type(output1))