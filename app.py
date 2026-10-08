from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

DATABASE = "expenses.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            expense_date TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


@app.route("/")
def index():
    conn = get_db()

    expenses = conn.execute("""
        SELECT * FROM expenses
        ORDER BY expense_date DESC, id DESC
    """).fetchall()

    total = conn.execute("""
        SELECT COALESCE(SUM(amount), 0)
        FROM expenses
    """).fetchone()[0]

    category_data = conn.execute("""
        SELECT category, SUM(amount) AS total
        FROM expenses
        GROUP BY category
        ORDER BY total DESC
    """).fetchall()

    conn.close()

    return render_template(
        "index.html",
        expenses=expenses,
        total=total,
        category_data=category_data
    )


@app.route("/add", methods=["POST"])
def add_expense():
    title = request.form["title"]
    category = request.form["category"]
    amount = request.form["amount"]
    expense_date = request.form["expense_date"]

    conn = get_db()

    conn.execute("""
        INSERT INTO expenses
        (title, category, amount, expense_date)
        VALUES (?, ?, ?, ?)
    """, (title, category, float(amount), expense_date))

    conn.commit()
    conn.close()

    return redirect(url_for("index"))


@app.route("/delete/<int:expense_id>")
def delete_expense(expense_id):
    conn = get_db()

    conn.execute(
        "DELETE FROM expenses WHERE id = ?",
        (expense_id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("index"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)