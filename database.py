import sqlite3
import json
from config import Config


def get_db_connection():
    """Establish and return SQLite database connection."""
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


DEFAULT_QUESTIONS = [
    {
        "title": "Two Sum",
        "difficulty": "Easy",
        "category": "Arrays & Hashing",
        "company": "Amazon, Google, Meta",
        "description": "Given an array of integers `nums` and an integer `target`, return the indices of the two numbers such that they add up to `target`.\n\nYou may assume that each input would have exactly one solution, and you may not use the same element twice. You can return the answer in any order.",
        "examples": [
            {"input": "nums = [2,7,11,15], target = 9", "output": "[0,1]", "explanation": "Because nums[0] + nums[1] == 9, we return [0, 1]."},
            {"input": "nums = [3,2,4], target = 6", "output": "[1,2]", "explanation": "nums[1] + nums[2] == 6."}
        ],
        "test_cases": [
            {"input": {"nums": [2, 7, 11, 15], "target": 9}, "expected": [0, 1]},
            {"input": {"nums": [3, 2, 4], "target": 6}, "expected": [1, 2]},
            {"input": {"nums": [3, 3], "target": 6}, "expected": [0, 1]},
            {"input": {"nums": [-1, -2, -3, -4, -5], "target": -8}, "expected": [2, 4]},
            {"input": {"nums": [1, 5, 7, 12, 19], "target": 20}, "expected": [0, 4]}
        ],
        "hints": [
            "A brute-force solution checks every pair with two nested loops in O(N^2) time. Can we do it in a single pass?",
            "As we iterate through the list, what value are we looking for to reach target? (complement = target - num)",
            "Use a Hash Map (dictionary) to store numbers we have already seen and their indices: `seen[num] = i`."
        ],
        "optimal_complexity": "Time: O(N), Space: O(N)",
        "starter_code": "def two_sum(nums, target):\n    # Write your solution here\n    pass\n",
        "solution_code": "def two_sum(nums, target):\n    seen = {}\n    for i, num in enumerate(nums):\n        diff = target - num\n        if diff in seen:\n            return [seen[diff], i]\n        seen[num] = i\n    return []\n"
    },
    {
        "title": "Valid Palindrome",
        "difficulty": "Easy",
        "category": "Two Pointers",
        "company": "Microsoft, Apple",
        "description": "A phrase is a palindrome if, after converting all uppercase letters into lowercase letters and removing all non-alphanumeric characters, it reads the same forward and backward. Alphanumeric characters include letters and numbers.\n\nGiven a string `s`, return `true` if it is a palindrome, or `false` otherwise.",
        "examples": [
            {"input": "s = \"A man, a plan, a canal: Panama\"", "output": "true", "explanation": "\"amanaplanacanalpanama\" is a palindrome."},
            {"input": "s = \"race a car\"", "output": "false", "explanation": "\"raceacar\" is not a palindrome."}
        ],
        "test_cases": [
            {"input": {"s": "A man, a plan, a canal: Panama"}, "expected": True},
            {"input": {"s": "race a car"}, "expected": False},
            {"input": {"s": " "}, "expected": True},
            {"input": {"s": "0P"}, "expected": False},
            {"input": {"s": "ab_a"}, "expected": True}
        ],
        "hints": [
            "First consider cleaning the string or checking alphanumeric characters on the fly.",
            "Can we use two pointers: one starting from the beginning and one from the end?",
            "Move the left pointer forward if not alphanumeric, right pointer backward if not alphanumeric, and compare `s[left].lower() == s[right].lower()`."
        ],
        "optimal_complexity": "Time: O(N), Space: O(1)",
        "starter_code": "def is_palindrome(s):\n    # Write your solution here\n    pass\n",
        "solution_code": "def is_palindrome(s):\n    left, right = 0, len(s) - 1\n    while left < right:\n        while left < right and not s[left].isalnum():\n            left += 1\n        while left < right and not s[right].isalnum():\n            right -= 1\n        if s[left].lower() != s[right].lower():\n            return False\n        left += 1\n        right -= 1\n    return True\n"
    },
    {
        "title": "Longest Substring Without Repeating Characters",
        "difficulty": "Medium",
        "category": "Sliding Window",
        "company": "Amazon, Meta, Google",
        "description": "Given a string `s`, find the length of the longest substring without repeating characters.",
        "examples": [
            {"input": "s = \"abcabcbb\"", "output": "3", "explanation": "The answer is \"abc\", with the length of 3."},
            {"input": "s = \"bbbbb\"", "output": "1", "explanation": "The answer is \"b\", with the length of 1."}
        ],
        "test_cases": [
            {"input": {"s": "abcabcbb"}, "expected": 3},
            {"input": {"s": "bbbbb"}, "expected": 1},
            {"input": {"s": "pwwkew"}, "expected": 3},
            {"input": {"s": ""}, "expected": 0},
            {"input": {"s": "au"}, "expected": 2},
            {"input": {"s": "dvdf"}, "expected": 3}
        ],
        "hints": [
            "Think about a sliding window with two pointers `left` and `right`.",
            "Maintain a set or dictionary of characters currently in your window.",
            "If `s[right]` is already in the window, shrink the window by moving `left` forward until the duplicate is removed."
        ],
        "optimal_complexity": "Time: O(N), Space: O(min(N, M)) where M is character set size",
        "starter_code": "def length_of_longest_substring(s):\n    # Write your solution here\n    pass\n",
        "solution_code": "def length_of_longest_substring(s):\n    char_set = set()\n    left = 0\n    max_len = 0\n    for right in range(len(s)):\n        while s[right] in char_set:\n            char_set.remove(s[left])\n            left += 1\n        char_set.add(s[right])\n        max_len = max(max_len, right - left + 1)\n    return max_len\n"
    },
    {
        "title": "Container With Most Water",
        "difficulty": "Medium",
        "category": "Two Pointers",
        "company": "Google, Amazon",
        "description": "You are given an integer array `height` of length `n`. There are `n` vertical lines drawn such that the two endpoints of the `i-th` line are `(i, 0)` and `(i, height[i])`.\n\nFind two lines that together with the x-axis form a container, such that the container contains the most water. Return the maximum amount of water a container can store.",
        "examples": [
            {"input": "height = [1,8,6,2,5,4,8,3,7]", "output": "49", "explanation": "The vertical lines are represented by array [1,8,6,2,5,4,8,3,7]. In this case, max area is 49."},
            {"input": "height = [1,1]", "output": "1", "explanation": "Max area is 1."}
        ],
        "test_cases": [
            {"input": {"height": [1, 8, 6, 2, 5, 4, 8, 3, 7]}, "expected": 49},
            {"input": {"height": [1, 1]}, "expected": 1},
            {"input": {"height": [4, 3, 2, 1, 4]}, "expected": 16},
            {"input": {"height": [1, 2, 1]}, "expected": 2}
        ],
        "hints": [
            "The area formed between lines at `i` and `j` is `(j - i) * min(height[i], height[j])`.",
            "Start with the widest container: two pointers at the extreme ends `left = 0` and `right = len(height) - 1`.",
            "Which pointer should you move? Moving the taller line will never increase the area, so always advance the shorter line."
        ],
        "optimal_complexity": "Time: O(N), Space: O(1)",
        "starter_code": "def max_area(height):\n    # Write your solution here\n    pass\n",
        "solution_code": "def max_area(height):\n    left, right = 0, len(height) - 1\n    max_water = 0\n    while left < right:\n        current_water = (right - left) * min(height[left], height[right])\n        max_water = max(max_water, current_water)\n        if height[left] < height[right]:\n            left += 1\n        else:\n            right -= 1\n    return max_water\n"
    },
    {
        "title": "Coin Change",
        "difficulty": "Medium",
        "category": "Dynamic Programming",
        "company": "Amazon, Microsoft, Bloomberg",
        "description": "You are given an integer array `coins` representing coins of different denominations and an integer `amount` representing a total amount of money.\n\nReturn the fewest number of coins that you need to make up that amount. If that amount of money cannot be made up by any combination of the coins, return `-1`.\n\nYou may assume that you have an infinite number of each kind of coin.",
        "examples": [
            {"input": "coins = [1,2,5], amount = 11", "output": "3", "explanation": "11 = 5 + 5 + 1"},
            {"input": "coins = [2], amount = 3", "output": "-1", "explanation": "Amount 3 cannot be formed with coin 2."}
        ],
        "test_cases": [
            {"input": {"coins": [1, 2, 5], "amount": 11}, "expected": 3},
            {"input": {"coins": [2], "amount": 3}, "expected": -1},
            {"input": {"coins": [1], "amount": 0}, "expected": 0},
            {"input": {"coins": [2, 5, 10, 1], "amount": 27}, "expected": 4}
        ],
        "hints": [
            "Greedy approach (always picking the biggest coin) fails for coins like [1, 3, 4] with amount 6. DP is required.",
            "Define `dp[i]` as the minimum coins needed to make amount `i`. Base case `dp[0] = 0`.",
            "For each amount `i` from 1 to `amount` and each `coin` in `coins`: `dp[i] = min(dp[i], 1 + dp[i - coin])` if `i >= coin`."
        ],
        "optimal_complexity": "Time: O(amount * len(coins)), Space: O(amount)",
        "starter_code": "def coin_change(coins, amount):\n    # Write your solution here\n    pass\n",
        "solution_code": "def coin_change(coins, amount):\n    dp = [float('inf')] * (amount + 1)\n    dp[0] = 0\n    for a in range(1, amount + 1):\n        for c in coins:\n            if a - c >= 0:\n                dp[a] = min(dp[a], 1 + dp[a - c])\n    return dp[amount] if dp[amount] != float('inf') else -1\n"
    }
]


