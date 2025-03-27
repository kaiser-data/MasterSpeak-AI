import os
from openai import OpenAI

# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_text_with_gpt(text: str):
    """
    Analyze the given text using OpenAI's GPT-4 Mini and return a structured response.
    """
    try:
        # Define the prompt for GPT-4 Mini
        prompt = (
            f"Bitte analysiere den folgenden Text:\n{text}\n\n"
            "Gebe eine Bewertung für die folgenden Kriterien (jeweils auf einer Skala von 1 bis 10):\n"
            "- Klarheit: Wie klar und verständlich ist der Text?\n"
            "- Struktur: Wie gut ist der Text strukturiert?\n"
            "- Füllwörter: Wie viele unnötige Füllwörter enthält der Text?\n"
            "Antworte im JSON-Format."
        )

        # Send the request to OpenAI
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Use the appropriate model
            messages=[
                {"role": "system", "content": "Du bist ein Experte für Textanalyse."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=200,
        )

        # Extract the response content
        analysis = response.choices[0].message.content

        # Parse the JSON response
        import json
        analysis_data = json.loads(analysis)

        return analysis_data

    except Exception as e:
        print(f"Error analyzing text with OpenAI: {e}")
        raise