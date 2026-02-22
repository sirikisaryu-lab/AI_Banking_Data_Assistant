from openai import OpenAI
from config.settings import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

# Max number of past messages to send to the LLM (each turn = 2 messages: user + assistant).
HISTORY_WINDOW = 2


def chat_completion(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0,
    conversation_history: list = None
):
    """
    Call the OpenAI chat completion API.

    Args:
        system_prompt:         The system-level instruction for the LLM.
        user_prompt:           The current user message / task prompt.
        temperature:           Sampling temperature (0 = deterministic).
        conversation_history:  Optional list of prior turns in the format:
                               [{"role": "user"|"assistant", "content": "..."}]
                               Injected between the system prompt and the
                               current user message so the LLM has context
                               for follow-up questions.
    """
    messages = [{"role": "system", "content": system_prompt}]

    # Inject the tail of the conversation history (most recent HISTORY_WINDOW messages)
    if conversation_history:
        recent_history = conversation_history[-HISTORY_WINDOW:]
        for turn in recent_history:
            role = turn.get("role")
            content = turn.get("content", "")
            # Only include valid OpenAI roles; skip anything malformed
            if role in ("user", "assistant") and content:
                messages.append({"role": role, "content": content})

    # Current user prompt always goes last
    messages.append({"role": "user", "content": user_prompt})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=temperature,
        messages=messages
    )
    return response.choices[0].message.content