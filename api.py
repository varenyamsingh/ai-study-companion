import os
from typing import Union
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import traceback
import asyncio

# 1. Load env before anything else
load_dotenv()

from core.engine import get_vectorstore
from core.tools import create_tutor_tools
from langchain_groq import ChatGroq 
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage

# Use create_agent from langchain.agents (same as main.py)
from langchain.agents import create_agent

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Initialize LLM (Using the 8B model to avoid rate limits)
llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.1-8b-instant", 
    temperature=0.1
)

# 3. Setup Knowledge Base and Tools
vs = None
tools = []
try:
    vs = get_vectorstore("my_notes.pdf")
    tools = create_tutor_tools(vs)
    print(f"✅ Successfully initialized {len(tools)} tools")
except Exception as e:
    print(f"❌ Error initializing vectorstore or tools: {e}")
    traceback.print_exc()
    tools = []

# 4. Initialize memory checkpoint
memory = MemorySaver()

# 5. Initialize the Agent (Using same pattern as main.py)
agent = None
try:
    # Use create_agent with checkpointer (same as main.py)
    agent = create_agent(llm, tools, checkpointer=memory)
    print("✅ Agent created successfully")
except Exception as e:
    print(f"❌ Failed to create agent: {e}")
    traceback.print_exc()
    agent = None

# 6. Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Smart Tutor API is running",
        "status": "ok",
        "agent_initialized": agent is not None,
        "tools_count": len(tools) if tools else 0
    }

# 7. Health check endpoint
@app.get("/health")
async def health():
    return {"status": "ok", "tools_count": len(tools) if tools else 0, "agent_initialized": agent is not None}

# 8. Data Model (Allows Strings, Numbers, and Special Characters)
class ChatRequest(BaseModel):
    message: Union[str, int]

@app.post("/chat")
async def chat(request: ChatRequest):
    if agent is None:
        return {"reply": "❌ Agent not initialized. Please check backend logs for errors."}
    
    try:
        # Convert message to string just in case it's a number
        user_input = str(request.message)
        
        # Use config for thread management
        config = {"configurable": {"thread_id": "student_1"}}
        
        # Try different message formats (run in thread pool to avoid blocking)
        response = None
        try:
            # First try: HumanMessage format (newer API)
            response = await asyncio.to_thread(
                agent.invoke, 
                {"messages": [HumanMessage(content=user_input)]}, 
                config
            )
        except Exception as e1:
            try:
                # Second try: Tuple format (older API, like main.py)
                response = await asyncio.to_thread(
                    agent.invoke,
                    {"messages": [("user", user_input)]},
                    config
                )
            except Exception as e2:
                # Third try: Just the input dict
                response = await asyncio.to_thread(
                    agent.invoke,
                    {"input": user_input},
                    config
                )
        
        # Get the final AI response
        if response is None:
            return {"reply": "❌ No response from agent"}
            
        if isinstance(response, dict):
            if "messages" in response:
                # Find the last AI message (not HumanMessage)
                from langchain_core.messages import AIMessage
                for msg in reversed(response["messages"]):
                    # Look for AIMessage or any message that's not HumanMessage
                    if isinstance(msg, AIMessage) or (hasattr(msg, 'content') and msg.content and not isinstance(msg, HumanMessage)):
                        reply = msg.content if hasattr(msg, 'content') else str(msg)
                        break
                else:
                    # If no AI message found, get the last message
                    if response["messages"]:
                        last_msg = response["messages"][-1]
                        reply = getattr(last_msg, 'content', str(last_msg))
                    else:
                        reply = "No messages in response"
            elif "output" in response:
                reply = response["output"]
            else:
                reply = str(response)
        else:
            reply = str(response)
            
        return {"reply": reply}
        
    except Exception as e:
        # Print full traceback for debugging
        error_trace = traceback.format_exc()
        print(f"Error in chat endpoint: {error_trace}")
        
        # Handle the Rate Limit error gracefully in the UI
        if "429" in str(e):
            return {"reply": "⚠️ Daily limit reached on Groq. Please try again later."}
        return {"reply": f"Error: {str(e)}\n\nCheck backend logs for details."}

# Run with: uvicorn api:app --reload