# AI Provider Abstraction

## Why This Exists

The application makes three AI calls for every housing request — one to analyse the user's input, one to research neighbourhoods, and one to format the final response. Early in development the project used Google Gemini directly. When Gemini became unavailable, every file that made an AI call had to be changed individually.

The abstraction layer solves this by giving the rest of the application a single, stable interface to call. The underlying provider — Gemini, OpenAI, or anything else — is an implementation detail that can be swapped out in one place without touching any business logic.

---

## Where the Code Lives

```
backend/app/ai/
├── base.py              ← The interface (AIProvider abstract class)
├── gemini_provider.py   ← Gemini implementation
├── openai_provider.py   ← OpenAI implementation
├── factory.py           ← Reads config and returns the correct provider
└── __init__.py          ← Exports
```

Nothing outside this folder imports from `gemini_provider.py` or `openai_provider.py` directly. The rest of the application only ever sees `AIProvider` and calls `get_ai_provider()`.

---

## The Interface

`base.py` defines the contract that every provider must honour:

```python
class AIProvider(ABC):

    @abstractmethod
    def generate_content(
        self,
        contents: List[Dict],   # [{"role": "user", "content": "..."}]
        temperature: float = 0.3,
        response_format: str = "json"  # "json" or "text"
    ) -> str:
        """Returns the generated text response."""
```

`ABC` stands for Abstract Base Class, imported from Python's built-in `abc` module. It does two things:

- **Prevents direct instantiation.** You cannot do `AIProvider()`. The class exists only to be subclassed. It is a template, not a usable object.
- **Enforces the contract.** The `@abstractmethod` decorator means any class that inherits from `AIProvider` *must* implement `generate_content`. If it does not, Python raises a `TypeError` the moment you try to instantiate that class — catching the mistake immediately rather than at the point the missing method is eventually called.

In other languages this pattern is called an **interface** (Java, TypeScript) or a **pure virtual class** (C++). Python calls it an Abstract Base Class.

In practice this means `housing_service.py` can call `self.ai_provider.generate_content(...)` without knowing or caring whether the provider underneath is Gemini, OpenAI, or anything else. As long as the provider passed the `ABC` check at instantiation time, the method is guaranteed to exist.

Every caller passes a list of messages in the same format regardless of which provider is active. Each provider is responsible for translating that into whatever its own SDK expects.

---

## How Each Provider Implements It

### OpenAI (`openai_provider.py`)

Uses the OpenAI Responses API with the `gpt-5-nano` model. Combines all messages into a single input string before sending.

```python
response = self.client.responses.create(
    model="gpt-5-nano",
    input=input_text,
    store=True
)
return response.output_text
```

### Gemini (`gemini_provider.py`)

Uses the `google-genai` SDK with the `gemini-flash-latest` model. Translates the message list into Gemini's `Content`/`Part` format and maps the `assistant` role to `model` (which is what Gemini expects).

```python
response = self.client.models.generate_content(
    model="models/gemini-flash-latest",
    contents=gemini_contents,
    config=types.GenerateContentConfig(
        temperature=temperature,
        response_mime_type="application/json" if response_format == "json" else "text/plain"
    )
)
return response.text
```

---

## The Factory

`factory.py` reads the `AI_PROVIDER` value from config and returns the appropriate instance. This is the only place in the codebase that knows which providers exist.

```python
def get_ai_provider() -> AIProvider:
    if Config.AI_PROVIDER == "openai":
        return OpenAIProvider(Config.OPENAI_API_KEY)
    elif Config.AI_PROVIDER == "gemini":
        return GeminiProvider(Config.GEMINI_API_KEY)
    else:
        raise ValueError(f"Unknown AI provider: {Config.AI_PROVIDER}")
```

The factory is called once per request inside `routes_fastapi.py` when `HousingAdvisoryService` is instantiated. It is not called at import time, which ensures the `.env` file is loaded before any provider is initialised.

---

## Switching Providers

Change one line in `.env`:

```bash
# Use OpenAI (currently active)
AI_PROVIDER=openai

# Switch to Gemini
AI_PROVIDER=gemini
```

Restart the server. No code changes required.

---

## Adding a New Provider

1. Create `backend/app/ai/anthropic_provider.py` (or whichever provider):

```python
from typing import List, Dict
from .base import AIProvider

class AnthropicProvider(AIProvider):

    def __init__(self, api_key: str):
        # initialise your SDK client here
        pass

    def generate_content(
        self,
        contents: List[Dict],
        temperature: float = 0.3,
        response_format: str = "json"
    ) -> str:
        # translate contents into your SDK's format
        # return the response as a plain string
        pass
```

2. Register it in `factory.py`:

```python
from .anthropic_provider import AnthropicProvider

def get_ai_provider() -> AIProvider:
    ...
    elif Config.AI_PROVIDER == "anthropic":
        return AnthropicProvider(Config.ANTHROPIC_API_KEY)
```

3. Add the key to `config/settings.py` and `.env`:

```python
# settings.py
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
```

```bash
# .env
ANTHROPIC_API_KEY=your_key_here
AI_PROVIDER=anthropic
```

That is all. No changes to `housing_service.py`, `routes_fastapi.py`, or any other file.

---

## Key Rules

- **Never import a provider directly** outside of `factory.py`. Always use `get_ai_provider()`.
- **Keep providers stateless** where possible. The provider receives a message list and returns a string — it should not store conversation history or application state.
- **The `response_format` parameter** tells the provider whether to request structured JSON or plain text. Providers that support native JSON mode (like Gemini) should use it. Providers that do not should still return valid JSON when `response_format="json"` is requested — the caller will parse it.
