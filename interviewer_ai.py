import os
import re
from config import Config

# Check Gemini availability
GENAI_AVAILABLE = False
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


def get_gemini_client():
    """Instantiate Google GenAI client if API key is present."""
    api_key = Config.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY", "")
    if not api_key or not GENAI_AVAILABLE:
        return None
    try:
        return genai.Client(api_key=api_key)
    except Exception as e:
        print(f"GenAI Client Init Error: {e}")
        return None


def get_welcome_message(candidate_name, question_title, target_company="Google", difficulty="Medium"):
    """Generate initial interviewer welcome statement."""
    return (
        f"Hello {candidate_name}! Welcome to your technical interview for the Software Engineer role at {target_company}. "
        f"Today, we have a problem titled '{question_title}' ({difficulty} level).\n\n"
        f"Take a minute to read the problem statement and example inputs on the left. "
        f"Before jumping into code, I'd love to hear your initial thoughts: how are you thinking about approaching this? "
        f"Feel free to ask any clarifying questions or state your assumptions."
    )


def rule_based_interviewer_response(message, session_data, current_code=""):
    """
    Intelligent conversational fallback when Gemini API is unavailable or offline.
    """
    msg_lower = message.lower()
    q_title = session_data.get("question_title", "the problem")
    hints = session_data.get("question_hints", [])
    hints_used = session_data.get("hints_used", 0)

    # Hint request
    if any(k in msg_lower for k in ["hint", "stuck", "clue", "help"]):
        if hints_used < len(hints):
            hint_tier = hints_used + 1
            hint_content = hints[hints_used]
            return f"[Hint Level {hint_tier}/3]: {hint_content}"
        else:
            return "You've unlocked all hints for this problem! Try writing out a simple example on paper and trace your variable states."

    # Time complexity question
    if any(k in msg_lower for k in ["complexity", "big o", "time complexity", "space complexity"]):
        optimal = session_data.get("optimal_complexity", "O(N) Time, O(1) Space")
        return f"For this problem, interviewers typically look for an optimal solution achieving: {optimal}. What is the current complexity of your proposed approach?"

    # Approach clarification
    if any(k in msg_lower for k in ["hash map", "dictionary", "hashmap", "set"]):
        return "Using a Hash Map/Set is a very promising direction for fast lookups. How does that trade off space complexity for speed?"

    if any(k in msg_lower for k in ["two pointer", "pointers", "pointer"]):
        return "Two pointers is an excellent technique here! Make sure to define your boundary conditions carefully (e.g. `while left < right`)."

    if any(k in msg_lower for k in ["dp", "dynamic programming", "memoization"]):
        return "Dynamic programming sounds applicable! What would be your state definition `dp[i]` and what are your base cases?"

    if any(k in msg_lower for k in ["negative", "empty", "zero", "duplicate", "null", "edge case"]):
        return "Great clarifying question! You should always handle empty inputs, single elements, and negative values gracefully as edge cases."

    if any(k in msg_lower for k in ["done", "finished", "ready", "submitted", "test"]):
        return "Awesome! Click 'Run Sample Tests' to verify against public cases, or click 'Submit Solution' to test against all hidden edge cases and receive your final evaluation score."

    # Default supportive response
    return (
        f"That's a reasonable thought process for '{q_title}'. "
        f"Walk me through your expected time complexity, and feel free to start typing your starter code in the editor when you're ready!"
    )


def chat_with_interviewer(candidate_message, session_data, chat_history=None, current_code=""):
    """
    Conversational interaction with Gemini API configured as an expert technical interviewer.
    Falls back cleanly to rule-based engine if offline.
    """
    client = get_gemini_client()
    if not client:
        return rule_based_interviewer_response(candidate_message, session_data, current_code)

    q_title = session_data.get("question_title", "")
    q_desc = session_data.get("question_description", "")
    optimal = session_data.get("optimal_complexity", "")
    target_comp = session_data.get("target_company", "Google")
    cand_name = session_data.get("candidate_name", "Candidate")

    system_instruction = (
        f"You are a friendly, rigorous Senior Software Engineer conducting a live technical coding interview at {target_comp}. "
        f"The candidate is {cand_name}. The problem being solved is '{q_title}'.\n"
        f"Problem Description:\n{q_desc}\n\n"
        f"Optimal Solution Target: {optimal}\n\n"
        f"RULES OF CONDUCT:\n"
        f"1. Be conversational, supportive, yet technically demanding like a real FAANG interviewer.\n"
        f"2. Keep responses brief and focused (2-4 sentences max).\n"
        f"3. NEVER write out the full solution code for the candidate.\n"
        f"4. If the candidate asks for a hint, provide a subtle nudge or question to steer them in the right direction.\n"
        f"5. Encourage them to analyze edge cases and discuss time/space complexity before coding."
    )

    history_context = ""
    if chat_history:
        for m in chat_history[-6:]:
            history_context += f"{m.get('sender', 'User')}: {m.get('message', '')}\n"

    code_context = f"\nCandidate's Current Editor Code:\n```python\n{current_code}\n```" if current_code else ""

    prompt = f"""
{history_context}
{code_context}
Candidate says: "{candidate_message}"

Interviewer response:
"""

    try:
        config = types.GenerateContentConfig(
            temperature=0.4,
            max_output_tokens=300,
            system_instruction=system_instruction
        )
        response = client.models.generate_content(
            model=Config.GEMINI_MODEL,
            contents=prompt,
            config=config
        )
        if response and response.text:
            return response.text.strip()
    except Exception as e:
        print(f"Gemini Chat Error: {e}")

    return rule_based_interviewer_response(candidate_message, session_data, current_code)


def get_progressive_hint(session_data, hint_index=0):
    """Return progressive hint (Level 1, 2, or 3)."""
    hints = session_data.get("question_hints", [])
    if hint_index < len(hints):
        return {
            "tier": hint_index + 1,
            "max_tiers": len(hints),
            "hint": hints[hint_index]
        }
    return {
        "tier": len(hints),
        "max_tiers": len(hints),
        "hint": "All hints have been used. Consider re-reading the problem constraints carefully."
    }
