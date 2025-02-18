# Quadropic OSS
# https://oss.quadropic.com
# Author : Mohamed Kamran
# Date : Feb 8th 2025

# File Description :
# This file contains the implementation of the LLM model.


# Use langchain-openai to make a LLM call with streaming

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
import os

# WARNING : You have to make and edit .env as per the instructions in the README.md
from dotenv import load_dotenv
load_dotenv()


def generateLLMResponse(System: str, User: str, streaming: str = True, verbose: str = False):
    Model = os.getenv("LLM_MODEL_ID")
    messages = [
        SystemMessage(content=System),
        HumanMessage(content=User),
    ]
    # Check and print the .env file for the LLM_ENDPOINT and LLM_API_KEY
    print(os.getenv("LLM_ENDPOINT"))
    print(os.getenv("LLM_API_KEY"))
    llm = ChatOpenAI(
        model=Model,
        base_url=os.getenv("LLM_ENDPOINT"),
        api_key=os.getenv("LLM_API_KEY"),
    ) | StrOutputParser()
    
    # Combine system and user messages    
    # Generate response
    response = llm.invoke(messages)
    return response
    
# Test Usage
if __name__ == "__main__":
    m = generateLLMResponse(System="You'rea helpfull AI", User="Hello, how are you?",verbose=True)
    print(m)