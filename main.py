import streamlit as st
import os
from crewai import Agent, Task, Crew
from crewai.tools import tool
from pydantic import BaseModel, Field
import requests
import openai

class JokeRequest(BaseModel):
    category: str = Field(..., description="The category of joke to generate")

@tool
def generate_joke(joke_request: JokeRequest) -> str:
    """Generate a random joke based on the given category."""
    try:
        url = f"https://api.humorapi.com/jokes/random?api-key={st.session_state.joke_api_key}&category={joke_request.category}"
        response = requests.get(url)
        response.raise_for_status()
        joke_data = response.json()
        return joke_data['joke']
    except requests.RequestException as e:
        return f"Error generating joke: {str(e)}"

def initialize_agent():
    return Agent(
        name="jokes",
        role="Jokes Generator",
        goal="Generate random jokes based on user input",
        backstory="I am an AI-powered jokes generator, ready to make you laugh!",
        tools=[generate_joke],
        verbose=True
    )

def create_task(agent):
    return Task(
        description="Generate a random joke based on user input",
        agent=agent,
        expected_output="A funny joke based on the specified category",
        tools=[generate_joke]
    )

def run_crew(task):
    crew = Crew(
        agents=[task.agent],
        tasks=[task],
        verbose=True
    )
    result = crew.kickoff()
    return result

def set_openai_api_key(api_key):
    os.environ["OPENAI_API_KEY"] = api_key

def check_openai_api_key(api_key):
    openai.api_key = api_key
    try:
        openai.Completion.create(engine="davinci", prompt="Hello, World!", max_tokens=5)
        return True
    except:
        return False

st.title("Joke Generator")

if 'openai_api_key' not in st.session_state:
    st.session_state.openai_api_key = ''

if 'joke_api_key' not in st.session_state:
    st.session_state.joke_api_key = ''

with st.sidebar:
    st.header("API Configuration")
    openai_api_key = st.text_input("Enter your OpenAI API key:", type="password")
    joke_api_key = st.text_input("Enter your Joke API key:", type="password")
    if st.button("Submit API Keys"):
        if check_openai_api_key(openai_api_key):
            st.session_state.openai_api_key = openai_api_key
            set_openai_api_key(openai_api_key)
            st.session_state.joke_api_key = joke_api_key
            st.success("API keys set successfully!")
        else:
            st.error("Invalid OpenAI API key. Please try again.")

if st.session_state.openai_api_key and st.session_state.joke_api_key:
    st.write("Welcome to the Joke Generator!")
    category = st.text_input("Enter a joke category:")
    
    if st.button("Generate Joke"):
        try:
            jokes_agent = initialize_agent()
            joke_task = create_task(jokes_agent)
            joke_result = run_crew(joke_task)
            st.write("Generated Joke:")
            st.write(joke_result)
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
else:
    st.warning("Please enter your OpenAI API key and Joke API key in the sidebar to use the Joke Generator.")