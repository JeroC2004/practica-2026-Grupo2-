from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)
DB = 'workout.db'


def get_db():
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    return db


def init_db():
    db = get_db()
    db.executescript('''
        CREATE TABLE IF NOT EXISTS sessions (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            date         TEXT NOT NULL,
            duration_min INTEGER,
            notes        TEXT
        );
        CREATE TABLE IF NOT EXISTS exercises (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            name       TEXT NOT NULL,
            muscle     TEXT,
            sets       INTEGER,
            reps       INTEGER,
            weight_kg  REAL,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        );
    ''')
    db.commit()
    db.close()


# ── HISTORIAL ────────────────────────────────────────────────
@app.route('/')
def index():
    db = get_db()
    sessions = db.execute(
        '''SELECT s.*, COUNT(e.id) as total_exercises
           FROM sessions s
           LEFT JOIN exercises e ON e.session_id = s.id
           GROUP BY s.id
           ORDER BY s.date DESC'''
    ).fetchall()
    db.close()
    return render_template('sessions.html', sessions=sessions)


# ── DETALLE DE SESIÓN ─────────────────────────────────────────
@app.route('/session/<int:_id>')
def session(_id):
    db = get_db()
    s  = db.execute('SELECT * FROM sessions WHERE id = ?', (_id,)).fetchone()
    ex = db.execute('SELECT * FROM exercises WHERE session_id = ? ORDER BY id', (_id,)).fetchall()
    db.close()
    if not s:
        return redirect('/')
    return render_template('session.html', session=s, exercises=ex)


# ── CREAR SESIÓN ──────────────────────────────────────────────
@app.route('/create')
def create():
    from datetime import date
    today = date.today().isoformat()
    return render_template('create.html', today=today)


@app.route('/insert')
def insert():
    date         = request.args.get('date', '')
    duration_min = request.args.get('duration_min', None)
    notes        = request.args.get('notes', '')

    db = get_db()
    cur = db.execute(
        'INSERT INTO sessions (date, duration_min, notes) VALUES (?, ?, ?)',
        (date, duration_min, notes)
    )
    new_id = cur.lastrowid
    db.commit()
    db.close()
    return redirect(f'/session/{new_id}')


# ── AGREGAR EJERCICIO ─────────────────────────────────────────
@app.route('/session/<int:_id>/add-exercise')
def add_exercise(_id):
    db = get_db()
    s  = db.execute('SELECT * FROM sessions WHERE id = ?', (_id,)).fetchone()
    db.close()
    if not s:
        return redirect('/')
    return render_template('add_exercise.html', session=s)


@app.route('/session/<int:_id>/insert-exercise')
def insert_exercise(_id):
    name      = request.args.get('name', '')
    muscle    = request.args.get('muscle', '')
    sets      = request.args.get('sets', None)
    reps      = request.args.get('reps', None)
    weight_kg = request.args.get('weight_kg', None)

    db = get_db()
    db.execute(
        'INSERT INTO exercises (session_id, name, muscle, sets, reps, weight_kg) VALUES (?, ?, ?, ?, ?, ?)',
        (_id, name, muscle, sets, reps, weight_kg)
    )
    db.commit()
    db.close()
    return redirect(f'/session/{_id}')


# ── ELIMINAR EJERCICIO ────────────────────────────────────────
@app.route('/exercise/delete/<int:ex_id>')
def delete_exercise(ex_id):
    db = get_db()
    ex = db.execute('SELECT session_id FROM exercises WHERE id = ?', (ex_id,)).fetchone()
    session_id = ex['session_id'] if ex else None
    db.execute('DELETE FROM exercises WHERE id = ?', (ex_id,))
    db.commit()
    db.close()
    return redirect(f'/session/{session_id}' if session_id else '/')


# ── ELIMINAR SESIÓN ───────────────────────────────────────────
@app.route('/delete/<int:_id>')
def delete(_id):
    db = get_db()
    db.execute('DELETE FROM exercises WHERE session_id = ?', (_id,))
    db.execute('DELETE FROM sessions WHERE id = ?', (_id,))
    db.commit()
    db.close()
    return redirect('/')


# ── ESTADÍSTICAS ──────────────────────────────────────────────
@app.route('/stats')
def stats():
    db = get_db()
    # Lista de ejercicios únicos para el selector
    exercises = db.execute(
        'SELECT DISTINCT name FROM exercises ORDER BY name'
    ).fetchall()

    selected = request.args.get('exercise', '')
    history  = []
    if selected:
        history = db.execute(
            '''SELECT s.date, e.sets, e.reps, e.weight_kg, e.muscle
               FROM exercises e
               JOIN sessions s ON s.id = e.session_id
               WHERE e.name = ?
               ORDER BY s.date ASC''',
            (selected,)
        ).fetchall()
    db.close()
    return render_template('stats.html', exercises=exercises, selected=selected, history=history)

if __name__ == '__main__':
    init_db()
    # Al agregar host='0.0.0.0', Flask escucha a cualquier dispositivo de tu red Wi-Fi
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
