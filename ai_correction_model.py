import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")

# Only initialize client if API key exists
client = Anthropic(api_key=api_key) if api_key else None

def fallback_ai_correction(name_part: str) -> str:
    print(f"Fallback AI correction for: {name_part}")

    # Return original if no key is available
    if not client:
        print("No API key found, returning original name part.")
        return name_part

    prompt = f"Correct the spelling of this Indian name: '{name_part}'. Only return the corrected name. No titles or explanations."

    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=100,
            temperature=0.2,
            system="You are a helpful assistant that corrects Indian names. You also remove common titles from the names and if the name is a single letter, you return it as is.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        corrected_name = response.content[0].text.strip()

        # Fallback if Claude returns an empty response
        if not corrected_name:
            print("Claude returned empty response, using original.")
            return name_part

        return corrected_name

    except Exception as e:
        print(f"Claude Fallback Error: {e}")
        return name_part
