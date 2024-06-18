import os

from crewai_tools import tool
from langchain.chains import create_sql_query_chain
from langchain_openai import ChatOpenAI
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain_community.utilities import SQLDatabase
from dotenv import load_dotenv
load_dotenv()


#API_KEY = os.environ['OPENAI_API_KEY']
os.environ["OPENAI_MODEL_NAME"] = 'gpt-4-0125-preview'
os.environ["OPENAI_MODEL_NAME"] = 'gpt-4-0125-preview'


@tool("QueryDatabase")
def queryDatabase(question: str) -> str:
        """This tool is to be used to query the AIS Database for any questions pertaining to historical behavior of vessels"""
        db = SQLDatabase.from_uri("sqlite:///chineseVesselsTaiwan.db")
        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

        chain = create_sql_query_chain(llm, db)

        execute_query = QuerySQLDataBaseTool(db=db)
        write_query = create_sql_query_chain(llm, db)
        chain = write_query | execute_query
        
        queryResponse = chain.invoke({"question": question})

        return queryResponse
