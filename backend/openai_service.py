# openai_service.py
import os
from dotenv import load_dotenv
from openai import OpenAI
from prompts import get_prompt  # Import the get_prompt function
import json

# Load environment variables from .env file
load_dotenv()

# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_text_with_gpt(text: str, prompt_type: str):
    try:
        # Dynamically load the prompt template
        prompt_template = get_prompt(prompt_type)

        # Replace the placeholder `{text}` in the prompt template with the actual text
        prompt = prompt_template.format(text=text)

        # Send the request to OpenAI
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Use the appropriate model
            messages=[
                {"role": "system", "content": "You are an expert in text analysis. Return all responses as valid JSON."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=200,
        )

        # Extract the response content
        analysis = response.choices[0].message.content

        # Strip Markdown-style backticks and surrounding whitespace
        if analysis.startswith("```") and analysis.endswith("```"):
            analysis = analysis.strip("```").strip()
            if analysis.lower().startswith("json"):
                analysis = analysis[4:].strip()

        # Parse the JSON response
        import json
        try:
            analysis_data = json.loads(analysis)
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON response: {analysis}")
            raise e

        return analysis_data

    except Exception as e:
        print(f"Error analyzing text with OpenAI: {e}")
        raise

# Add a test case at the end of the script
if __name__ == "__main__":
    # Define test inputs
    test_text = "This is a sample text for analysis."
    test_prompt_type = "default"

    try:
        # Call the function with test inputs
        result = analyze_text_with_gpt(test_text, test_prompt_type)

        # Print the result
        print("Test Result:")
        print(json.dumps(result, indent=4))

    except Exception as e:
        # Handle any errors during the test
        print(f"Test failed with error: {e}")