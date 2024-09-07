
# Define system prompts with examples included for each task

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
