from flask import Flask, render_template, request, redirect, url_for, session
from questions import questions
import random

app = Flask(__name__)
app.secret_key = "ballknower123"


@app.route('/')
def home():
    try:
        with open("leaderboard.txt", "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        lines = []

    scores = {}
    for line in lines:
        name, score = line.strip().split(",")
        score = int(score)
        if name not in scores or scores[name] < score:
            scores[name] = score

    top_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:10]

    leaderboard_html = "<ol>"
    for name, score in top_scores:
        leaderboard_html += f"<li>{name}: {score}</li>"
    leaderboard_html += "</ol>"

    return f'''
    <html>
    <head>
        <link rel="stylesheet" href="/static/style.css">
        <title>Ball Knower</title>
    </head>
    <body>
        <div class="container">
            <h1>🏈 Are you a ball knower?</h1>
            <form action="/start" method="POST">
                <label>Enter your name:</label><br>
                <input type="text" name="username" required>
                <input type="submit" value="Start Game">
            </form>

            <h2>🏆 Leaderboard</h2>
            {leaderboard_html}
        </div>
    </body>
    </html>
    '''


@app.route('/start', methods=['POST'])
def start():
    session['username'] = request.form.get('username')
    session['streak'] = 0
    session['used_questions'] = []
    return redirect(url_for('question'))


@app.route('/question')
def question():
    used = session.get('used_questions', [])
    unused = [i for i in range(len(questions)) if i not in used]

    if not unused:
        return f"""
        <h3>🔥 You’ve answered every question correctly!</h3>
        <p>Final streak: {session['streak']}</p>
        <a href="/">Play Again</a> | <a href="/leaderboard">Leaderboard</a>
        """

    idx = random.choice(unused)
    q = questions[idx]
    session['used_questions'].append(idx)
    session['correct_answer'] = q['answer']
    return render_template("index.html",
                           question=q['question'],
                           choices=q['choices'],
                           streak=session['streak'])


@app.route('/answer', methods=['POST'])
def answer():
    selected = request.form.get('choice')
    correct = session.get('correct_answer')
    username = session.get('username')

    if selected == correct:
        session['streak'] += 1
        return redirect(url_for('question'))
    else:
        final_streak = session['streak']
        with open("leaderboard.txt", "a") as f:
            f.write(f"{username},{final_streak}\n")
        session['streak'] = 0
        session['used_questions'] = []
        return f"""
        <h3>Wrong! The correct answer was <b>{correct}</b>.</h3>
        <p>Your final streak: {final_streak}</p>
        <a href="/">Play Again</a> | <a href="/leaderboard">Leaderboard</a>
        """


@app.route('/leaderboard')
def leaderboard():
    try:
        with open("leaderboard.txt", "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        lines = []

    scores = {}
    for line in lines:
        name, score = line.strip().split(",")
        score = int(score)
        if name not in scores or scores[name] < score:
            scores[name] = score

    top_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:10]

    output = "<h1>🏆 Leaderboard</h1><ol>"
    for name, score in top_scores:
        output += f"<li>{name}: {score}</li>"
    output += "</ol><a href='/'>Back to Game</a>"
    return output


if __name__ == "__main__":
    app.run(debug=True)
