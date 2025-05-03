# backend/seed.py

from typing import Dict

# Define the prompts as constants
PROMPTS: Dict[str, str] = {
    "default": (
        "Please analyze the following text:\n{text}\n\n"
        "Provide a rating for the following criteria (on a scale of 1 to 10):\n"
        "- clarity_score: How clear and understandable is the text?\n"
        "- structure_score: How well is the text structured?\n"
        "- filler_words_rating: How many unnecessary filler words are present? (1 = many filler words, 10 = no filler words)\n"
        "Also provide a brief feedback comment.\n"
        "Respond in JSON format with these exact field names."
    ),
    "detailed": (
        "Perform a detailed analysis of the following text:\n{text}\n\n"
        "Evaluate the following aspects:\n"
        "- clarity_score: Is the text easy to understand? Are there any unclear parts? (1-10)\n"
        "- structure_score: Does the text have a clear structure? Are there an introduction, main body, and conclusion? (1-10)\n"
        "- filler_words_rating: How many filler words like 'um', 'so', 'basically' are present? (1 = many, 10 = none)\n"
        "Also provide detailed feedback in the feedback field.\n"
        "Respond in JSON format with these exact field names."
    ),
    "quick": (
        "Perform a quick analysis of the following text:\n{text}\n\n"
        "Rate on a scale of 1 to 10:\n"
        "- clarity_score: Text clarity\n"
        "- structure_score: Text structure\n"
        "- filler_words_rating: Filler words (1 = many, 10 = none)\n"
        "Include a brief feedback.\n"
        "Respond in JSON format with these exact field names."
    ),
}


def get_prompt(prompt_type: str) -> str:
    """
    Retrieve a prompt template by its type.

    Args:
        prompt_type (str): The type of prompt to retrieve (e.g., "default", "detailed", "quick").

    Returns:
        str: The prompt template.

    Raises:
        ValueError: If the prompt type is not found.
    """
    try:
        return PROMPTS[prompt_type]
    except KeyError:
        raise ValueError(f"Unknown prompt type: {prompt_type}")