from flask import Flask
from langchain_openai import ChatOpenAI
#from tools.queryDatabase import queryDatabase
from langchain_openai import ChatOpenAI
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain_community.utilities import SQLDatabase
from crewai_tools import PDFSearchTool
from crewai_tools import tool
from langchain.chains import create_sql_query_chain
from langchain.chains import create_sql_query_chain
from flask import Flask, jsonify, request
from flask_cors import CORS

import os

app = Flask(__name__)
CORS(app)

os.environ["OPENAI_API_KEY"] = 'sk-proj-VX1gWbDELubUSI1MINlzT3BlbkFJBbFO8NSmoMa6rybCYt6T'
os.environ["OPENAI_MODEL_NAME"] = 'gpt-4-0125-preview'

from tools.queryDatabase import queryDatabase

@app.route("/nestor", methods=['POST'])
def nestor():

    #Functions that make arrays of the latitude and longitude values from the LLM response.
    coordinateArray = []
    def latArray():
        latArray = coordinateArray[::2]
        return latArray
    def lonArray():
        lonArray = coordinateArray[1::2]
        return lonArray
    
    displayHistory = 0

    queryAIS = queryDatabase

    question = request.form['question']

    from crewai import Agent
    databaseAnalyst = Agent(
        role='Database Querier',
        goal='Provide vessel tracking inforrmation from an SQL database findings verbosely given raw database input and context from the user. Provide additional geographical information such as closest country and gepgraphical features of specific location in the ocean.',
        backstory='An expert geospatial analyst with a keen eye illegal fishing vessels and millitary developments.',
        tools=[queryAIS],
        llm=ChatOpenAI(model_name="gpt-4-0125-preview", temperature=1),
        allow_delegation=True
    )

    OSINTresearcher = Agent(
        role='Research Analyst',
        goal='The goal is to search through pdf documents and summarize important data, with the tools at hand.',
        backstory='An expert CIA analyst with a keen eye for finding information regarding military developments in open-source intelligence.',
        tools=[],
        llm=ChatOpenAI(model_name="gpt-4-0125-preview", temperature=1),
        allow_delegation=True
    )

    from crewai import Task
    translate = Task(
        description = ("Answer the question:" + question + ", using the tools at hand provide a verbose response in natural language that satisfies the user's question.  If you provide coordinates, follow this format ( LATITUDE , LONGITUDE ), with spaces between parenthesis and commas and digits. Always leave a space after a coordinate floating number."),
        expected_output = 'insightful response, a sentence in length.'
    )

    from crewai import Crew, Process

    crew = Crew(
        agents = [databaseAnalyst],
        manager_llm=ChatOpenAI(temperature=0, model="gpt-4"),
        tasks = [translate],
        process=Process.hierarchical,
        #memory=True, If set to true, error appears, possibly trying to find history that doesn't yet exist
        verbose=True,
        cache=True,
        max_rpm=100,
        share_crew=True
    )
    # The cue to display the vessel history is including "Display" (case sensitive) in the user input. 
    #If it is not included, the LLM kickoff goes through

    if "Display" not in question:
        result = crew.kickoff(inputs={'topic':'database query'})

        # Haphazard approach to extract coordinate values from LLM response. Does not work if there are no spaces between digits and other characters.
        for i in result.split():
            try:
                if 17 < float(i) < 123:    
                    coordinateArray.append(str(float(i))) 
            except ValueError:
                pass

    lon = lonArray()
    lat = latArray() 
    
    if "Display" in question:
        displayHistory = 1
        
        return jsonify(
         {
             'result': "", 
            'lat': "",
            'lon': "",
            'displayHistory':displayHistory
        }
        )
    else:
        return jsonify(
        {
            'result': result, 
            'lat': lat,
            'lon': lon,
            'displayHistory':displayHistory
        }
        )

if __name__ == "__main__":
    app.run(debug=True)