def init_db():
    """Create database tables and seed initial technical questions."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Questions Bank
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        difficulty TEXT NOT NULL,
        category TEXT NOT NULL,
        company TEXT,
        description TEXT NOT NULL,
        examples TEXT NOT NULL,
        test_cases TEXT NOT NULL,
        hints TEXT NOT NULL,
        optimal_complexity TEXT NOT NULL,
        starter_code TEXT NOT NULL,
        solution_code TEXT NOT NULL
    );
    """)

    # Interview Sessions
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        candidate_name TEXT NOT NULL,
        question_id INTEGER NOT NULL,
        target_role TEXT,
        target_company TEXT,
        difficulty TEXT,
        status TEXT DEFAULT 'in_progress',
        duration_seconds INTEGER DEFAULT 0,
        hints_used INTEGER DEFAULT 0,
        submitted_code TEXT,
        started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP,
        FOREIGN KEY (question_id) REFERENCES questions (id)
    );
    """)

    # Chat Messages (Conversation history with AI interviewer)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER NOT NULL,
        sender TEXT NOT NULL,
        message TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE
    );
    """)

    # Candidate Performance Evaluations
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS evaluations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER NOT NULL UNIQUE,
        overall_score INTEGER NOT NULL,
        recommendation TEXT NOT NULL,
        correctness_score INTEGER NOT NULL,
        complexity_score INTEGER NOT NULL,
        quality_score INTEGER NOT NULL,
        communication_score INTEGER NOT NULL,
        test_results TEXT,
        feedback TEXT,
        time_complexity TEXT,
        space_complexity TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE
    );
    """)

    conn.commit()

    # Check if questions exist; if empty, seed default questions
    cursor.execute("SELECT COUNT(*) FROM questions")
    if cursor.fetchone()[0] == 0:
        for q in DEFAULT_QUESTIONS:
            cursor.execute("""
                INSERT INTO questions (
                    title, difficulty, category, company, description,
                    examples, test_cases, hints, optimal_complexity, starter_code, solution_code
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                q["title"],
                q["difficulty"],
                q["category"],
                q["company"],
                q["description"],
                json.dumps(q["examples"]),
                json.dumps(q["test_cases"]),
                json.dumps(q["hints"]),
                q["optimal_complexity"],
                q["starter_code"],
                q["solution_code"]
            ))
        conn.commit()

    conn.close()


