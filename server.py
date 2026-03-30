from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)
DB_NAME = "tiku.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            qid TEXT PRIMARY KEY,
            question TEXT,
            ans_1 TEXT,
            ans_2 TEXT,
            ans_3 TEXT,
            ans_4 TEXT,
            answer TEXT,
            source TEXT,
            author TEXT,
            category TEXT
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/submit', methods=['POST'])
def submit_question():
    data = request.json
    if not data:
        return jsonify({"status": "error", "message": "Invalid JSON"}), 400

    qid = data.get('qid')
    question = data.get('question')
    ans_1 = data.get('ans_1')
    ans_2 = data.get('ans_2')
    ans_3 = data.get('ans_3')
    ans_4 = data.get('ans_4')
    answer = data.get('answer')
    source = data.get('source')
    author = data.get('author')
    category = data.get('category')

    if not qid:
        return jsonify({"status": "error", "message": "qid is required"}), 400

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    try:
        # Check if question already exists
        cursor.execute("SELECT qid, answer FROM questions WHERE qid = ?", (qid,))
        existing = cursor.fetchone()
        if existing:
            existing_qid, existing_answer = existing
            if existing_answer is None and answer is not None:
                # Update existing question with new answer
                cursor.execute("UPDATE questions SET answer = ? WHERE qid = ?", (answer, qid))
                conn.commit()
                return jsonify({"status": "updated", "message": "Question updated with new answer"})
            return jsonify({"status": "exists", "message": "Question already exists"})

        # Insert new question
        cursor.execute('''
            INSERT INTO questions (qid, question, ans_1, ans_2, ans_3, ans_4, answer, source, author, category)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (qid, question, ans_1, ans_2, ans_3, ans_4, answer, source, author, category))
        
        conn.commit()
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        conn.close()

@app.route('/statistics', methods=['GET'])
def statistics():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM questions")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM questions WHERE answer IS NOT NULL")
    answered = cursor.fetchone()[0]
    conn.close()
    data = {
        "total_questions": total,
        "answered_questions": answered,
        "unanswered_questions": total - answered
    }
    return jsonify(data)

@app.route('/question/<qid>', methods=['GET'])
def get_question(qid):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM questions WHERE qid = ?", (qid,))
    question = cursor.fetchone()
    conn.close()
    if question:
        keys = ["qid", "question", "ans_1", "ans_2", "ans_3", "ans_4", "answer", "source", "author", "category"]
        return jsonify(dict(zip(keys, question)))
    else:
        return jsonify({"status": "error", "message": "Question not found"}), 404

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
