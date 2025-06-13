import random
import os
import streamlit as st
from typing import List
from crewai import Agent, Task, Crew
from crewai.tools import tool
import openai

# Set page configuration
st.set_page_config(
    page_title="Joke Generator",
    page_icon="😂",
    layout="wide"
)

# Function to set OpenAI API key
def set_openai_api_key(api_key):
    """Set the OpenAI API key as an environment variable."""
    os.environ["OPENAI_API_KEY"] = api_key
    openai.api_key = api_key
    return api_key

# Sidebar for API key input
st.sidebar.title("Authentication")
api_key = st.sidebar.text_input("Enter your OpenAI API key:", type="password")

if api_key:
    set_openai_api_key(api_key)
    st.sidebar.success("API key set successfully!")
else:
    st.sidebar.warning("Please enter your OpenAI API key to continue.")
    st.stop()

# Define a tool function with the @tool decorator
@tool
def generate_joke(category: str) -> str:
    """Generate a random joke based on the given category.
    
    Args:
        category: The category of jokes to generate (programming, animal, or food)
        
    Returns:
        A random joke from the specified category
    """
    # List of joke categories and corresponding jokes
    jokes = {
        "programming": [
            "Why do programmers prefer dark mode? Because light attracts bugs!",
            "Why did the programmer quit his job? Because he didn't get arrays!",
            "How many programmers does it take to change a light bulb? None, that's a hardware problem!"
        ],
        "animal": [
            "Why don't oysters donate to charity? Because they're shellfish!",
            "What do you call a bear with no teeth? A gummy bear!",
            "Why don't ants get sick? Because they have tiny ant-ibodies!"
        ],
        "food": [
            "Why did the tomato blush? Because it saw the salad dressing!",
            "What do you call a fake noodle? An impasta!",
            "Why did the cookie go to the doctor? Because it was feeling crumbly!"
        ]
    }
    
    # Check if the category exists, if not return a default message
    if category.lower() not in jokes:
        return f"Sorry, I don't have any jokes for the category '{category}'. Try 'programming', 'animal', or 'food'."
    
    # Return a random joke from the specified category
    return random.choice(jokes[category.lower()])

# Main application
st.title("🎭 AI Joke Generator")
st.write("Get a random joke from your chosen category!")

# Category selection
category_options = ["programming", "animal", "food"]
selected_category = st.selectbox("Select a joke category:", category_options)

# Button to generate joke
if st.button("Generate Joke"):
    try:
        with st.spinner("Generating your joke..."):
            # Initialize the Agent
            jokes_agent = Agent(
                name="jokes generator",
                role="Generate random jokes based on user input category",
                goal="Provide entertaining jokes from specific categories",
                backstory="I am an AI-powered joke generator with a vast database of jokes across various categories.",
                tools=[generate_joke],
            )

            # Initialize the Task
            joke_task = Task(
                description=f"Generate a joke based on the {selected_category} category",
                agent=jokes_agent,
                expected_output="A random joke from the specified category",
            )

            # Initialize the Crew
            joke_crew = Crew(
                agents=[jokes_agent],
                tasks=[joke_task],
                verbose=True
            )

            # Execute the crew and get the result
            result = joke_crew.kickoff(inputs={"category": selected_category})
            
            # Display the joke in a nice box
            st.success(result)
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        if "API key" in str(e).lower() or "authentication" in str(e).lower():
            st.warning("There might be an issue with your OpenAI API key. Please check if it's valid.")

# Additional information
st.markdown("---")
st.markdown("### Available Joke Categories")
st.markdown("- **Programming**: Jokes about coding, developers, and software")
st.markdown("- **Animal**: Jokes about animals and their funny behaviors")
st.markdown("- **Food**: Jokes about food, cooking, and eating")
