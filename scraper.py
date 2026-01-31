import requests
import os
from markdownify import markdownify as md 

URL = "https://support.optisigns.com/api/v2/help_center/articles.json?per_page=30"
OUTPUT_DIR = "docs"

def get_articles():
    print(f"Starting scraper. Fetch data from: {URL}...")
    
    try:
        #Step 1: Request data from Zendesk
        response = requests.get(URL)
        
        #Check the request was successful (HTTP 200)
        if response.status_code != 200:
            print(f"Error: Failed to fetch data. Status Code: {response.status.code}")
            return
        
        #Step 2: Parse JSON response
        data = response.json()
        articles = data.get('articles', [])
        
        print(f"Successfully fetched {len(articles)} articles.")
        
        #Create output directory if it doesn't exist
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)
            print(f"Created directory: {OUTPUT_DIR}")
            
        #Step 3: Process each article and convert to Markdown
        for article in articles:
            article_id = article['id']
            title = article['title']
            body_html = article['body']
            link = article['html_url']
            
            #Skip articles with empty body
            if not body_html:
                print(f"Skipping article ID {article_id}.")
                continue
            
            #Convert HTML to clean Markdown
            #heading_style="ATX" ensures standard Markdown headers (#, ##)
            markdown_content = md(body_html, heading_style="ATX")
            
            #Format the final file content
            final_content = f"#{title}\n\nSource: {link} \n\n{markdown_content}"
            
            #Save to file
            filename = f"{OUTPUT_DIR}/{article_id}.md"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(final_content)
                
            print(f"Saved: {filename}")
            
        print("\n Scraping completed successfully!")
        
    except Exception as e:
        print(f"An unexpected error occured {e}")
        
#Entry Point
if __name__ == "__main__":
    get_articles()