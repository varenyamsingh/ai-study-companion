import os
import time
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent # In v1.0, create_react_agent moved here as create_agent
from langgraph.checkpoint.memory import MemorySaver
# Replace the old langgraph/react imports with this:
from langchain.agents import create_agent

# Import your custom modules
from core.engine import get_vectorstore
from core.tools import create_tutor_tools
from modules.evaluation import generate_quiz
from langchain_groq import ChatGroq

load_dotenv()

# Setup Brain & Memory

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.1,  # Lower temperature = More direct and less 'chatty'
    max_tokens=300    # This physically stops the AI from writing too much
)
memory = MemorySaver()

# 1. Initialize Knowledge
vs = get_vectorstore("my_notes.pdf")
tools = create_tutor_tools(vs)

# 2. Create the Agent
# Change create_react_agent to create_agent
# Note: the parameter name changed from 'system_prompt' (optional) to 'prompt' or 'system_prompt'
agent = create_agent(llm, tools, checkpointer=memory)

print("🎓 Smart Tutor is Online. Type 'quiz' to test yourself or 'quit' to stop.")

# 3. Simple Loop
while True:
    user_input = input("\nYou: ")
    if user_input.lower() == "quiz":
            print("\n📝 GENERATING QUIZ (Taking a 30-second breather for API)...")
            time.sleep(30) # Increase this to 30 seconds for the Free Tier
            try:
                for event in agent.stream({"messages": [("user", user_input)]}, config):
                    for value in event.values():
                        if "messages" in value:
                            print(f"Tutor: {value['messages'][-1].content}")
            except Exception as e:
                if "429" in str(e):
                    print("\n⚠️ API is still busy. Wait 45 seconds before your next message.")
                else:
                    print(f"\n❌ An error occurred: {e}")
    
    if user_input.lower() == "quiz":
        # We'll simulate getting history for now
        print("\n📝 GENERATING QUIZ...")
        print(generate_quiz("Previous study topic: Neural Networks", llm).content)
        continue

    # Normal Tutoring
    config = {"configurable": {"thread_id": "student_1"}}
    for event in agent.stream({"messages": [("user", user_input)]}, config):
        for value in event.values():
            if "messages" in value:
                print(f"Tutor: {value['messages'][-1].content}")