from mem0 import Memory
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")
from openai import OpenAI
import json
import os

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
config = {
    "version": "v1.1",
    "embedder": {
        "provider": "openai",
        "config": {"api_key": OPENAI_API_KEY, "model": "text-embedding-3-small"},
    },
    "llm": {
        "provider": "openai",
        "config": {"api_key": OPENAI_API_KEY, "model": "gpt-4.1"},
    },
    "vector_store": {
        "provider": "qdrant",
        "config": {"host": "localhost", "port": 6333},
    },
}

llm_client = OpenAI()
mem_client = Memory.from_config(config)

while True:
    user_query = input("::>")
    search_memory = mem_client.search(query=user_query, user_id="abhi")

    memory_list = [
        f"ID: {mem.get('id')}\n Memory: {mem.get('memory')}\n"
        for mem in search_memory.get("results")
    ]
    print("Found Memories: ", memory_list)
    SYSTEM_PROMPT = f"""Here a short context of user {json.dumps(memory_list)}"""

    response = llm_client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_query},
        ],
    )
    ai_response = response.choices[0].message.content
    print("AI: ", ai_response)

    mem_client.add(
        user_id="abhi",
        messages=[
            {"role": "user", "content": user_query},
            {"role": "assistant", "content": ai_response},
        ],
    )
