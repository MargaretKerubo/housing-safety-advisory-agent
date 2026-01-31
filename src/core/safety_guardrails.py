"""
Safety Guardrails Module

Provides input validation, stereotype detection, and query reframing
to ensure the agent doesn't perpetuate biases or make authoritative claims.

Based on Documentation-guide principles:
- Advisory, not authoritative
- Refuse or reframe problematic queries
- No stigmatizing language or labels
"""

import re
from typing import Tuple, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum


class QueryType(Enum):
    """Classification of user query types."""
    STANDARD = "standard"
    BIASED = "biased"
    STEREOTYPICAL = "stereotypical"
    DANGEROUS_AREA_QUERY = "dangerous_area_query"
    SAFETY_RANKING = "safety_ranking"
    CRIME_PREDICTION = "crime_prediction"


@dataclass
class GuardrailResult:
    """Result of guardrail validation."""
    is_safe: bool
    query_type: QueryType
    reframed_query: Optional[str]
    warning_message: Optional[str]
    advisory_disclaimer: Optional[str]


# Stereotype detection patterns
STEREOTYPE_PATTERNS = [
    # Area-based stereotypes
    r'\b(dangerous|unsafe|risk[ey]|crime-ridden|ghetto|slum)\b',
    r'\b(avoid|stay away from|never go to)\b.*\b(area|neighborhood|place)\b',
    r'\b(people from|residents of)\b.*\b(are|is|can be)\b.*\b(dangerous|poor|criminal)\b',
    r'\b(avoid|don\'t live in|never move to)\s+(kibera|mathare|kiambiu| Dandora|estcourt|lavington)\b',
    
    # Safety ranking queries
    r'\b(which|safe|dangerous|unsafe|risky)\b.*\b(area|neighborhood|place)\b',
    r'\b(best|worst|most safe|most dangerous|top|worst)\b.*\b(area|neighborhood)\b',
    r'\b(crime rate|most dangerous|safest)\b',
    
    # Authority claims
    r'\b(is safe|is dangerous|will be|guarantee|certain)\b',
    
    # Predictions
    r'\b(will (happen|be|get)|going to|likely to)\b.*\b(robbed|attacked|harmed|crime)\b',
]

# Query type patterns for classification
QUERY_TYPE_PATTERNS = {
    QueryType.DANGEROUS_AREA_QUERY: [
        r'\b(which.*dangerous|which.*unsafe|areas.*dangerous|areas.*unsafe|dangerous areas|unsafe areas)\b',
        r'\b(most dangerous|safest|highest crime)\b',
    ],
    QueryType.SAFETY_RANKING: [
        r'\b(rank|rating|score)\b.*\b(area|neighborhood|safety|security)\b',
        r'\b(safe.*rating|security.*rating|compare.*safety)\b',
    ],
    QueryType.CRIME_PREDICTION: [
        r'\b(will.*happen|likely.*crime|probability.*robbed|future.*crime)\b',
        r'\b(predict|forecast)\b.*\b(crime|robbery|attack)\b',
    ],
    QueryType.STEREOTYPICAL: [
        r'\b(kibera|mathare|kiambiu)\b.*\b(dangerous|unsafe|bad)\b',
        r'\b(poor.*area|rich.*area|rich.*neighborhood)\b.*\b(safe|dangerous)\b',
    ],
}

# Nairobi areas that often get stereotyped
STEREOTYPED_AREAS = [
    'kibera', 'mathare', 'kiambiu', 'dandora', 'kangundo', 
    'huruma', 'bondeni', 'laini saba', 'githurai', 'muguru'
]


def detect_query_type(user_input: str) -> QueryType:
    """
    Classifies the type of user query.
    
    Args:
        user_input: The user's query text
        
    Returns:
        QueryType enum indicating the classification
    """
    input_lower = user_input.lower()
    
    for query_type, patterns in QUERY_TYPE_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, input_lower):
                return query_type
    
    # Check for stereotypes
    for pattern in STEREOTYPE_PATTERNS:
        if re.search(pattern, input_lower):
            return QueryType.STEREOTYPICAL
    
    return QueryType.STANDARD


def contains_stereotype(user_input: str) -> Tuple[bool, Optional[str]]:
    """
    Detects if user input contains stereotypes about areas.
    
    Args:
        user_input: The user's query text
        
    Returns:
        Tuple of (contains_stereotype, detected_pattern)
    """
    input_lower = user_input.lower()
    
    for pattern in STEREOTYPE_PATTERNS:
        match = re.search(pattern, input_lower)
        if match:
            return True, match.group()
    
    # Check for specific area stereotypes
    for area in STEREOTYPED_AREAS:
        if area in input_lower:
            dangerous_words = ['dangerous', 'unsafe', 'bad', 'avoid', 'never']
            for word in dangerous_words:
                if word in input_lower:
                    return True, f"{area} + {word}"
    
    return False, None