def get_all_questions():
    """Retrieve all coding questions from question bank."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM questions ORDER BY difficulty, id")
    rows = cursor.fetchall()
    conn.close()

    questions = []
    for row in rows:
        item = dict(row)
        item["examples"] = json.loads(item["examples"])
        item["test_cases"] = json.loads(item["test_cases"])
        item["hints"] = json.loads(item["hints"])
        questions.append(item)
    return questions


def get_question(question_id):
    """Retrieve single question by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM questions WHERE id = ?", (question_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None
    item = dict(row)
    item["examples"] = json.loads(item["examples"])
    item["test_cases"] = json.loads(item["test_cases"])
    item["hints"] = json.loads(item["hints"])
    return item


def create_session(candidate_name, question_id, target_role="Software Engineer", target_company="Google"):
    """Initialize a new interview session."""
    question = get_question(question_id)
    difficulty = question["difficulty"] if question else "Medium"

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO sessions (candidate_name, question_id, target_role, target_company, difficulty, submitted_code)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (candidate_name, question_id, target_role, target_company, difficulty, question["starter_code"]))

    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return session_id


def get_session(session_id):
    """Fetch session with question details."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.*, q.title as question_title, q.description as question_description,
               q.examples as question_examples, q.test_cases as question_test_cases,
               q.hints as question_hints, q.optimal_complexity, q.starter_code, q.solution_code
        FROM sessions s
        JOIN questions q ON s.question_id = q.id
        WHERE s.id = ?
    """, (session_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None
    item = dict(row)
    item["question_examples"] = json.loads(item["question_examples"])
    item["question_test_cases"] = json.loads(item["question_test_cases"])
    item["question_hints"] = json.loads(item["question_hints"])
    return item


def add_chat_message(session_id, sender, message):
    """Log an interviewer or candidate message."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO chat_messages (session_id, sender, message)
        VALUES (?, ?, ?)
    """, (session_id, sender, message))
    conn.commit()
    conn.close()


