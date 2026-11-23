import os

def answer_with_ai(question: str, analysis_context: str) -> tuple[str, str]:
    """Use OpenAI if configured; otherwise return a transparent local fallback."""
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return (
            "Natural-language AI answers are not enabled because OPENAI_API_KEY is not configured. "
            "The dataset was still analyzed locally.\n\n"
            "**Dataset analysis context**\n\n" + analysis_context,
            "Local analysis (no API key)",
        )
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=0.2,
            messages=[
                {"role": "system", "content": (
                    "You are a careful data analyst. Answer only from the supplied dataset profile "
                    "and aggregate statistics. Never invent values. If information is insufficient, "
                    "say so. Do not execute code or claim to inspect raw rows."
                )},
                {"role": "user", "content": f"Dataset context:\n{analysis_context}\n\nQuestion: {question}"},
            ],
        )
        answer = response.choices[0].message.content
        return (answer or "The model returned an empty answer.", "OpenAI")
    except Exception as exc:
        return (f"AI request failed. Check API key, model access, and network. Details: {exc}", "AI unavailable")

def answer_question(question: str, analysis_context: str) -> str:
    """Simple text-only wrapper for integrations."""
    return answer_with_ai(question, analysis_context)[0]
