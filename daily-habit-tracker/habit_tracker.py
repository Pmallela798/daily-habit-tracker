from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///habits.db'  # SQLite database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "your_secret_key"  # Required for flash messages
db = SQLAlchemy(app)

# Habit model
class Habit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    frequency = db.Column(db.String(50), nullable=False)
    start_date = db.Column(db.String(50), nullable=False, default=datetime.now().strftime("%Y-%m-%d"))
    priority = db.Column(db.String(20), nullable=False, default="Medium")

class Progress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    habit_id = db.Column(db.Integer, db.ForeignKey('habit.id'), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    completed = db.Column(db.Boolean, nullable=False)
    habit = db.relationship('Habit', backref=db.backref('progress', lazy=True))

# Initialize database
with app.app_context():
    db.create_all()

# Home route to display all habits
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
@app.route('/log_progress/<int:habit_id>', methods=['GET', 'POST'])
def log_progress(habit_id):
    habit = Habit.query.get_or_404(habit_id)
    if request.method == 'POST':
        completed = request.form['completed'] == 'true'
        date = datetime.now().strftime("%Y-%m-%d")
        new_progress = Progress(habit_id=habit_id, date=date, completed=completed)
        db.session.add(new_progress)
        db.session.commit()

        flash(f"Progress logged for '{habit.name}'!", "success")
        return redirect(url_for('view_progress', habit_id=habit_id))
    
    return render_template('log_progress.html', habit=habit)

# Route to view progress for a specific habit
@app.route('/progress/<int:habit_id>')
def view_progress(habit_id):
    habit = Habit.query.get_or_404(habit_id)
    progress = Progress.query.filter_by(habit_id=habit_id).all()
    return render_template('progress.html', habit=habit, progress=progress)

if __name__ == '__main__':
    app.run(debug=True)
