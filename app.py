import os
import json
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file

from config import Config
from database import (
    init_db, get_all_questions, get_question, create_session, get_session,
    add_chat_message, get_chat_history, save_evaluation, get_evaluation,
    get_all_sessions, get_dashboard_metrics, get_db_connection
)
from code_executor import run_all_test_cases
from interviewer_ai import get_welcome_message, chat_with_interviewer, get_progressive_hint
from evaluation_engine import evaluate_interview_session
from scorecard_pdf import generate_scorecard_pdf


app = Flask(__name__)
app.config.from_object(Config)

# Initialize database schema on startup
with app.app_context():
    init_db()


@app.context_processor
def inject_global_data():
    """Inject configuration flags and global variables into all Jinja2 templates."""
    has_api_key = bool(Config.GEMINI_API_KEY)
    ai_status = "Gemini AI Interviewer Active" if has_api_key else "Intelligent Heuristic Interviewer"
    return {
        "app_name": Config.APP_NAME,
        "app_version": Config.VERSION,
        "gemini_active": has_api_key,
        "ai_status_label": ai_status,
        "port": Config.PORT
    }


# -------------------------------------------------------------
# 1. LANDING & DASHBOARD ROUTES
# -------------------------------------------------------------

@app.route("/")
@app.route("/api/index.py")
@app.route("/api/index")
@app.route("/api")
@app.route("/index.py")
def index():
    """Home / Landing page."""
    return render_template("index.html", active_page="home")


@app.route("/debug")
def debug_endpoint():
    return jsonify({
        "message": "Flask is running!",
        "path": request.path,
        "PATH_INFO": request.environ.get("PATH_INFO"),
        "SCRIPT_NAME": request.environ.get("SCRIPT_NAME"),
    })


@app.errorhandler(404)
def handle_404(e):
    if request.path.startswith("/api/index") or request.path in ["/api", "/index.py"]:
        return index()
    return jsonify({
        "error": "Not Found",
        "requested_path": request.path,
        "PATH_INFO": request.environ.get("PATH_INFO")
    }), 404


@app.route("/dashboard")
def dashboard():
    """Overview dashboard displaying interview metrics and recent sessions."""
    metrics = get_dashboard_metrics()
    recent_sessions = get_all_sessions(limit=5)
    questions = get_all_questions()
    return render_template(
        "dashboard.html",
        active_page="dashboard",
        metrics=metrics,
        recent_sessions=recent_sessions,
        questions=questions[:4]
    )


# -------------------------------------------------------------
# 2. INTERVIEW SETUP & LAUNCH
# -------------------------------------------------------------

@app.route("/setup", methods=["GET", "POST"])
def setup():
    """Configure interview parameters: Candidate name, company, and question."""
    questions = get_all_questions()

    if request.method == "POST":
        candidate_name = request.form.get("candidate_name", "Candidate").strip()
        target_company = request.form.get("target_company", "Google").strip()
        target_role = request.form.get("target_role", "Software Engineer").strip()
        question_id = int(request.form.get("question_id", questions[0]["id"]))

        # Create session in SQLite
        session_id = create_session(
            candidate_name=candidate_name,
            question_id=question_id,
            target_role=target_role,
            target_company=target_company
        )

        # Generate and log welcome message from AI interviewer
        q_data = get_question(question_id)
        welcome_text = get_welcome_message(
            candidate_name=candidate_name,
            question_title=q_data["title"],
            target_company=target_company,
            difficulty=q_data["difficulty"]
        )
        add_chat_message(session_id, sender="AI Interviewer", message=welcome_text)

        return redirect(url_for("interview_room", session_id=session_id))

    return render_template("setup.html", active_page="setup", questions=questions)


# -------------------------------------------------------------
# 3. LIVE INTERVIEW ROOM
# -------------------------------------------------------------

@app.route("/interview/<int:session_id>")
def interview_room(session_id):
    """Interactive interview room with live code editor and AI chat."""
    session_data = get_session(session_id)
    if not session_data:
        flash("Interview session not found.", "warning")
        return redirect(url_for("dashboard"))

    chat_history = get_chat_history(session_id)
    return render_template(
        "interview.html",
        active_page="interview",
        session=session_data,
        chat_history=chat_history
    )


# -------------------------------------------------------------
# 4. ASYNC API ENDPOINTS (Code Execution, Chat, Hints)
# -------------------------------------------------------------

@app.route("/api/chat", methods=["POST"])
def api_chat():
    """AJAX endpoint for conversing with the AI interviewer."""
    data = request.get_json() or {}
    session_id = data.get("session_id")
    candidate_message = data.get("message", "").strip()
    current_code = data.get("current_code", "")

    if not session_id or not candidate_message:
        return jsonify({"success": False, "error": "Missing session ID or message"}), 400

    session_data = get_session(session_id)
    if not session_data:
        return jsonify({"success": False, "error": "Session not found"}), 404

    # Log candidate message
    add_chat_message(session_id, sender="Candidate", message=candidate_message)

    # Fetch updated chat history
    history = get_chat_history(session_id)

    # Generate response
    ai_reply = chat_with_interviewer(
        candidate_message=candidate_message,
        session_data=session_data,
        chat_history=history,
        current_code=current_code
    )

    # Log AI reply
    add_chat_message(session_id, sender="AI Interviewer", message=ai_reply)

    return jsonify({
        "success": True,
        "reply": ai_reply,
        "sender": "AI Interviewer"
    })


