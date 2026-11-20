import os
import sys
import unittest

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from config import Config
from database import init_db, get_all_questions, get_question, create_session, get_session, add_chat_message, get_chat_history, get_evaluation
from code_executor import run_all_test_cases, execute_test_case
from interviewer_ai import get_welcome_message, chat_with_interviewer, get_progressive_hint
from evaluation_engine import evaluate_interview_session
from scorecard_pdf import generate_scorecard_pdf
from app import app


class TestAIMockInterviewer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = app.test_client()

    def test_01_question_bank(self):
        questions = get_all_questions()
        self.assertTrue(len(questions) >= 5, "Database must have seeded questions")
        q1 = get_question(1)
        self.assertIsNotNone(q1)
        self.assertEqual(q1["title"], "Two Sum")
        self.assertTrue(len(q1["test_cases"]) >= 3)
        print("✓ Question Bank seeding and queries verified.")

    def test_02_code_executor_sandbox(self):
        # 1. Correct two sum code
        code_correct = """
def two_sum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        diff = target - num
        if diff in seen:
            return [seen[diff], i]
        seen[num] = i
    return []
"""
        q1 = get_question(1)
        res = run_all_test_cases(code_correct, q1["test_cases"])
        self.assertTrue(res["all_passed"], "Correct code must pass all test cases")
        self.assertEqual(res["pass_percentage"], 100)
        print(f"✓ Code execution: Correct code passed {res['passed_count']}/{res['total']} test cases.")

        # 2. Buggy code
        code_buggy = """
def two_sum(nums, target):
    return [0, 0]
"""
        res_buggy = run_all_test_cases(code_buggy, q1["test_cases"])
        self.assertFalse(res_buggy["all_passed"], "Buggy code should fail")

        # 3. Timeout / Infinite loop detection
        code_infinite = """
def two_sum(nums, target):
    while True:
        pass
"""
        res_timeout = execute_test_case(code_infinite, "two_sum", {"nums": [2, 7], "target": 9}, [0, 1], timeout_sec=1.5)
        self.assertFalse(res_timeout["passed"])
        self.assertIn("Time Limit Exceeded", res_timeout["error"])
        print("✓ Sandbox security: Infinite loop caught and terminated within timeout limit.")

    def test_03_session_and_chat(self):
        session_id = create_session("Alex Morgan", 1, "Software Engineer", "Google")
        self.assertTrue(session_id > 0)
        
        session = get_session(session_id)
        self.assertEqual(session["candidate_name"], "Alex Morgan")

        # Test Welcome message
        welcome = get_welcome_message("Alex Morgan", session["question_title"], "Google")
        self.assertIn("Alex Morgan", welcome)
        add_chat_message(session_id, "AI Interviewer", welcome)

        # Test Candidate message
        add_chat_message(session_id, "Candidate", "Can the array contain negative numbers?")
        history = get_chat_history(session_id)
        self.assertEqual(len(history), 2)

        # Test Progressive Hints
        h1 = get_progressive_hint(session, 0)
        self.assertEqual(h1["tier"], 1)
        self.assertTrue(len(h1["hint"]) > 10)
        print("✓ Session lifecycle, conversation history, and 3-tier hints verified.")

    def test_04_evaluation_engine(self):
        session = get_session(1)
        q1 = get_question(1)
        code_optimal = q1["solution_code"]
        test_results = run_all_test_cases(code_optimal, q1["test_cases"])

        evaluation = evaluate_interview_session(
            session_data=session,
            test_results=test_results,
            submitted_code=code_optimal,
            chat_history=[{"sender": "Candidate", "message": "I will use a Hash Map."}]
        )

        self.assertIn("overall_score", evaluation)
        self.assertTrue(0 <= evaluation["overall_score"] <= 100)
        self.assertIn("recommendation", evaluation)
        self.assertIn(evaluation["recommendation"], ["Strong Hire", "Hire", "Lean No-Hire", "No-Hire"])
        print(f"✓ Evaluation Engine: Score {evaluation['overall_score']}/100, Verdict: {evaluation['recommendation']}")

    def test_05_scorecard_pdf_generation(self):
        sample_eval = {
            "session_id": 1,
            "candidate_name": "Alex Morgan",
            "target_role": "Backend SDE",
            "target_company": "Google",
            "question_title": "Two Sum",
            "overall_score": 92,
            "recommendation": "Strong Hire",
            "correctness_score": 100,
            "complexity_score": 95,
            "quality_score": 85,
            "communication_score": 90,
            "time_complexity": "O(N)",
            "space_complexity": "O(N)",
            "solution_code": "def two_sum(nums, target):\n    seen = {}\n    for i, num in enumerate(nums):\n        if target - num in seen:\n            return [seen[target - num], i]\n        seen[num] = i\n",
            "feedback": {
                "summary": "Candidate demonstrated outstanding algorithmic reasoning.",
                "strengths": ["Clean single-pass hash map implementation", "Optimal O(N) complexity"],
                "weaknesses": ["Minor: could add explicit docstrings"],
                "hints_used": 0
            }
        }

        pdf_path, _ = generate_scorecard_pdf(sample_eval, output_filename="test_scorecard.pdf")
        self.assertTrue(os.path.exists(pdf_path))
        with open(pdf_path, "rb") as f:
            header = f.read(5)
            self.assertEqual(header, b"%PDF-")
        print("✓ ReportLab Scorecard PDF generated and verified successfully.")

    def test_06_flask_routes(self):
        # 1. Landing
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)

        # 2. Dashboard
        resp = self.client.get("/dashboard")
        self.assertEqual(resp.status_code, 200)

        # 3. Setup GET & POST
        resp = self.client.get("/setup")
        self.assertEqual(resp.status_code, 200)

        resp = self.client.post("/setup", data={
            "candidate_name": "Test User",
            "target_company": "Amazon",
            "target_role": "SDE I",
            "question_id": 1
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Interview:", resp.data)

        # 4. API Chat
        resp = self.client.post("/api/chat", json={
            "session_id": 1,
            "message": "Hello, I am ready to begin."
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data["success"])

        # 5. API Hint
        resp = self.client.post("/api/hint", json={"session_id": 1})
        self.assertEqual(resp.status_code, 200)

        # 6. API Run Code
        q1 = get_question(1)
        resp = self.client.post("/api/run-code", json={
            "session_id": 1,
            "code": q1["starter_code"]
        })
        self.assertEqual(resp.status_code, 200)

        # 7. API Submit Code
        resp = self.client.post("/api/submit-code", json={
            "session_id": 1,
            "code": q1["solution_code"],
            "duration_seconds": 180
        })
        self.assertEqual(resp.status_code, 200)
        submit_data = resp.get_json()
        self.assertTrue(submit_data["success"])

        # 8. Scorecard & PDF download
        resp = self.client.get("/scorecard/1")
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get("/download-pdf/1")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.headers["Content-Type"], "application/pdf")

        # 9. Questions Bank
        resp = self.client.get("/questions")
        self.assertEqual(resp.status_code, 200)

        # 10. History
        resp = self.client.get("/history")
        self.assertEqual(resp.status_code, 200)

        # 11. About & Viva Guide
        resp = self.client.get("/about")
        self.assertEqual(resp.status_code, 200)

        print("✓ All 11 Flask routes & API endpoints tested with HTTP 200!")


if __name__ == "__main__":
    unittest.main()
