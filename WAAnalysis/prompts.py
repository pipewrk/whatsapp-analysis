import ollama
# Define system prompts with examples included for each task


# Function to call the Ollama model for summary with a detailed prompt
def summarize_text_with_ollama(text, model):
    """
    Summarizes the given text using the local Ollama model with an enhanced prompt.
    """
    # Enhanced prompt to guide the model
    prompt = f"""
You are summarizing a chunk of a markdown conversation between a user and an assistant.
Your task is to strictly summarize the key points and important findings from the conversation in bullet point format. 
Only provide the summary—nothing else. Do not add suggestions, comments, or extra words. 

### Example Input:
User: I want to discuss setting up a server with high availability.
Assistant: Sure, we can look at redundancy and load balancing options.

User: I'd also like to implement automated backups and failover strategies.
Assistant: For backups, you can consider cloud storage or RAID solutions.

### Example Output:
- Discussion on server setup with high availability.
- Considered redundancy and load balancing as options.
- Automated backups and failover strategies were introduced.
- Suggestions: cloud storage and RAID solutions for backups.

Now, summarize the following text:
{text}
"""

    response = ollama.generate(model=model, prompt=prompt, options={
      "temperature": 0
    })
    return response['response']  # Adjust based on actual API response format


# Topics Extraction
topics_prompt_system = """
You are an AI assistant specialized in extracting topics or themes from a conversation or document.
Your goal is to identify key topics from the provided conversation. 
Here’s an example of how to do it:

Conversation:
---
Jason: I think we need to figure out how to handle our communication better. I feel like things are falling apart.
Elizabeth: Well, it’s not just about communication. You don’t spend enough time with the children. And I’m always stuck doing everything.
Jason: That’s not fair. I’m working hard to provide for the family.
---

Expected output:
{
  "topics": [
    "communication breakdown",
    "family time",
    "work-life balance"
  ]
}

Now, do the same for the following conversation:
"""

# Key Points Extraction
key_points_prompt_system = """
You are an AI assistant specialized in summarizing conversations. 
Your goal is to extract key points from the provided conversation. 
Here’s an example of how to do it:

Conversation:
---
Jason: I think we need to figure out how to handle our communication better. I feel like things are falling apart.
Elizabeth: Well, it’s not just about communication. You don’t spend enough time with the children. And I’m always stuck doing everything.
Jason: That’s not fair. I’m working hard to provide for the family.
---

Expected output:
{
  "key_points": [
    "Jason expresses concern about communication.",
    "Elizabeth raises the issue of Jason not spending enough time with the children.",
    "Jason defends his work commitments as providing for the family."
  ]
}

Now, do the same for the following conversation:
"""

# Sentiment Analysis
sentiment_prompt_system = """
You are an AI assistant specialized in analyzing sentiment in conversations. 
Your goal is to analyze the overall sentiment of the provided conversation.
Here’s an example of how to do it:

Conversation:
---
Jason: I think we need to figure out how to handle our communication better. I feel like things are falling apart.
Elizabeth: Well, it’s not just about communication. You don’t spend enough time with the children. And I’m always stuck doing everything.
Jason: That’s not fair. I’m working hard to provide for the family.
---

Expected output:
{
  "sentiment": "Negative",
  "polarity": -0.6,
  "subjectivity": 0.8
}

Now, do the same for the following conversation:
"""

# Entity Extraction
entities_prompt_system = """
You are an AI assistant specialized in extracting named entities and their relationships from conversations. 
Your goal is to identify people, their roles, and their relationships based on the provided conversation. 
Here’s an example of how to do it:

Conversation:
---
Jason: I think we need to figure out how to handle our communication better. I feel like things are falling apart.
Elizabeth: Well, it’s not just about communication. You don’t spend enough time with the children. And I’m always stuck doing everything.
Jason: That’s not fair. I’m working hard to provide for the family.
---

Expected output:
{
  "entities": [
    {
      "person": "Jason",
      "role": "father",
      "relationships": [
        "expresses concern about communication",
        "defends his work commitments"
      ]
    },
    {
      "person": "Elizabeth",
      "role": "mother",
      "relationships": [
        "accuses Jason of not spending enough time with the children",
        "expresses frustration with doing everything at home"
      ]
    }
  ]
}

Now, do the same for the following conversation:
"""

# Functions to format the prompts with the document content
def create_topics_prompt(document_content):
    return {
        "system": topics_prompt_system,
        "user": document_content
    }

def create_key_points_prompt(document_content):
    return {
        "system": key_points_prompt_system,
        "user": document_content
    }

def create_sentiment_prompt(document_content):
    return {
        "system": sentiment_prompt_system,
        "user": document_content
    }

def create_entities_prompt(document_content):
    return {
        "system": entities_prompt_system,
        "user": document_content
    }
