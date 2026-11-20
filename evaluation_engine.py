import ast
import re
from config import Config
from interviewer_ai import get_gemini_client

# Try importing Gemini types
try:
    from google.genai import types
except ImportError:
    pass


def analyze_code_structure(code_str):
    """
    Perform Abstract Syntax Tree (AST) analysis on submitted code
    to evaluate modularity, naming, and complexity.
    """
    quality_score = 70  # Baseline
    notes = []

    try:
        tree = ast.parse(code_str)

        # Check for function definitions
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        if functions:
            quality_score += 10
            notes.append("Properly structured into Python function definition.")

        # Check for loop nesting (detect potential O(N^2) or O(N^3))
        nested_loops = 0
        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.While)):
                for child in ast.walk(node):
                    if child is not node and isinstance(child, (ast.For, ast.While)):
                        nested_loops += 1
        
        if nested_loops > 0:
            notes.append(f"Detected {nested_loops} nested loop(s); verify if quadratic O(N^2) time is optimal.")
        else:
            quality_score += 10
            notes.append("Clean linear control flow without nested loops.")

        # Check variable naming
        variables = [node.id for node in ast.walk(tree) if isinstance(node, ast.Name)]
        short_vars = [v for v in variables if len(v) == 1 and v not in ['i', 'j', 'k', 's', 'c', 'n']]
        if len(short_vars) > 4:
            quality_score -= 10
            notes.append("Consider using more descriptive variable names for readability.")
        else:
            quality_score += 10
            notes.append("Readable and descriptive variable names used.")

    except SyntaxError as e:
        return 20, [f"Syntax Error in code: {str(e)}"], "Undetermined", "Undetermined"

    quality_score = max(20, min(100, quality_score))
    return quality_score, notes


def evaluate_with_gemini(code_str, question_title, optimal_complexity, test_results):
    """
    Use Gemini AI to analyze Big-O complexity and generate senior interviewer feedback.
    """
    client = get_gemini_client()
    if not client:
        return None

    prompt = f"""
You are a Staff Software Engineer at Google conducting an interview evaluation.
Problem: {question_title}
Optimal Complexity: {optimal_complexity}

Candidate Code:
```python
{code_str}
```

Test Cases Result: {test_results.get('passed_count')}/{test_results.get('total')} Passed.

Analyze the candidate's code and reply in valid JSON format:
{{
  "time_complexity": "e.g. O(N)",
  "space_complexity": "e.g. O(1)",
  "complexity_score": 85,
  "code_quality_score": 80,
  "strengths": ["...", "..."],
  "weaknesses": ["...", "..."],
  "hiring_verdict": "Strong Hire / Hire / Lean No-Hire / No-Hire",
  "summary_feedback": "Detailed paragraph explaining performance and how to improve."
}}
"""
    try:
        config = types.GenerateContentConfig(
            temperature=0.2,
            max_output_tokens=700,
            response_mime_type="application/json"
        )
        response = client.models.generate_content(
            model=Config.GEMINI_MODEL,
            contents=prompt,
            config=config
        )
        if response and response.text:
            import json
            return json.loads(response.text.strip())
    except Exception as e:
        print(f"Gemini Evaluation Error: {e}")
    return None


def evaluate_interview_session(session_data, test_results, submitted_code, chat_history=None):
    """
    Complete interview performance evaluation synthesizing:
    - Correctness (40%)
    - Complexity (25%)
    - Code Quality (20%)
    - Communication & Hint Usage (15%)
    """
    # 1. Correctness Score (40% weight)
    correctness_score = test_results.get("pass_percentage", 0)

    # 2. Code Quality Score (20% weight)
    quality_score, quality_notes = analyze_code_structure(submitted_code)

    # 3. Communication & Hint Deduction (15% weight)
    hints_used = session_data.get("hints_used", 0)
    hint_penalty = min(20, hints_used * 7)
    
    comm_baseline = 85
    msg_count = len(chat_history) if chat_history else 0
    if msg_count >= 4:
        comm_baseline = 95
    elif msg_count <= 1:
        comm_baseline = 65

    communication_score = max(20, min(100, comm_baseline - hint_penalty))

    # 4. Complexity & Feedback
    q_title = session_data.get("question_title", "")
    optimal_complexity = session_data.get("optimal_complexity", "O(N) Time, O(1) Space")

    # Try Gemini AI evaluation first
    ai_eval = evaluate_with_gemini(submitted_code, q_title, optimal_complexity, test_results)

    if ai_eval:
        time_comp = ai_eval.get("time_complexity", "O(N)")
        space_comp = ai_eval.get("space_complexity", "O(1)")
        complexity_score = ai_eval.get("complexity_score", 75)
        strengths = ai_eval.get("strengths", [])
        weaknesses = ai_eval.get("weaknesses", [])
        summary = ai_eval.get("summary_feedback", "")
    else:
        # Rule-based fallback complexity derivation
        if "for " in submitted_code and "for " in submitted_code.split("for ", 1)[1]:
            time_comp = "O(N^2)"
            space_comp = "O(1)"
            complexity_score = 60
        else:
            time_comp = "O(N)"
            space_comp = "O(N)" if "{" in submitted_code or "set(" in submitted_code else "O(1)"
            complexity_score = 90

        strengths = [
            f"Successfully executed against {test_results.get('passed_count')}/{test_results.get('total')} test scenarios.",
            "Structured implementation using clean modular functions."
        ]
        weaknesses = []
        if correctness_score < 100:
            weaknesses.append("Failed some edge cases; test for boundary conditions like empty inputs.")
        if hints_used > 0:
            weaknesses.append(f"Requested {hints_used} hint(s) during problem solving.")

        summary = (
            f"Candidate demonstrated functional problem-solving skills for '{q_title}'. "
            f"The implementation achieved {correctness_score}% test case coverage with estimated {time_comp} time complexity."
        )

    # Calculate Overall Weighted Score (0-100)
    overall_score = round(
        (correctness_score * 0.40) +
        (complexity_score * 0.25) +
        (quality_score * 0.20) +
        (communication_score * 0.15)
    )
    overall_score = max(10, min(99, overall_score))

    # Hiring Recommendation Verdict
    if overall_score >= 85 and correctness_score == 100:
        recommendation = "Strong Hire"
        badge_color = "success"
    elif overall_score >= 70 and correctness_score >= 80:
        recommendation = "Hire"
        badge_color = "primary"
    elif overall_score >= 50:
        recommendation = "Lean No-Hire"
        badge_color = "warning"
    else:
        recommendation = "No-Hire"
        badge_color = "danger"

    feedback_payload = {
        "summary": summary,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "quality_notes": quality_notes,
        "hints_used": hints_used,
        "badge_color": badge_color,
        "optimal_complexity": optimal_complexity
    }

    return {
        "overall_score": overall_score,
        "recommendation": recommendation,
        "badge_color": badge_color,
        "correctness_score": correctness_score,
        "complexity_score": complexity_score,
        "quality_score": quality_score,
        "communication_score": communication_score,
        "time_complexity": time_comp,
        "space_complexity": space_comp,
        "feedback": feedback_payload
    }
