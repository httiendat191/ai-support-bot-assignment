import os
import json
import requests
import sys
from datetime import datetime
from dotenv import load_dotenv
from markdownify import markdownify as md
from openai import OpenAI

# 1. CONFIGURATION
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
VECTOR_STORE_ID = os.getenv("VECTOR_STORE_ID")
ZENDESK_URL = "https://support.optisigns.com/api/v2/help_center/articles.json?per_page=30"
TRACKING_FILE = "tracking.json"
DOCS_DIR = "docs"

# Validate API Keys
if not API_KEY or not VECTOR_STORE_ID:
    print("Critical Error: Missing Keys in .env file.")
    sys.exit(1)

client = OpenAI(api_key=API_KEY)

# Create docs directory if it doesn't exist
if not os.path.exists(DOCS_DIR):
    os.makedirs(DOCS_DIR)

# 2. HELPER FUNCTIONS
def load_tracking_data():
    """Load the tracking history from JSON file."""
    if os.path.exists(TRACKING_FILE):
        with open(TRACKING_FILE, "r") as f:
            return json.load(f)
    return {}

def save_tracking_data(data):
    """Save the tracking history to JSON file."""
    with open(TRACKING_FILE, "w") as f:
        json.dump(data, f, indent=4)

def clean_html(html_content):
    """Convert HTML to Markdown."""
    return md(html_content, heading_style="ATX")

# 3. MAIN DAILY FUNCTION
def run_daily_job():
    print(f"Starting Daily Job at {datetime.now()}...")
    
    # A. Fetch article from Zendesk
    try:
        response = requests.get(ZENDESK_URL)
        if response.status_code != 200:
            print(f"Error fetching Zendesk: {response.status_code}")
            return
        articles = response.json().get('articles', [])
    except Exception as e:
        print(f"Connection Error: {e}")
        return

    # B. Check for updated article
    tracking_data = load_tracking_data()
    files_to_upload = []
    updated_count = 0
    skipped_count = 0
    
    for article in articles:
        article_id = str(article['id'])
        remote_updated_at = article['updated_at']
        
        # Condition: New article OR timestamp changed
        if (article_id not in tracking_data) or (tracking_data[article_id] != remote_updated_at):
            print(f"Detected Change/New: Article {article_id}")
            
            # Process content
            title = article['title']
            body = article['body']
            link = article['html_url']
            
            if not body: continue

            markdown_content = f"# {title}\n\nSource: {link}\n\n{clean_html(body)}"
            
            # Save file to disk
            filename = f"{DOCS_DIR}/{article_id}.md"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(markdown_content)

            files_to_upload.append(filename)
            
            # Update tracking memory (wait for upload to confirm save)
            tracking_data[article_id] = remote_updated_at
            updated_count += 1
        else:
            skipped_count += 1

    print(f"Summary: {updated_count} New/Updated, {skipped_count} Skipped.")

    # C. Upload to OpenAI (Only if there are new files)
    if files_to_upload:
        print(f"Uploading {len(files_to_upload)} files to Vector Store...")
        try:
            # Open file streams
            file_streams = [open(path, "rb") for path in files_to_upload]
            
            # Upload and poll for processing
            client.vector_stores.file_batches.upload_and_poll(
                vector_store_id=VECTOR_STORE_ID,
                files=file_streams
            )
            
            # Save tracking state only after successful upload
            save_tracking_data(tracking_data)
            print("Upload Complete & Tracking Saved.")
            
        except Exception as e:
            print(f"Upload Failed: {e}")
    else:
        print("No new updates to upload. System is up to date.")

if __name__ == "__main__":
    run_daily_job()