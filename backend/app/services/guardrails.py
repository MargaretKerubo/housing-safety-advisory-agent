import re
import logging

logger = logging.getLogger(__name__)

# Patterns that indicate biased, harmful, or out-of-scope queries
_BLOCKED_PATTERNS = [
    r"\bdangerous\s+(area|neighborhood|estate|place|zone)\b",
    r"\b(worst|bad|unsafe|criminal|ghetto|slum)\s+(area|neighborhood|estate|place|zone)\b",
    r"\b(avoid|stay away from)\s+\w+\s*(people|community|tribe|ethnic)\b",
    r"\bwhich\s+(tribe|ethnic|race|community)\b",
    r"\b(crime|criminal)\s+rate\s+ranking\b",
    r"\bmost\s+dangerous\b",
    r"\brank\w*\s+(neighborhood|area|estate)\s+by\s+(crime|safety|danger)\b",
]

# Reframe message shown to the user when a blocked pattern is detected
_REFRAME_MESSAGE = (
    "I'm not able to rank or label areas by danger, crime, or community characteristics — "
    "that kind of framing can be misleading and unfair to residents. "
    "What I can do is help you compare housing options based on practical factors like "
    "commute safety, lighting, transport availability, and proximity to amenities. "
    "Could you tell me where you work and your monthly budget so I can find the best options for you?"
)


def check_input(user_input: str) -> dict:
    """
    Check user input against guardrail rules.

    Returns:
        { "allowed": True } if input is safe to proceed.
        { "allowed": False, "message": str } if input should be blocked and reframed.
    """
    if not user_input or not user_input.strip():
        return {"allowed": False, "message": "Please describe what you are looking for so I can help you."}

    if len(user_input) > 2000:
        return {"allowed": False, "message": "Your message is too long. Please keep it under 2000 characters."}

    lowered = user_input.lower()
    for pattern in _BLOCKED_PATTERNS:
        if re.search(pattern, lowered):
            logger.warning(f"Guardrail triggered for input: {user_input[:100]}")
            return {"allowed": False, "message": _REFRAME_MESSAGE}

    return {"allowed": True}
