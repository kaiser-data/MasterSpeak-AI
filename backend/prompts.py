PROMPTS = {
    "default": (
        "Please analyze the following text:\n{text}\n\n"
        "Provide a rating for the following criteria (on a scale of 1 to 10):\n"
        "- Clarity: How clear and understandable is the text?\n"
        "- Structure: How well is the text structured?\n"
        "- Filler Words: How many unnecessary filler words are present?\n"
        "Respond in JSON format."
    ),
    "detailed": (
        "Perform a detailed analysis of the following text:\n{text}\n\n"
        "Evaluate the following aspects:\n"
        "- Clarity: Is the text easy to understand? Are there any unclear parts?\n"
        "- Structure: Does the text have a clear structure? Are there an introduction, main body, and conclusion?\n"
        "- Filler Words: How many filler words like 'um', 'so', 'basically' are present?\n"
        "Respond in JSON format with a brief explanation for each rating."
    ),
    "concise": (
        "Perform a quick analysis of the following text:\n{text}\n\n"
        "Rate Clarity, Structure, and Filler Words on a scale of 1 to 10.\n"
        "Respond in JSON format without explanations."
    ),
}


def get_prompt(prompt_type: str) -> str:
    """
    Retrieve a prompt template by its type.

    Args:
        prompt_type (str): The type of prompt to retrieve (e.g., "default", "detailed", "concise").

    Returns:
        str: The prompt template.

    Raises:
        ValueError: If the prompt type is not found.
    """
    if prompt_type not in PROMPTS:
        raise ValueError(f"Unknown prompt type: {prompt_type}")
    return PROMPTS[prompt_type]