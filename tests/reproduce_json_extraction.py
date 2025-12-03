
import json
import re
import logging

# Mock logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def _extract_json_from_response(response_text: str, required_keys: list = None) -> dict:
    """
    Extract JSON from agent response, handling various formats.
    """
    # Strategy 1: Try direct parsing
    try:
        data = json.loads(response_text.strip())
        if required_keys:
             if all(key in data for key in required_keys):
                 return data
        else:
            return data
    except json.JSONDecodeError:
        pass
    
    # Strategy 2: Remove markdown code fences
    cleaned = response_text.replace("```json", "").replace("```", "").strip()
    try:
        data = json.loads(cleaned)
        if required_keys:
             if all(key in data for key in required_keys):
                 return data
        else:
            return data
    except json.JSONDecodeError:
        pass
    
    # Strategy 3: Extract JSON object using regex
    # Look for content between { and } that appears to be JSON
    json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
    matches = re.findall(json_pattern, response_text, re.DOTALL)
    
    for match in matches:
        try:
            # Try to parse this potential JSON
            data = json.loads(match)
            # Verify it has expected keys for our use case
            if isinstance(data, dict) and len(data) > 0:
                if required_keys:
                    if all(key in data for key in required_keys):
                        logger.info(f"Successfully extracted JSON with required keys: {required_keys}")
                        return data
                    else:
                        logger.info(f"Skipping JSON without required keys: {list(data.keys())}")
                        continue
                else:
                    logger.info(f"Successfully extracted JSON from mixed content")
                    return data
        except json.JSONDecodeError:
            continue
    
    # If all strategies fail, raise an error with helpful context
    raise ValueError(
        f"Could not extract valid JSON from response. "
        f"Response preview (first 300 chars): {response_text[:300]}"
    )

# Test case simulating the user's issue
response_text = """
Here is the literature review:
{
    "title": "Multi-objective optimization of wind turbines",
    "url": "https://researchgate.net/...",
    "source": "ResearchGate"
}

And here is the problem definition:
{
    "problem_statement": "The integration of wind turbines...",
    "main_research_question": "How to optimize...?",
    "secondary_questions": [],
    "key_variables": [],
    "preliminary_literature": []
}
"""

print("--- Testing WITHOUT required keys (Current Behavior) ---")
try:
    data = _extract_json_from_response(response_text)
    print(f"Extracted keys: {list(data.keys())}")
    if "problem_statement" not in data:
        print("FAILURE: Extracted wrong JSON object (missing 'problem_statement')")
    else:
        print("SUCCESS: Extracted correct JSON object")
except Exception as e:
    print(f"ERROR: {e}")

print("\n--- Testing WITH required keys (Proposed Fix) ---")
try:
    data = _extract_json_from_response(response_text, required_keys=["problem_statement", "main_research_question"])
    print(f"Extracted keys: {list(data.keys())}")
    if "problem_statement" in data:
        print("SUCCESS: Extracted correct JSON object with required keys")
    else:
        print("FAILURE: Did not extract object with required keys")
except Exception as e:
    print(f"ERROR: {e}")
