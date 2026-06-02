from ml.prompts.templates import PROMPT_TEMPLATES


def get_prompt(name: str, version: str = "latest") -> str:
    """Retrieve a versioned prompt template by name.

    Args:
        name: Prompt name (e.g., 'churn_analysis', 'retention_suggestion')
        version: Version string (e.g., 'v1', 'v2') or 'latest'

    Returns:
        Prompt template string

    Raises:
        KeyError: If prompt name or version not found
    """
    if name not in PROMPT_TEMPLATES:
        raise KeyError(f"Prompt '{name}' not found. Available: {list(PROMPT_TEMPLATES.keys())}")

    versions = PROMPT_TEMPLATES[name]
    if version == "latest":
        version = max(versions.keys())

    if version not in versions:
        raise KeyError(f"Version '{version}' not found for prompt '{name}'. Available: {list(versions.keys())}")

    return versions[version]
