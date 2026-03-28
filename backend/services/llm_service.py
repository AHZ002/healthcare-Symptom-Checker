import os
import json
import logging
from openai import OpenAI
from dotenv import load_dotenv
from backend.models.schemas import SymptomAnalysis, Condition

load_dotenv()


# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Client Setup
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise EnvironmentError(
        "GROQ_API_KEY is not set. Please add it to your .env file."
    )

client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

# System Prompt
SYSTEM_PROMPT = """
You are a medical information assistant providing educational health information only.
You are NOT a doctor and do NOT provide medical diagnoses or professional medical advice.

Your role is to help users understand possible conditions related to their symptoms
for educational purposes only, and to guide them toward appropriate next steps.

RESPONSE FORMAT:
You must respond ONLY with a valid JSON object — no preamble, no explanation, no markdown fences.
The JSON must follow this exact structure:

{
  "conditions": [
    {
      "name": "Condition Name",
      "likelihood": "High|Moderate|Low",
      "description": "Brief educational description of this condition and how it relates to the symptoms"
    }
  ],
  "recommended_steps": [
    "Step 1 as a clear actionable instruction",
    "Step 2 as a clear actionable instruction"
  ],
  "urgency_level": "Emergency|High|Moderate|Low",
  "disclaimer": "This information is for educational purposes only and does not constitute medical advice. Please consult a qualified healthcare professional for proper diagnosis and treatment."
}

RULES YOU MUST FOLLOW:
1. Always list 3 to 5 possible conditions ordered from most to least likely.
2. Always provide 3 to 6 clear recommended next steps.
3. Urgency levels mean:
   - Emergency: Life-threatening symptoms, call emergency services immediately
   - High: Seek medical attention within 24 hours
   - Moderate: Schedule a doctor visit within a few days
   - Low: Monitor symptoms, self-care may be appropriate
4. The disclaimer field must always contain the exact disclaimer text shown above.
5. Never suggest specific prescription medications.
6. Never make a definitive diagnosis.
7. Always recommend consulting a healthcare professional.
8. If symptoms suggest a life-threatening emergency, set urgency_level to "Emergency"
   and make the first recommended step "Call emergency services (112 or 108) immediately".
9. Respond ONLY with the JSON object. Any text outside the JSON will break the application.
"""


# Core Function

def analyze_symptoms(symptoms: str) -> SymptomAnalysis:
    """
    Send symptoms to Groq and return a structured SymptomAnalysis.

    Args:
        symptoms: Raw symptom text from the user

    Returns:
        SymptomAnalysis: Validated Pydantic model with conditions,
                         recommended steps, urgency level, and disclaimer

    Raises:
        ValueError: If the LLM returns malformed JSON or missing fields
        RuntimeError: If the API call itself fails
    """

    user_message = f"""
    A user has reported the following symptoms:

    \"\"\"{symptoms}\"\"\"

    Based on these symptoms, provide possible conditions and recommended next steps
    strictly following the JSON format specified. Remember this is for educational
    purposes only.
    """

    logger.info(f"Sending symptom analysis request to Groq | length={len(symptoms)} chars")

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": user_message}
            ],
            temperature=0.3,
            max_tokens=1500,
        )

        raw_content = response.choices[0].message.content.strip()
        logger.info("Received response from Groq successfully")

    except Exception as e:
        logger.error(f"Groq API call failed: {e}")
        raise RuntimeError(f"Failed to reach the AI service. Please try again. Detail: {str(e)}")

    # Parse & Validate JSON Response
    try:
        # Strip markdown fences if model accidentally adds them
        if raw_content.startswith("```"):
            raw_content = raw_content.split("```")[1]
            if raw_content.startswith("json"):
                raw_content = raw_content[4:]
            raw_content = raw_content.strip()

        parsed = json.loads(raw_content)

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM response as JSON: {e}\nRaw: {raw_content}")
        raise ValueError("The AI returned an unexpected response format. Please try again.")

    # Build & Return Pydantic Model
    try:
        raw_conditions = parsed.get("conditions", [])

        # Flatten if model accidentally returned a nested list
        if raw_conditions and isinstance(raw_conditions[0], list):
            raw_conditions = raw_conditions[0]

        # Deduplicate by condition name — keep first occurrence only
        seen = set()
        unique_conditions = []
        for c in raw_conditions:
            if c["name"] not in seen:
                seen.add(c["name"])
                unique_conditions.append(c)

        conditions = [
            Condition(
                name        = c["name"],
                likelihood  = c["likelihood"],
                description = c["description"]
            )
            for c in unique_conditions
        ]

        analysis = SymptomAnalysis(
            conditions        = conditions,
            recommended_steps = parsed.get("recommended_steps", []),
            urgency_level     = parsed.get("urgency_level", "Moderate"),
            disclaimer        = parsed.get(
                "disclaimer",
                "This information is for educational purposes only. "
                "Please consult a qualified healthcare professional."
            )
        )

        logger.info(f"Analysis complete | urgency={analysis.urgency_level} | conditions={len(conditions)}")
        return analysis

    except (KeyError, TypeError) as e:
        logger.error(f"Failed to build SymptomAnalysis from parsed JSON: {e}")
        raise ValueError("The AI response was missing required fields. Please try again.")