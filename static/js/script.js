/**
 * AI Mock Technical Interviewer - Interactive Client Engine
 */

let interviewSeconds = 0;
let timerInterval = null;
let speechRecognizer = null;
let isRecognizing = false;

document.addEventListener("DOMContentLoaded", function () {
    // -------------------------------------------------------------
    // 1. LIVE INTERVIEW STOPWATCH TIMER
    // -------------------------------------------------------------
    const timerEl = document.getElementById("interviewTimer");
    if (timerEl) {
        timerInterval = setInterval(() => {
            interviewSeconds++;
            const mins = String(Math.floor(interviewSeconds / 60)).padStart(2, "0");
            const secs = String(interviewSeconds % 60).padStart(2, "0");
            timerEl.innerText = `${mins}:${secs}`;
        }, 1000);
    }

    // -------------------------------------------------------------
    // 2. CODE EDITOR TAB SUPPORT (Insert 4 spaces)
    // -------------------------------------------------------------
    const codeEditor = document.getElementById("codeEditor");
    if (codeEditor) {
        codeEditor.addEventListener("keydown", function (e) {
            if (e.key === "Tab") {
                e.preventDefault();
                const start = this.selectionStart;
                const end = this.selectionEnd;
                this.value = this.value.substring(0, start) + "    " + this.value.substring(end);
                this.selectionStart = this.selectionEnd = start + 4;
            }
        });
    }

    // Initialize Web Speech Recognition if supported
    initSpeechRecognition();
});

// -------------------------------------------------------------
// 3. CHAT INTERACTION & SPEECH SYNTHESIS
// -------------------------------------------------------------
function sendChatMessage(e) {
    if (e) e.preventDefault();
    const chatInput = document.getElementById("chatInput");
    if (!chatInput) return;

    const message = chatInput.value.trim();
    if (!message) return;

    const chatBox = document.getElementById("chatMessagesBox");
    const codeEditor = document.getElementById("codeEditor");
    const currentCode = codeEditor ? codeEditor.value : "";

    // Append Candidate Bubble
    appendMessageBubble("Candidate", message);
    chatInput.value = "";

    // Show temporary thinking indicator
    const thinkingId = appendThinkingBubble();

    // Send to backend API
    fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            session_id: SESSION_ID,
            message: message,
            current_code: currentCode
        })
    })
    .then(res => res.json())
    .then(data => {
        removeBubble(thinkingId);
        if (data.success) {
            appendMessageBubble("AI Interviewer", data.reply);
            speakAIResponse(data.reply);
        } else {
            appendMessageBubble("AI Interviewer", "Error: " + (data.error || "Unable to process message."));
        }
    })
    .catch(err => {
        removeBubble(thinkingId);
        appendMessageBubble("AI Interviewer", "Connection error. Please try again.");
    });
}