def extract_stereotyped_area(user_input: str) -> Optional[str]:
    """
    Extracts the name of any area mentioned in a stereotypical context.
    
    Args:
        user_input: The user's query text
        
    Returns:
        The area name if found, None otherwise
    """
    input_lower = user_input.lower()
    
    for area in STEREOTYPED_AREAS:
        if area in input_lower:
            return area
    
    return None


def reframe_query(user_input: str, query_type: QueryType) -> str:
    """
    Reframes problematic queries to be more advisory and neutral.
    
    Args:
        user_input: The original user query
        query_type: The classified type of query
        
    Returns:
        Reframed query that focuses on trade-offs and considerations
    """
    reframed = user_input
    
    if query_type == QueryType.DANGEROUS_AREA_QUERY:
        reframed = re.sub(
            r'(which.*dangerous|which.*unsafe|areas.*dangerous|areas.*unsafe)',
            'what factors should I consider for',
            user_input,
            flags=re.IGNORECASE
        )
        reframed += ". I'm interested in understanding trade-offs between safety, budget, and commute."
    
    elif query_type == QueryType.SAFETY_RANKING:
        reframed = re.sub(
            r'(safest|most safe|most dangerous|best.*safety|worst.*safety)',
            'with various safety considerations',
            user_input,
            flags=re.IGNORECASE
        )
        reframed = re.sub(
            r'(which.*area|which.*neighborhood)',
            'what should I consider when choosing',
            reframed,
            flags=re.IGNORECASE
        )
    
    elif query_type == QueryType.CRIME_PREDICTION:
        reframed = re.sub(
            r'(will.*happen|likely|crime probability|predict)',
            'what situational factors affect',
            user_input,
            flags=re.IGNORECASE
        )
        reframed = "I can help you understand " + reframed.lower()
    
    elif query_type == QueryType.STEREOTYPICAL:
        area = extract_stereotyped_area(user_input)
        if area:
            # Replace the stereotypical statement with a neutral inquiry
            reframed = re.sub(
                rf'\b({area}.*dangerous|{area}.*unsafe|{area}.*bad|avoid {area}|never {area})\b',
                f"I have some concerns about {area.title()}. What are the key factors I should consider?",
                user_input,
                flags=re.IGNORECASE
            )
        reframed += ". I'd like to understand the trade-offs between different housing options."
    
    return reframed


def generate_advisory_disclaimer(query_type: QueryType) -> str:
    """
    Generates an appropriate advisory disclaimer based on query type.
    
    Uses positive framing language that empowers users with actionable information
    rather than negative labels.
    
    Args:
        query_type: The classified type of query
        
    Returns:
        Advisory disclaimer text
    """
    disclaimers = {
        QueryType.DANGEROUS_AREA_QUERY: (
            "I can help you evaluate housing options based on your specific needs, "
            "budget, and commute considerations. Instead of labeling areas, I focus on "
            "objective factors like lighting, transport availability, and community initiatives. "
            "What factors matter most to you?"
        ),
        QueryType.SAFETY_RANKING: (
            "I don't rank neighborhoods by safety - these labels can be misleading and "
            "perpetuate stereotypes. Instead, I can help you understand contextual factors "
            "like street lighting, transport hours, and strategies that residents use. "
            "What specific concerns do you have?"
        ),
        QueryType.CRIME_PREDICTION: (
            "I don't make predictions about safety outcomes. I can help you understand "
            "situational factors you can influence - like commute timing, transport mode, "
            "and community resources. Would you like to explore these instead?"
        ),
        QueryType.STEREOTYPICAL: (
            "I aim to provide balanced, evidence-based information without relying on "
            "stereotypes. Every area has diverse communities with varying experiences. "
            "I can help you understand factors to consider and strategies that work for "
            "residents in different areas."
        ),
        QueryType.BIASED: (
            "Let me help you focus on objective factors like budget, commute, and amenities "
            "rather than generalizations. I can also share strategies that residents in "
            "various areas use to navigate their environments safely. What criteria matter most?"
        ),
        QueryType.STANDARD: None,
    }
    
    return disclaimers.get(query_type)


def generate_warning_message(stereotype: str, area: Optional[str] = None) -> Optional[str]:
    """
    Generates a warning message when stereotypes are detected.
    
    Args:
        stereotype: The detected stereotype pattern
        area: Optional area name that was stereotyped
        
    Returns:
        Warning message or None
    """
    if area:
        return (
            f"I noticed you mentioned concerns about {area.title()}. "
            "Rather than relying on generalizations, I can help you understand "
            "specific factors like commute, budget, and amenities. "
            "Would you like to discuss your priorities?"
        )
    
    return (
        "I noticed your query includes some assumptions about safety. "
        "I aim to provide balanced, advisory information rather than perpetuating stereotypes. "
        "Let me help you focus on specific factors relevant to your situation."
    )


