import time

def generate_quiz(chat_history, llm):
    # Short pause to keep the API happy
    time.sleep(1) 
    
    # We add a 'Strict System Instruction'
    prompt = f"""
    SYSTEM: You are a concise Quiz Generator. Do NOT provide long explanations. 
    Do NOT talk about yourself. Only output the questions and options.

    CONTEXT: {chat_history}

    FORMAT YOUR RESPONSE EXACTLY LIKE THIS:
    Q1: [Question text]
    A) [Option]
    B) [Option]
    C) [Option]
    D) [Option]

    Q2: [Question text]
    A) [Option]
    B) [Option]
    C) [Option]
    D) [Option]

    ANSWER KEY: (At the very bottom)
    """
    return llm.invoke(prompt)