@app.route("/api/hint", methods=["POST"])
def api_hint():
    """AJAX endpoint to unlock a progressive 3-tier hint."""
    data = request.get_json() or {}
    session_id = data.get("session_id")

    session_data = get_session(session_id)
    if not session_data:
        return jsonify({"success": False, "error": "Session not found"}), 404

    hints_used = session_data.get("hints_used", 0)
    hint_info = get_progressive_hint(session_data, hints_used)

    # Increment hints used in database
    conn = get_db_connection()
    conn.execute("UPDATE sessions SET hints_used = hints_used + 1 WHERE id = ?", (session_id,))
    conn.commit()
    conn.close()

    hint_msg = f"[Progressive Hint {hint_info['tier']}/{hint_info['max_tiers']}]: {hint_info['hint']}"
    add_chat_message(session_id, sender="AI Interviewer", message=hint_msg)

    return jsonify({
        "success": True,
        "hint": hint_info["hint"],
        "tier": hint_info["tier"],
        "max_tiers": hint_info["max_tiers"]
    })


@app.route("/api/run-code", methods=["POST"])
def api_run_code():
    """AJAX endpoint to execute code against sample test cases only."""
    data = request.get_json() or {}
    session_id = data.get("session_id")
    code_str = data.get("code", "")

    session_data = get_session(session_id)
    if not session_data:
        return jsonify({"success": False, "error": "Session not found"}), 404

    # Run against first 2 sample test cases
    sample_cases = session_data["question_test_cases"][:2]
    results = run_all_test_cases(code_str, sample_cases)

    return jsonify({
        "success": True,
        "results": results
    })


@app.route("/api/submit-code", methods=["POST"])
def api_submit_code():
    """AJAX endpoint for final submission: tests all edge cases and runs full evaluation."""
    data = request.get_json() or {}
    session_id = data.get("session_id")
    code_str = data.get("code", "")
    duration_seconds = data.get("duration_seconds", 0)

    session_data = get_session(session_id)
    if not session_data:
        return jsonify({"success": False, "error": "Session not found"}), 404

    # Update submitted code in DB
    conn = get_db_connection()
    conn.execute("""
        UPDATE sessions
        SET submitted_code = ?, duration_seconds = ?
        WHERE id = ?
    """, (code_str, duration_seconds, session_id))
    conn.commit()
    conn.close()

    # Run full test suite (samples + hidden edge cases)
    all_cases = session_data["question_test_cases"]
    test_results = run_all_test_cases(code_str, all_cases)

    # Fetch chat history for communication scoring
    chat_history = get_chat_history(session_id)

    # Run comprehensive evaluation
    evaluation = evaluate_interview_session(
        session_data=session_data,
        test_results=test_results,
        submitted_code=code_str,
        chat_history=chat_history
    )

    # Save to SQLite
    save_evaluation(
        session_id=session_id,
        overall_score=evaluation["overall_score"],
        recommendation=evaluation["recommendation"],
        correctness_score=evaluation["correctness_score"],
        complexity_score=evaluation["complexity_score"],
        quality_score=evaluation["quality_score"],
        communication_score=evaluation["communication_score"],
        test_results=test_results,
        feedback=evaluation["feedback"],
        time_complexity=evaluation["time_complexity"],
        space_complexity=evaluation["space_complexity"]
    )

    return jsonify({
        "success": True,
        "redirect_url": url_for("scorecard", session_id=session_id)
    })


# -------------------------------------------------------------
# 5. PERFORMANCE SCORECARD & PDF EXPORT
# -------------------------------------------------------------

@app.route("/scorecard/<int:session_id>")
def scorecard(session_id):
    """Display final interview evaluation, Big-O metrics, and reference code diff."""
    eval_data = get_evaluation(session_id)
    if not eval_data:
        flash("Scorecard not available. Please submit code first.", "warning")
        return redirect(url_for("interview_room", session_id=session_id))

    return render_template(
        "scorecard.html",
        active_page="scorecard",
        eval=eval_data
    )


@app.route("/download-pdf/<int:session_id>")
def download_pdf(session_id):
    """Generate and deliver downloadable PDF candidate scorecard."""
    eval_data = get_evaluation(session_id)
    if not eval_data:
        flash("Evaluation not found.", "danger")
        return redirect(url_for("dashboard"))

    candidate_name = eval_data.get("candidate_name", "Candidate")
    safe_name = "".join(c for c in candidate_name if c.isalnum() or c in (' ', '_', '-')).strip() or "Candidate"
    download_filename = f"Scorecard_{safe_name.replace(' ', '_')}_Session{session_id}.pdf"

    try:
        pdf_path, _ = generate_scorecard_pdf(eval_data, output_filename=download_filename)
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=download_filename,
            mimetype="application/pdf"
        )
    except Exception as e:
        flash(f"Error generating PDF scorecard: {str(e)}", "danger")
        return redirect(url_for("scorecard", session_id=session_id))


# -------------------------------------------------------------
# 6. QUESTIONS BANK & HISTORY & ABOUT
# -------------------------------------------------------------

@app.route("/questions")
def questions_bank():
    """Browse curated technical interview questions."""
    questions = get_all_questions()
    return render_template("questions.html", active_page="questions", questions=questions)


@app.route("/history")
def history():
    """View past mock interview sessions."""
    sessions = get_all_sessions(limit=50)
    return render_template("history.html", active_page="history", sessions=sessions)


@app.route("/about")
def about():
    """Project architecture, academic research aspects, and viva guide."""
    return render_template("about.html", active_page="about")


@app.route("/health")
def health():
    """Health check probe for Vercel, Render, and Docker."""
    return jsonify({
        "status": "healthy",
        "service": Config.APP_NAME,
        "version": Config.VERSION
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=Config.PORT, debug=True)
