import os
import gradio as gr
from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

class PlannerState(TypedDict):
    messages: Annotated[List[HumanMessage | AIMessage], "The messages in the conversation"]
    city: str
    interests: List[str]
    itinerary: str


llm = ChatGroq(
    temperature=0,
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.3-70b-versatile"
)

itinerary_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful travel assistant. Create a day trip itinerary for {city} based on interests: {interests}."),
    ("human", "Create an itinerary for my day trip."),
])

def input_city(city: str, state: PlannerState) -> PlannerState:
    return {
        **state,
        "city": city,
        "messages": state['messages'] + [HumanMessage(content=city)]
    }

def input_interests(interests: str, state: PlannerState) -> PlannerState:
    return {
        **state,
        "interests": [interest.strip() for interest in interests.split(",") if interest.strip()],
        "messages": state['messages'] + [HumanMessage(content=interests)]
    }

def create_itinerary(state: PlannerState) -> PlannerState:
    response = llm.invoke(itinerary_prompt.format_messages(
        city=state['city'],
        interests=', '.join(state['interests'])
    ))
    return {
        **state,
        "messages": state['messages'] + [AIMessage(content=response.content)],
        "itinerary": response.content,
    }

def travel_planner(city: str, interests: str):
    if not city.strip():
        return "Please enter a city."
    if not interests.strip():
        return "Please enter at least one interest."

    state = {
        "messages": [HumanMessage(content=f"Plan a trip to {city} with interests {interests}")],
        "city": "",
        "interests": [],
        "itinerary": "",
    }

    state = input_city(city, state)
    state = input_interests(interests, state)
    state = create_itinerary(state)

    return state["itinerary"]

interface = gr.Interface(
    fn=travel_planner,
    theme="Yntec/HaleyCH_Theme_Orange_Green",
    inputs=[
        gr.Textbox(label="Enter the city for your day trip"),
        gr.Textbox(label="Enter your interests (comma-separated)"),
    ],
    outputs=gr.Textbox(label="Generated Itinerary"),
    title="Travel Itinerary Planner",
    description="Enter a city and your interests to generate a personalized day trip itinerary.",
)

if __name__ == "__main__":
    interface.launch()
