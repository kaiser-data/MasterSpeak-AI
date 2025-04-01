import os
from dotenv import load_dotenv
from openai import OpenAI
from prompts import get_prompt  # Import the get_prompt function

# Load environment variables from .env file
load_dotenv()

# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def analyze_text_with_gpt(text: str, prompt_type: str):
    """
    Analyze the given text using OpenAI's GPT-4 Mini with a dynamic prompt template.

    Args:
        text (str): The text to be analyzed.
        prompt_type (str): The type of prompt to use for analysis (e.g., "default", "detailed", "concise").

    Returns:
        dict: The structured analysis result in JSON format.
    """
    try:
        # Dynamically load the prompt template
        prompt_template = get_prompt(prompt_type)

        # Replace the placeholder `{text}` in the prompt template with the actual text
        prompt = prompt_template.format(text=text)

        # Send the request to OpenAI
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Use the appropriate model
            messages=[
                {"role": "system", "content": "You are an expert in text analysis."},
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