# AI Provider Abstraction

## Overview

The Housing Safety Advisory Agent uses an interface-based abstraction layer for AI integrations, allowing seamless switching between different AI providers (Gemini, OpenAI, etc.).

## Architecture

```
src/ai/
├── base.py              # Abstract base class (AIProvider)
├── gemini_provider.py   # Gemini implementation
├── openai_provider.py   # OpenAI implementation
├── factory.py           # Provider factory
└── __init__.py          # Module exports
```

## Switching Between Providers

Set the `AI_PROVIDER` environment variable in your `.env` file:

```bash
# Use OpenAI
AI_PROVIDER=openai

# Use Gemini (default)
AI_PROVIDER=gemini
```

## Adding a New Provider

1. Create a new provider class in `src/ai/`:

```python
from .base import AIProvider

class NewProvider(AIProvider):
    def __init__(self, api_key: str):
        # Initialize your client
        pass
    
    def generate_content(self, contents, temperature=0.3, response_format="json"):
        # Implement the interface
        pass
```

2. Update `factory.py`:

```python
from .new_provider import NewProvider

def get_ai_provider() -> AIProvider:
    provider_type = os.getenv("AI_PROVIDER", "gemini").lower()
    
    if provider_type == "newprovider":
        api_key = os.getenv("NEWPROVIDER_API_KEY")
        return NewProvider(api_key)
    # ... existing providers
```

3. Add API key to `.env`:

```bash
NEWPROVIDER_API_KEY=your_key_here
AI_PROVIDER=newprovider
```

## Interface Contract

All providers must implement:

```python
def generate_content(
    self,
    contents: List[Dict],  # [{"role": "user", "content": "..."}]
    temperature: float = 0.3,
    response_format: str = "json"  # "json" or "text"
) -> str:
    """Returns the generated text response."""
```

## Benefits

- **Flexibility**: Switch providers without code changes
- **Resilience**: Fallback to alternative providers if one fails
- **Testing**: Easy to mock for unit tests
- **Cost optimization**: Use different providers based on cost/performance needs
