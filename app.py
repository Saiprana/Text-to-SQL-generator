from langchain import OpenAI, SQLDatabase
from langchain.prompts import PromptTemplate
from langchain_experimental.sql import SQLDatabaseChain
import os
import streamlit as st

os.environ["OPENAI_API_KEY"] = ""

username = "postgres"
password = "1234"
host = "localhost"
port = "5432"
mydatabase = "foot_ball"

pg_uri = f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{mydatabase}"
db = SQLDatabase.from_uri(pg_uri)

llm = OpenAI(temperature=0, verbose=True)

TRAIN_PROMPT = """Given an input question, first create a syntactically correct postgresql query to run.

Context:
1. Here is general context on soccer matches:
If the home team has more goals than the away team, then the home team won the game.
If the away team has more goals than the home team, then the away team won the game.
If the teams goals are the same, then the teams tied.

2. Here is context on the appearances table:
goals are how many goals the player scored.
ownGoals are when a player scores on their own net, and the goal counts for the other team.
xGoals is the expected amount of goals scored.
xAssists is the expected amount of assists.
xAssists are not assists.
time is how many minutes a player played in that game.

3. Here is context on the leagues table:
name is the accecpted form of league name, and understatNotation is a different notation for the league name.

4. Here is context on the shots table:
shooterID is the playerID of the player who performed the shot.
assisterID is the playerID of the player who assisted the shot.
minute is the minute of the game that the shot was performed in.
lastAction is the action right before the shot was performed.
xGoal is the calculated percent chance that a goal was to be scored from that shot - the scale is from 0 to 1, and the closer to 1 the number is, the more the higher chance the shot should have been a goal.

5. Here is context on the teamstats table:
location 'h' means the team was playing at home, and location 'a' means the team was playing away from their home stadium.
xGoals is the amount of goals the team was expected to score in the game.
deep is the number of passes made in the opponents box.
ppda is the amount of passes allowed per defensive action in opposition half
result refers to that teams result for the game, and a 'W' means win, 'L' means a loss, and 'D' means a draw.

6. Here is context on the games table:
homeProbability is the projected percentage that the game results in a win for the home team.
drawProbability is the projected percentage that the game results in a tie.
awayProbability is the projected percentage that the game results in a win for the away team.
B365H is the betting odds for the home team to win the game.
B365D is the betting odds for the game to result in a draw.
B365A is the betting odds for the away team to win the game.

7. Here is additional context regarding query and final output construction:
Always use double quotes when referencing a column in the SELECT statement.
In the SELECT statement, use the table reference for that column.
When using the Max() function, use quotes for the column names.
Use double quotes on column names in JOIN condition.
Use team names instead of team ids.
Do not forget to use table references for column references in the select clause.
Everything in the SELECT statement should use double quotes.

Examples:
Question-1: What was the highest expectation for a headed shot to go in, but it did not?
SQLQuery: SELECT MAX("xGoal") FROM shots WHERE "shotType" = 'Head' AND "shotResult" != 'Goal';

Question-2: Did Manchester City have a player who scored 3 goals in a single game during 2018 season
SQLQuery: SELECT "players"."name" FROM "appearances"
INNER JOIN "games" ON "appearances"."gameID" = "games"."gameID"
INNER JOIN "players" ON "appearances"."playerID" = "players"."playerID"
INNER JOIN "teams" ON "games"."homeTeamID" = "teams"."teamID"
WHERE "teams"."name" = 'Manchester City'
AND "games"."season" = 2018
AND "appearances"."goals" = 3
LIMIT 3;

Question-3: What game had the most passes made in the opponents box for a single team?
SQLQuery: SELECT "gameID", "teamID", "deep" FROM teamstats WHERE "deep" = (SELECT MAX("deep") FROM teamstats);

Question-4: Has a team ever won a game at home when they were expected to score less than 0.2 goals
SQLQuery: SELECT t.name AS "Team Name", g.date AS "Game Date", g."homeGoals" AS "Home Goals", g."awayGoals" AS "Away Goals"
FROM games g
JOIN teams t ON g."homeTeamID" = t."teamID"
JOIN teamstats ts ON g."gameID" = ts."gameID"
WHERE ts."location" = 'h'
AND ts."xGoals" < 0.2
AND g."homeGoals" > g."awayGoals"
LIMIT 3;

Question-5: Give the query to find the number of games that are played in different leagues
SQLQuery: SELECT "leagueID", COUNT(*) AS "Number of Games"
FROM games
GROUP BY "leagueID"
LIMIT 3;

Question-6: What game had the most shots from crosses?
SQLQuery: SELECT "games"."gameID", "games"."homeTeamID", "games"."awayTeamID", "shots"."lastAction", COUNT("shots"."lastAction") AS "crossShots"
FROM "shots"
JOIN "games" ON "shots"."gameID" = "games"."gameID"
JOIN "teams" AS "homeTeam" ON "games"."homeTeamID" = "homeTeam"."teamID"
JOIN "teams" AS "awayTeam" ON "games"."awayTeamID" = "awayTeam"."teamID"
WHERE "shots"."lastAction" = 'Cross'
GROUP BY "games"."gameID", "games"."homeTeamID", "games"."awayTeamID", "shots"."lastAction"
ORDER BY "crossShots" DESC
LIMIT 3;

Let's think step by step.

Question: {question}
 """

# TRAIN_PROMPT = """"""

st.title("CT2S")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Enter your query"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    db_chain = SQLDatabaseChain.from_llm(llm=llm, db=db, verbose=True, top_k=3)
    result = db_chain.run(TRAIN_PROMPT.format(question=prompt))


    response = f"{result}"
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})