function appendMessageBubble(sender, text) {
    const chatBox = document.getElementById("chatMessagesBox");
    if (!chatBox) return;

    const isCand = (sender === "Candidate");
    const wrap = document.createElement("div");
    wrap.className = `chat-bubble-wrap mb-2.5 ${isCand ? "text-end" : ""}`;

    wrap.innerHTML = `
        <div class="text-2xs text-muted mb-0.5">${sender}</div>
        <div class="chat-bubble d-inline-block text-start p-2.5 px-3 rounded-4 text-xs ${isCand ? "bg-primary text-white" : "bg-light text-navy border"}" style="max-width: 85%; line-height: 1.5; white-space: pre-wrap;">${escapeHtml(text)}</div>
    `;

    chatBox.appendChild(wrap);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function appendThinkingBubble() {
    const chatBox = document.getElementById("chatMessagesBox");
    if (!chatBox) return null;

    const id = "thinking_" + Date.now();
    const wrap = document.createElement("div");
    wrap.id = id;
    wrap.className = "chat-bubble-wrap mb-2.5 text-start";
    wrap.innerHTML = `
        <div class="text-2xs text-muted mb-0.5">AI Interviewer</div>
        <div class="chat-bubble d-inline-block p-2 px-3 rounded-4 text-xs bg-light text-muted border">
            <span class="spinner-grow spinner-grow-sm me-1" role="status"></span> Thinking...
        </div>
    `;
    chatBox.appendChild(wrap);
    chatBox.scrollTop = chatBox.scrollHeight;
    return id;
}

function removeBubble(id) {
    if (!id) return;
    const el = document.getElementById(id);
    if (el) el.remove();
}

function escapeHtml(text) {
    const div = document.createElement("div");
    div.innerText = text;
    return div.innerHTML;
}

// -------------------------------------------------------------
// 4. WEB SPEECH API: SPEECH RECOGNITION (VOICE INPUT)
// -------------------------------------------------------------
function initSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        const micBtn = document.getElementById("micBtn");
        if (micBtn) micBtn.title = "Speech recognition not supported in this browser";
        return;
    }

    speechRecognizer = new SpeechRecognition();
    speechRecognizer.continuous = false;
    speechRecognizer.interimResults = false;
    speechRecognizer.lang = "en-US";

    speechRecognizer.onstart = function () {
        isRecognizing = true;
        const micBtn = document.getElementById("micBtn");
        if (micBtn) micBtn.classList.add("mic-recording");
    };

    speechRecognizer.onresult = function (event) {
        const transcript = event.results[0][0].transcript;
        const chatInput = document.getElementById("chatInput");
        if (chatInput) {
            chatInput.value = transcript;
            chatInput.focus();
        }
    };

    speechRecognizer.onerror = function () {
        stopSpeechRecognition();
    };

    speechRecognizer.onend = function () {
        stopSpeechRecognition();
    };
}

function toggleSpeechRecognition() {
    if (!speechRecognizer) {
        alert("Web Speech API is not supported in your browser. Please use Google Chrome or Edge.");
        return;
    }
    if (isRecognizing) {
        speechRecognizer.stop();
        stopSpeechRecognition();
    } else {
        speechRecognizer.start();
    }
}

function stopSpeechRecognition() {
    isRecognizing = false;
    const micBtn = document.getElementById("micBtn");
    if (micBtn) micBtn.classList.remove("mic-recording");
}

function speakAIResponse(text) {
    const ttsToggle = document.getElementById("ttsToggle");
    if (!ttsToggle || !ttsToggle.checked || !window.speechSynthesis) return;

    window.speechSynthesis.cancel();
    const cleanText = text.replace(/\[Hint.*?\]:\s*/gi, "").replace(/```[\s\S]*?```/g, "Code snippet");
    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    window.speechSynthesis.speak(utterance);
}

// -------------------------------------------------------------
// 5. PROGRESSIVE 3-TIER HINT REQUEST
// -------------------------------------------------------------
function requestProgressiveHint() {
    const btn = document.getElementById("requestHintBtn");
    if (btn) btn.disabled = true;

    fetch("/api/hint", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: SESSION_ID })
    })
    .then(res => res.json())
    .then(data => {
        if (btn) btn.disabled = false;
        if (data.success) {
            const badge = document.getElementById("hintsCountBadge");
            if (badge) badge.innerText = data.tier;

            const hintText = `[Progressive Hint Level ${data.tier}/${data.max_tiers}]:\n${data.hint}`;
            appendMessageBubble("AI Interviewer", hintText);
            speakAIResponse(data.hint);

            // Switch to chat tab to see hint
            const chatTabBtn = document.querySelector('[data-bs-target="#tabChat"]');
            if (chatTabBtn) {
                const tab = new bootstrap.Tab(chatTabBtn);
                tab.show();
            }
        }
    })
    .catch(() => {
        if (btn) btn.disabled = false;
    });
}

