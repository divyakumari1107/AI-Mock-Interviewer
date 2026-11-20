import time
import sys
import traceback
import multiprocessing


def _worker_execute(code_str, func_name, kwargs, result_queue):
    """Worker process function to safely execute code in an isolated scope."""
    try:
        # Create dedicated local namespace
        local_scope = {}
        # Pre-import common algorithmic libraries
        exec("import math\nimport collections\nimport heapq\nfrom typing import List, Dict, Optional, Tuple", local_scope)

        # Execute candidate's function definition
        exec(code_str, local_scope)

        if func_name not in local_scope:
            result_queue.put({"success": False, "error": f"Function '{func_name}' not defined in submitted code."})
            return

        func = local_scope[func_name]
        start_time = time.perf_counter()
        output = func(**kwargs)
        duration_ms = (time.perf_counter() - start_time) * 1000

        result_queue.put({
            "success": True,
            "output": output,
            "duration_ms": round(duration_ms, 2)
        })
    except Exception as e:
        result_queue.put({
            "success": False,
            "error": f"{type(e).__name__}: {str(e)}"
        })


def execute_test_case(code_str, func_name, input_kwargs, expected_output, timeout_sec=2.5):
    """
    Execute a single test case with hard timeout protection.
    """
    result_queue = multiprocessing.Queue()
    process = multiprocessing.Process(
        target=_worker_execute,
        args=(code_str, func_name, input_kwargs, result_queue)
    )

    process.start()
    process.join(timeout=timeout_sec)

    if process.is_alive():
        process.terminate()
        process.join()
        return {
            "passed": False,
            "input": input_kwargs,
            "expected": expected_output,
            "actual": None,
            "error": "Time Limit Exceeded (TLE): Execution exceeded 2.5 seconds.",
            "duration_ms": timeout_sec * 1000
        }

    if not result_queue.empty():
        res = result_queue.get()
        if not res["success"]:
            return {
                "passed": False,
                "input": input_kwargs,
                "expected": expected_output,
                "actual": None,
                "error": res["error"],
                "duration_ms": 0
            }

        actual_output = res["output"]
        # Comparison with handling for lists, sets, and booleans
        passed = (actual_output == expected_output)

        return {
            "passed": passed,
            "input": input_kwargs,
            "expected": expected_output,
            "actual": actual_output,
            "error": None if passed else f"Expected {expected_output}, got {actual_output}",
            "duration_ms": res.get("duration_ms", 0)
        }

    return {
        "passed": False,
        "input": input_kwargs,
        "expected": expected_output,
        "actual": None,
        "error": "Execution terminated unexpectedly without output.",
        "duration_ms": 0
    }


def find_function_name(code_str):
    """Extract primary function name from code string."""
    import re
    match = re.search(r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', code_str)
    return match.group(1) if match else None


def run_all_test_cases(code_str, test_cases, custom_func_name=None):
    """
    Run full suite of test cases against candidate's code.
    Returns structured results and pass percentage.
    """
    func_name = custom_func_name or find_function_name(code_str)
    if not func_name:
        return {
            "total": len(test_cases),
            "passed_count": 0,
            "pass_percentage": 0,
            "all_passed": False,
            "details": [],
            "error": "No Python function definition ('def ...') found in submitted code."
        }

    results = []
    passed_count = 0

    for idx, tc in enumerate(test_cases):
        input_args = tc.get("input", {})
        expected = tc.get("expected")

        case_res = execute_test_case(code_str, func_name, input_args, expected)
        case_res["case_number"] = idx + 1
        if case_res["passed"]:
            passed_count += 1
        results.append(case_res)

    total = len(test_cases)
    pass_pct = round((passed_count / total) * 100) if total > 0 else 0

    return {
        "total": total,
        "passed_count": passed_count,
        "pass_percentage": pass_pct,
        "all_passed": (passed_count == total),
        "details": results,
        "function_name": func_name,
        "error": None
    }
