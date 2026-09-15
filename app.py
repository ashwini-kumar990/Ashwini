from flask import Flask, render_template, request, session
import json, re

app = Flask(__name__)
app.secret_key = "student-support-demo-key"

with open("knowledge_base.json", "r", encoding="utf-8") as f:
    knowledge_base = json.load(f)

def retrieve_answer(question):
    words = set(re.findall(r"\b\w+\b", question.lower()))
    best, score = None, 0
    for item in knowledge_base:
        text = (item["question"] + " " + item["answer"]).lower()
        s = sum(1 for w in words if w in text)
        if s > score:
            score, best = s, item["answer"]
    return best

def attendance_tool(attended, total):
    if total <= 0 or attended < 0 or attended > total:
        return "Please enter valid attendance values."
    return f"Your attendance is {(attended/total)*100:.2f}%."

def agent(question):
    q = question.strip()
    low = q.lower()

    m = re.search(r"my name is ([a-zA-Z ]+)", q, re.I)
    if m:
        name = m.group(1).strip()
        session["student_name"] = name
        return f"Nice to meet you, {name}! I will remember your name during this session."

    if "what is my name" in low or "do you know my name" in low:
        return f"Your name is {session['student_name']}." if session.get("student_name") else "You have not told me your name yet."

    if "attendance" in low:
        nums = re.findall(r"\d+(?:\.\d+)?", q)
        if len(nums) >= 2:
            return attendance_tool(float(nums[0]), float(nums[1]))

    answer = retrieve_answer(q)
    return answer or "Sorry, I could not find the answer in my college knowledge base."

@app.route("/", methods=["GET", "POST"])
def home():
    answer, question = None, ""
    if request.method == "POST":
        question = request.form.get("question", "")
        if question.strip():
            answer = agent(question)
    return render_template("index.html", answer=answer, question=question)

if __name__ == "__main__":
    app.run(debug=True)
