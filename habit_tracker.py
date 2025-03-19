from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///habits.db'  # SQLite database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "your_secret_key"  # Required for flash messages
db = SQLAlchemy(app)

# Habit Model
class Habit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    frequency = db.Column(db.String(50), nullable=False)
    start_date = db.Column(db.String(50), nullable=False, default=datetime.now().strftime("%Y-%m-%d"))
    priority = db.Column(db.String(20), nullable=False, default="Medium")

    def __repr__(self):
        return f'<Habit {self.name}>'

# Progress Model
class Progress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    habit_id = db.Column(db.Integer, db.ForeignKey('habit.id'), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    completed = db.Column(db.Boolean, nullable=False)
    notes = db.Column(db.String(200), nullable=True)  # Notes field for additional details
    habit = db.relationship('Habit', backref=db.backref('progress', lazy=True))

    def __repr__(self):
        return f'<Progress {self.date} for Habit {self.habit_id}>'

# Initialize database
with app.app_context():
    db.create_all()

# Utility Functions
def calculate_streak(progress_entries):
    progress_dates = [entry.date for entry in progress_entries if entry.completed]
    streak = 0
    current_streak = 0
    last_date = None

    for date in sorted(progress_dates):
        if last_date:
            if (datetime.strptime(date, "%Y-%m-%d") - datetime.strptime(last_date, "%Y-%m-%d")).days == 1:
                current_streak += 1
            else:
                current_streak = 1
        else:
            current_streak = 1
        last_date = date
        streak = max(streak, current_streak)

    return streak

# Inject calculate_streak globally in Jinja templates
@app.context_processor
def inject_functions():
    return dict(calculate_streak=calculate_streak)

# Route to display all habits
@app.route('/')
def index():
    habits = Habit.query.all()
    return render_template('index.html', habits=habits)

# Route to add a new habit
@app.route('/add_habit', methods=['GET', 'POST'])
def add_habit():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        frequency = request.form['frequency']
        start_date = request.form['start_date']
        priority = request.form['priority']

        new_habit = Habit(name=name, description=description, frequency=frequency, start_date=start_date, priority=priority)
        db.session.add(new_habit)
        db.session.commit()

        flash("Habit added successfully!", "success")
        return redirect(url_for('index'))

    return render_template('add_habit.html')

# Route to log progress for a habit
@app.route('/log_progress', methods=['GET', 'POST'])
def log_progress():
    if request.method == 'POST':
        habit_id = request.form['habit_id']
        completed = request.form.get('completed') == 'true'  # 'true' means True, 'false' means False
        date = datetime.now().strftime("%Y-%m-%d")
        notes = request.form.get('notes', '')  # Capture any additional notes
        new_progress = Progress(habit_id=habit_id, date=date, completed=completed, notes=notes)
        db.session.add(new_progress)
        db.session.commit()

        flash("Progress logged successfully!", "success")
        return redirect(url_for('view_progress'))  # Redirect to view progress page
    
    habits = Habit.query.all()
    return render_template('log_progress.html', habits=habits)

# Route to view progress for a specific habit
@app.route('/view_progress')
def view_progress():
    habits = Habit.query.all()
    progress_data = {}

    for habit in habits:
        progress = Progress.query.filter_by(habit_id=habit.id).all()  # Fetch all progress for each habit
        streak = calculate_streak(progress)

        progress_data[habit.name] = {
            'progress': progress,
            'streak': streak
        }

    return render_template('view_progress.html', progress_data=progress_data)

# Route to see all habits
@app.route('/all_habits')
def all_habits():
    habits = Habit.query.all()
    return render_template('all_habits.html', habits=habits)

if __name__ == '__main__':
    app.run(debug=True)
