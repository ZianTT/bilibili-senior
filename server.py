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
        cursor.execute("SELECT qid FROM questions WHERE qid = ?", (qid,))
        if cursor.fetchone():
            return jsonify({"status": "exist"})

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

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
