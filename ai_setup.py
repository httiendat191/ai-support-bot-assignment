import os
import glob
import sys
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
VECTOR_STORE_NAME = "OptiSigns-Knowledge-Base"
DOCS_DIR = "docs"
MODEL_ID = "gpt-4o" 

if not API_KEY:
    print("Critical Error: OPENAI_API_KEY not found in .env file.")
    sys.exit(1)

client = OpenAI(api_key=API_KEY)

def setup_assistant():
    print("Initializing AI Assistant Setup (v2.16.0 Fixed)...")

    try:
        #STEP 1: Create Vector Store
        print(f"Creating Vector Store: '{VECTOR_STORE_NAME}'...")
        vector_store = client.vector_stores.create(name=VECTOR_STORE_NAME)
        print(f"Vector Store created. ID: {vector_store.id}")

        #STEP 2: Upload Files
        file_paths = glob.glob(f"{DOCS_DIR}/*.md")
        
        if not file_paths:
            print(f"Error: No Markdown files found in '{DOCS_DIR}/'.")
            return

        print(f"Found {len(file_paths)} markdown files. Uploading to OpenAI...")

        file_batch = client.vector_stores.file_batches.upload_and_poll(
            vector_store_id=vector_store.id,
            files=[open(path, "rb") for path in file_paths]
        )

        print(f"Upload Status: {file_batch.status}")
        print(f"File Counts: {file_batch.file_counts}")

        # STEP 3: Create Assistant
        system_instructions = """
You are OptiBot, the customer support bot for OptiSigns.com.
• Tone: helpful, factual, concise.
• Only answer using the uploaded docs.
• Max 5 bullet points; else link to the doc.
• Cite up to 3 "Article URL:" lines per reply.
        """

        print("Creating Assistant with 'file_search' tool...")
        
        assistant = client.beta.assistants.create(
            name="OptiBot-Clone",
            instructions=system_instructions,
            model=MODEL_ID,
            tools=[{"type": "file_search"}],
            tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
        )

        print("\n" + "="*50)
        print("SUCCESS: Assistant Created Successfully!")
        print(f"Assistant Name: {assistant.name}")
        print(f"Assistant ID:   {assistant.id}")
        print("="*50)

    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")

if __name__ == "__main__":
    setup_assistant()