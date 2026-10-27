
from flask import Flask, render_template, request, redirect
import os
import psycopg
from psycopg.rows import dict_row

app = Flask(__name__)

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://student:studentpass@localhost:5432/tasksdb"
)

def get_connection():
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)

def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                completed BOOLEAN DEFAULT FALSE
            )
        """)

@app.route("/")
def home():
    with get_connection() as conn:
        tasks = conn.execute(
            "SELECT * FROM tasks ORDER BY id DESC"
        ).fetchall()
    return render_template("index.html", tasks=tasks)

@app.route("/add", methods=["POST"])
def add_task():
    title = request.form.get("title", "").strip()
    if title:
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO tasks (title) VALUES (%s)", (title,)
            )
    return redirect("/")

@app.route("/complete/<int:task_id>", methods=["POST"])
def complete_task(task_id):
    with get_connection() as conn:
        conn.execute(
            "UPDATE tasks SET completed = NOT completed WHERE id = %s",
            (task_id,)
        )
    return redirect("/")

@app.route("/delete/<int:task_id>", methods=["POST"])
def delete_task(task_id):
    with get_connection() as conn:
        conn.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
    return redirect("/")

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
