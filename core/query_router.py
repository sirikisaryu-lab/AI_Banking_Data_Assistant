import logging
from core.intent_classifier import classify_intent
from structured.sql_engine import generate_sql
from db.schema_loader import fetch_schema
from db.db_executor import execute_query
from llm.prompts import STRUCTURED_PROMPT, UNSTRUCTURED_PROMPT, CLIENT360_INSIGHTS_PROMPT, EXPLAINABILITY_PROMPT
from llm.llm_client import chat_completion
from rag.rag_engine import RAGEngine
from security.sql_validator import ForbiddenSQLError

logger = logging.getLogger(__name__)

MAX_SQL_RETRIES = 3
SQL_FAILURE_MESSAGE = (
    "I was unable to retrieve the data due to a technical issue with the query. "
    "Please try rephrasing your question or contact support if the problem persists."
)

rag_engine = RAGEngine()


def execute_with_retry(user_query: str, schema: str, intent: str, conversation_history: list = None):
    """
    Generate SQL and execute it against the DB.
    On failure, regenerates SQL up to MAX_SQL_RETRIES times, passing the
    previous SQL + error back to the LLM so it can self-correct.

    ForbiddenSQLError is caught immediately and re-raised without retrying —
    there is no point regenerating a query the user was never allowed to run.

    Returns:
        dict: Query result with 'columns' and 'rows' on success.

    Raises:
        ForbiddenSQLError: Immediately, without retrying, when a disallowed
                           operation (DELETE, DROP, etc.) is detected.
        RuntimeError:      After all retries are exhausted for genuine DB errors.
    """
    sql = None
    last_error = None

    for attempt in range(1, MAX_SQL_RETRIES + 1):
        error_feedback = (
            f"SQL that failed:\n{sql}\n\nDatabase error:\n{last_error}"
            if last_error else None
        )

        try:
            sql = generate_sql(
                user_query, schema, intent,
                error_feedback=error_feedback,
                conversation_history=conversation_history
            )
            logger.info(f"[Attempt {attempt}/{MAX_SQL_RETRIES}] Generated SQL:\n{sql}")
            print(f"[Attempt {attempt}/{MAX_SQL_RETRIES}] Generated SQL:\n{sql}")

            result = execute_query(sql)
            logger.info(f"[Attempt {attempt}] SQL executed successfully.")
            return result  # ✅ success — exit immediately

        except ForbiddenSQLError:
            logger.warning(f"[Attempt {attempt}] Forbidden SQL detected. Halting immediately.")
            print(f"[Attempt {attempt}] Forbidden SQL detected. Halting immediately.")
            raise  # re-raise so handle_query returns the right message

        except Exception as e:
            last_error = str(e)
            logger.warning(f"[Attempt {attempt}/{MAX_SQL_RETRIES}] SQL execution failed: {last_error}")
            print(f"[Attempt {attempt}/{MAX_SQL_RETRIES}] SQL execution failed: {last_error}")

            if attempt == MAX_SQL_RETRIES:
                logger.error(f"All {MAX_SQL_RETRIES} SQL attempts exhausted. Last error: {last_error}")
                raise RuntimeError(last_error)

def structured_insights(user_query, data_result, conversation_history=None):
    return chat_completion(
        "Generate structured data insights.",
        STRUCTURED_PROMPT.format(question=user_query, data=data_result),
        conversation_history=conversation_history
    )

def unstructured_insights(user_query, data_result, conversation_history=None):
    return chat_completion(
        "Generate unstructured data insights.",
        UNSTRUCTURED_PROMPT.format(user_query=user_query, data_result=data_result),
        conversation_history=conversation_history
    )

def client360_insights(user_query, combined_data, conversation_history=None):
    return chat_completion(
        "Generate client 360 insights.",
        CLIENT360_INSIGHTS_PROMPT.format(user_query=user_query, combined_data=combined_data),
        conversation_history=conversation_history
    )


# ── Data source labels per intent ──────────────────────────────────────────────
DATA_SOURCES = {
    "STRUCTURED_DATA_QUERY": ["Snowflake Database"],
    "UNSTRUCTURED_DATA_QUERY": ["Document Store (RAG)"],
    "CLIENT360": ["Snowflake Database", "Document Store (RAG)"],
    "GREETING": [],
}


def generate_explanation(user_query: str, answer: str, intent: str) -> dict:
    """
    Produce explainability metadata for a given response.

    Args:
        user_query: The original user question.
        answer:     The AI-generated answer text.
        intent:     The classified intent string.

    Returns:
        dict with keys:
            - reasoning    (str)  — LLM-generated reasoning summary
            - data_sources (list) — programmatically determined source labels
    """
    import json

    data_sources = DATA_SOURCES.get(intent, [])

    # Skip LLM call for greetings — nothing to explain
    if intent == "GREETING" or not answer:
        return {"reasoning": "This was a greeting response — no data was queried.", "data_sources": data_sources}

    try:
        raw = chat_completion(
            "You are an AI explainability assistant. Return only valid JSON.",
            EXPLAINABILITY_PROMPT.format(user_query=user_query, answer=answer),
            temperature=0
        )
        raw = raw.strip().replace("```json", "").replace("```", "").strip()
        parsed = json.loads(raw)
        reasoning = parsed.get("reasoning", "Reasoning not available.")
    except Exception as e:
        logger.warning(f"Explainability generation failed: {e}")
        reasoning = "Reasoning could not be generated for this response."

    return {"reasoning": reasoning, "data_sources": data_sources}

def handle_query(user_query: str, conversation_history: list = None):
    """
    Route the user query to the appropriate handler based on classified intent.

    Returns:
        dict: {
            "response":      str  — the main AI answer,
            "explainability": {
                "reasoning":     str  — why this answer was given,
                "data_sources":  list — which systems were queried
            }
        }
    """
    conversation_history = conversation_history or []

    intent = classify_intent(user_query)
    print(f"Classified Intent: {intent}")

    def build_result(answer: str) -> dict:
        """Attach explainability to any answer before returning."""
        return {
            "response": answer,
            "explainability": generate_explanation(user_query, answer, intent)
        }

    if intent == "GREETING":
        return build_result("Hello! How can I assist you with your banking data today?")

    if intent == "STRUCTURED_DATA_QUERY":
        schema = fetch_schema()
        try:
            result = execute_with_retry(user_query, schema, intent, conversation_history)
            print(f"Query Result:\n{result}")
            answer = structured_insights(user_query, result, conversation_history)
        except ForbiddenSQLError as e:
            answer = str(e)
        except RuntimeError:
            answer = SQL_FAILURE_MESSAGE
        return build_result(answer)

    if intent == "UNSTRUCTURED_DATA_QUERY":
        context = rag_engine.answer(user_query)
        print(f"RAG Engine Context:\n{context}")
        answer = unstructured_insights(user_query, context, conversation_history)
        return build_result(answer)

    if intent == "CLIENT360":
        schema = fetch_schema()
        try:
            structured_data = execute_with_retry(user_query, schema, intent, conversation_history)
            print(f"Structured Data Result:\n{structured_data}")
        except ForbiddenSQLError as e:
            return build_result(str(e))
        except RuntimeError:
            return build_result(SQL_FAILURE_MESSAGE)

        unstructured_data = rag_engine.retrieve(user_query)
        print(f"Unstructured Data Result:\n{unstructured_data}")

        combined_data = f"""
        Structured Data:
        {structured_data}

        Unstructured Data:
        {unstructured_data}
        """
        answer = client360_insights(user_query, combined_data, conversation_history)
        return build_result(answer)

    return build_result("Unable to classify query.")