// -------------------------------------------------------------
// 6. RUN SAMPLE TEST CASES
// -------------------------------------------------------------
function runSampleTests() {
    const codeEditor = document.getElementById("codeEditor");
    const code = codeEditor ? codeEditor.value : "";
    const runBtn = document.getElementById("runTestsBtn");
    const outArea = document.getElementById("testOutputArea");
    const summaryBadge = document.getElementById("testSummaryBadge");

    if (runBtn) {
        runBtn.disabled = true;
        runBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Running...';
    }

    if (outArea) outArea.innerHTML = '<div class="text-muted"><i class="bi bi-gear-wide-connected me-1"></i>Executing code in sandbox...</div>';

    fetch("/api/run-code", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            session_id: SESSION_ID,
            code: code
        })
    })
    .then(res => res.json())
    .then(data => {
        if (runBtn) {
            runBtn.disabled = false;
            runBtn.innerHTML = '<i class="bi bi-play-fill me-1"></i>Run Sample Tests';
        }

        if (data.success && data.results) {
            const res = data.results;
            if (res.error) {
                if (summaryBadge) {
                    summaryBadge.className = "badge bg-danger text-2xs";
                    summaryBadge.innerText = "Error";
                }
                outArea.innerHTML = `<div class="text-danger fw-bold"><i class="bi bi-x-circle me-1"></i>${escapeHtml(res.error)}</div>`;
                return;
            }

            if (summaryBadge) {
                summaryBadge.className = `badge bg-${res.all_passed ? "success" : "warning"} text-2xs`;
                summaryBadge.innerText = `${res.passed_count}/${res.total} Passed (${res.pass_percentage}%)`;
            }

            let html = "";
            res.details.forEach(tc => {
                const passClass = tc.passed ? "text-success" : "text-danger";
                const passIcon = tc.passed ? "bi-check-circle-fill" : "bi-x-circle-fill";
                html += `
                    <div class="mb-2 p-2 rounded bg-white border">
                        <div class="d-flex align-items-center justify-content-between mb-1">
                            <span class="fw-bold ${passClass}"><i class="bi ${passIcon} me-1"></i>Test Case ${tc.case_number}</span>
                            <span class="text-muted text-2xs">${tc.duration_ms} ms</span>
                        </div>
                        <div class="text-2xs text-muted">Input: ${escapeHtml(JSON.stringify(tc.input))}</div>
                        <div class="text-2xs text-muted">Expected: ${escapeHtml(JSON.stringify(tc.expected))}</div>
                        <div class="text-2xs text-dark">Output: ${escapeHtml(JSON.stringify(tc.actual))}</div>
                        ${tc.error ? `<div class="text-danger text-2xs mt-1">${escapeHtml(tc.error)}</div>` : ""}
                    </div>
                `;
            });
            outArea.innerHTML = html;
        }
    })
    .catch(() => {
        if (runBtn) {
            runBtn.disabled = false;
            runBtn.innerHTML = '<i class="bi bi-play-fill me-1"></i>Run Sample Tests';
        }
        if (outArea) outArea.innerHTML = '<div class="text-danger">Execution request failed.</div>';
    });
}

// -------------------------------------------------------------
// 7. FINAL SUBMISSION & EVALUATION
// -------------------------------------------------------------
function submitFinalSolution() {
    if (!confirm("Are you ready to submit your solution? This will test all hidden edge cases and generate your final evaluation scorecard.")) {
        return;
    }

    const codeEditor = document.getElementById("codeEditor");
    const code = codeEditor ? codeEditor.value : "";
    const submitBtn = document.getElementById("submitSolutionBtn");

    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Evaluating...';
    }

    fetch("/api/submit-code", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            session_id: SESSION_ID,
            code: code,
            duration_seconds: interviewSeconds
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success && data.redirect_url) {
            window.location.href = data.redirect_url;
        } else {
            alert("Error submitting solution: " + (data.error || "Unknown error"));
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i class="bi bi-check2-circle"></i><span>Submit Solution</span>';
            }
        }
    })
    .catch(err => {
        alert("Submission failed. Check network connection.");
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="bi bi-check2-circle"></i><span>Submit Solution</span>';
        }
    });
}