def get_chat_history(session_id):
    """Retrieve full chronological chat transcript."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM chat_messages WHERE session_id = ? ORDER BY id ASC", (session_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def save_evaluation(session_id, overall_score, recommendation, correctness_score,
                    complexity_score, quality_score, communication_score,
                    test_results, feedback, time_complexity="O(N)", space_complexity="O(1)"):
    """Persist final interview scorecard evaluation."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO evaluations (
            session_id, overall_score, recommendation, correctness_score,
            complexity_score, quality_score, communication_score,
            test_results, feedback, time_complexity, space_complexity
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        session_id, overall_score, recommendation, correctness_score,
        complexity_score, quality_score, communication_score,
        json.dumps(test_results), json.dumps(feedback),
        time_complexity, space_complexity
    ))

    # Mark session as completed
    cursor.execute("""
        UPDATE sessions
        SET status = 'completed', completed_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (session_id,))

    conn.commit()
    conn.close()


def get_evaluation(session_id):
    """Fetch completed evaluation record."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT e.*, s.candidate_name, s.target_role, s.target_company, s.started_at, s.completed_at,
               s.submitted_code, q.title as question_title, q.difficulty as question_difficulty,
               q.optimal_complexity, q.solution_code
        FROM evaluations e
        JOIN sessions s ON e.session_id = s.id
        JOIN questions q ON s.question_id = q.id
        WHERE e.session_id = ?
    """, (session_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None
    item = dict(row)
    item["test_results"] = json.loads(item["test_results"])
    item["feedback"] = json.loads(item["feedback"])
    return item


def get_all_sessions(limit=50):
    """Fetch recent interview sessions for dashboard/history."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.*, q.title as question_title, e.overall_score, e.recommendation
        FROM sessions s
        JOIN questions q ON s.question_id = q.id
        LEFT JOIN evaluations e ON s.id = e.session_id
        ORDER BY s.started_at DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_dashboard_metrics():
    """Aggregate interview statistics."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM sessions")
    total_interviews = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*), AVG(overall_score) FROM evaluations")
    row = cursor.fetchone()
    completed_interviews = row[0] or 0
    avg_score = round(row[1], 1) if row[1] is not None else 0

    cursor.execute("SELECT COUNT(*) FROM questions")
    total_questions = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM evaluations WHERE recommendation IN ('Strong Hire', 'Hire')")
    hire_recommendations = cursor.fetchone()[0]

    conn.close()
    return {
        "total_interviews": total_interviews,
        "completed_interviews": completed_interviews,
        "avg_score": avg_score,
        "total_questions": total_questions,
        "hire_recommendations": hire_recommendations
    }
