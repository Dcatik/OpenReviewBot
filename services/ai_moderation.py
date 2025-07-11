from openai import AsyncOpenAI
import json
from config import config

client = AsyncOpenAI(api_key=config.openai_token)


async def check_review(text: str) -> dict:
    try:
        response = await client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are a moderator's assistant. Analyze the following review of an employer. "
                    "Check for the following: "
                    "1. Profanity or insults. "
                    "2. Spam or advertising. "
                    "3. Adequacy and realism of the review. "
                    "Your response must be a JSON object with two keys: 'allowed' (boolean) and 'reason' (a string explaining your decision).",
                },
                {"role": "user", "content": text},
            ],
            temperature=0,
            max_tokens=100,
        )
        result = json.loads(response.choices[0].message.content)
        return result
    except Exception as e:
        return {"allowed": False, "reason": str(e)}