from llm.llm_client import chat_completion
from llm.prompts import INTENT_CLASSIFIER_PROMPT

def classify_intent(query: str):
    return chat_completion(
        INTENT_CLASSIFIER_PROMPT,
        query,
        temperature=0
    ).strip()

