# AI Customer Support Agent (OptiSigns Assignment)

This project implements an intelligent Customer Support Agent powered by OpenAI's Assistant API. It features a specialized scraper that synchronizes OptiSigns Help Center articles with a Vector Store and provides accurate, citation-backed answers using RAG (Retrieval-Augmented Generation).

## Key Features

- **Automated Scraper:** Fetches articles from Zendesk API and converts HTML to clean Markdown.
- **Delta Sync Logic:** Optimizes costs and performance by tracking article timestamps (`tracking.json`) and only uploading new or modified content.
- **RAG Assistant:** Uses OpenAI's `gpt-4o` model with `file_search` (v2) to answer user queries with strictly grounded citations.
- **Dockerized:** Fully containerized application ready for deployment.

---

## Installation & Setup

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.
- An OpenAI API Key.

### 1. Clone the Repository

```bash
git clone [https://github.com/httiendat191/ai-support-bot-assignment](https://github.com/httiendat191/ai-support-bot-assignment)
cd ai-support-bot-assignment
```

### 2. Build the Docker Image

This command packages the application and all its dependencies into a container.

```bash
docker build -t optibot-app .
```

---

## How to Run

Run the agent using the command below.

> **Important:** Replace `sk-PlaceYourActualOpenAIKeyHere` with your actual OpenAI API Key.
> _(The `VECTOR_STORE_ID` is pre-configured with the scraped OptiSigns data)._

```bash
docker run \
  -e OPENAI_API_KEY=sk-PlaceYourActualOpenAIKeyHere \
  -e VECTOR_STORE_ID=vs_697ed0eb32f48191bcf356662e7d3288\
  optibot-app
```

### Expected Output

The system will execute the daily sync job:

1.  Fetch articles from Zendesk.
2.  Check against `tracking.json` history.
3.  Upload only new changes (Delta Sync).

If no new articles are found, you will see:

```text
Starting Daily Job...
Summary: 0 New/Updated, 30 Skipped.
No new updates to upload. System is up to date.
```

---

## Proof of Work

I have recorded a full demo video showing the Docker build process, the "Delta Sync" logic, and the Chatbot answering questions with citations.

**[Click here to watch the Demo Video](https://drive.google.com/file/d/1c8rgy-HXD9kEHDsyvyZgVczBP8okGwNT/view?usp=sharing)**

_(Alternatively, please see the attached video file in the submission email)._

---

## System Architecture

- **Data Source:** OptiSigns Help Center (Zendesk API).
- **Processing:** Python (Requests, Markdownify).
- **AI Engine:** OpenAI Assistants API (Model: `gpt-4o`, Tool: `file_search`).
- **Infrastructure:** Docker Container.

---

**Author:** Truong Tien Dat