def validate_query(user_input: str) -> GuardrailResult:
    """
    Main function to validate user input and apply guardrails.
    
    Args:
        user_input: The user's query text
        
    Returns:
        GuardrailResult with validation results and recommendations
    """
    # Classify the query
    query_type = detect_query_type(user_input)
    
    # Check for stereotypes
    has_stereotype, stereotype_pattern = contains_stereotype(user_input)
    
    # Extract any stereotyped areas
    area = extract_stereotyped_area(user_input) if has_stereotype else None
    
    # Determine if query is safe
    is_safe = query_type == QueryType.STANDARD and not has_stereotype
    
    # Generate reframed query
    reframed_query = None
    if not is_safe:
        reframed_query = reframe_query(user_input, query_type)
    
    # Generate warnings and disclaimers
    warning_message = None
    if has_stereotype:
        warning_message = generate_warning_message(stereotype_pattern, area)
    
    advisory_disclaimer = generate_advisory_disclaimer(query_type)
    
    return GuardrailResult(
        is_safe=is_safe,
        query_type=query_type,
        reframed_query=reframed_query,
        warning_message=warning_message,
        advisory_disclaimer=advisory_disclaimer
    )


def inject_safety_context(prompt: str, context: Dict[str, Any] = None) -> str:
    """
    Injects safety context into a prompt to guide AI behavior.
    
    Args:
        prompt: The original prompt
        context: Optional context dictionary with user info
        
    Returns:
        Prompt with safety context prepended
    """
    safety_instructions = """
    IMPORTANT SAFETY GUIDELINES:
    
    1. You are an ADVISORY agent, not an authority. Do not make definitive claims about areas being "safe" or "dangerous".
    
    2. Do NOT accept user stereotypes as facts. If a user says "X area is dangerous," do not repeat this as fact. Instead, focus on specific factors.
    
    3. Focus on TRADE-OFFS (cost vs commute vs amenities) rather than predictions or labels.
    
    4. Present BALANCED perspectives - every area has diverse communities and experiences.
    
    5. Use neutral language: "factors to consider" instead of "dangerous areas."
    
    6. Include advisory language: "Based on your criteria..." not "You should..."
    
    7. Acknowledge uncertainty: "Factors to consider include..." not "This area is safe."
    
    Remember: Your role is to help users make informed decisions, not to label neighborhoods.
    
    """
    
    if context:
        context_info = f"\nUser Context:\n- Budget: KES {context.get('budget', 'Not specified')}\n- Location: {context.get('location', 'Not specified')}\n- Workplace: {context.get('workplace', 'Not specified')}\n"
        safety_instructions += context_info
    
    return safety_instructions + "\n" + prompt


def postprocess_response(response: str) -> str:
    """
    Post-processes AI response to remove any remaining authoritative claims.
    
    Args:
        response: The AI generated response
        
    Returns:
        Cleaned response with potentially problematic phrases replaced
    """
    # Remove authoritative claims
    replacements = [
        (r'\b(this area is|these areas are|that area is)\b', 'factors to consider in'),
        (r'\b(is safe|is dangerous|is risky|is unsafe)\b', 'has various characteristics to consider'),
        (r'\b(guarantee|certain|definitely|will be)\b', 'may be considered'),
        (r'\b(never|always)\b', 'often'),
        (r'\b(most dangerous|safest|highest crime)\b', 'various considerations'),
    ]
    
    cleaned = response
    for pattern, replacement in replacements:
        cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)
    
    # Add advisory disclaimer if not present
    if "Based on your specific needs" not in cleaned and "considerations" in cleaned.lower():
        cleaned += "\n\n*This is advisory information. Always visit areas personally and consult local sources for the most current information.*"
    
    return cleaned


# Example usage
if __name__ == "__main__":
    test_queries = [
        "I am moving from Kisumu to Nairobi. My budget is 100000 and my new workplace will be around Prestige Plaza. I prefer safe areas and I have been told Kibera is a very dangerous place.",
        "Which areas in Nairobi are most dangerous?",
        "What is the safest neighborhood in Nairobi?",
        "Is Kibera safe to live in?",
        "I want to live in a safe area near Prestige Plaza with budget of 50000."
    ]
    
    print("=" * 80)
    print("SAFETY GUARDRAILS TEST")
    print("=" * 80)
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        result = validate_query(query)
        print(f"Type: {result.query_type.value}")
        print(f"Safe: {result.is_safe}")
        print(f"Warning: {result.warning_message}")
        print(f"Reframed: {result.reframed_query}")
        print("-" * 40)

