import os
import logging
from fastapi import HTTPException
from groq import Groq

logger = logging.getLogger(__name__)

def summarize_text(text: str) -> str:
    """
    Summarize text using Groq Llama3 model
    """
    try:
        # Truncate if too long
        if len(text) > 4000:
            text = text[:4000] + "..."

        prompt = f"""
        Summarize the following LinkedIn post in one short sentence (max 15 words).
        Avoid hashtags and marketing fluff.

        LinkedIn Post:
        {text}

        Summary:
        """

        client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a concise summarizer."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=50,
            temperature=0.3,
        )

        summary = response.choices[0].message.content.strip()
        summary = summary.replace('"', '').replace('Summary:', '').strip()

        logger.info(f"Generated summary: {summary}")
        return summary

    except Exception as e:
        logger.error(f"Summarization error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error generating summary"
        )
