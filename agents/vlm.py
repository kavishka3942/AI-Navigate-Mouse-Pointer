# vlm.py
from ollama import AsyncClient

async def agent_llm(prompt: str, screenshot_path: str = None):
    """
    Asynchronous VLM caller.
    Accepts an optional screenshot path.
    """
    # 1. Start building the message payload
    message = {'role': 'user', 'content': prompt}
        
    # 2. Use Ollama's AsyncClient to safely await the network call
    client = AsyncClient()
    response = await client.chat(
        model='qwen2.5vl:3b',
        messages=[message],
        options={
            "num_ctx": 8192,       # Expand context window so cache isn't overwritten
            "num_predict": 512,    # Cap response tokens to speed up generation
            "temperature": 0.0,    # Set determinism to 0 for strict routing logic
        }
    )
    
    return response.message.content

async def agent_vlm(prompt: str, screenshot_path: str = None):
    """
    Asynchronous VLM caller.
    Accepts an optional screenshot path.
    """
    # 1. Start building the message payload
    message = {'role': 'user', 'content': prompt}
    
    # 2. Only attach the image if a valid path was provided
    if screenshot_path:
        message['images'] = [screenshot_path]
        
    # 3. Use Ollama's AsyncClient to safely await the network call
    client = AsyncClient()
    response = await client.chat(
        model='qwen2.5vl:3b',
        messages=[message],
        options={
            "num_ctx": 8192,       # Expand context window so cache isn't overwritten
            "num_predict": 512,    # Cap response tokens to speed up generation
            "temperature": 0.0,    # Set determinism to 0 for strict routing logic
        }
    )
    
    return response.message.content