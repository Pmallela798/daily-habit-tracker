from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

# Initialize Flask app
app = Flask(__name__)

# Configurations for database and session handling
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///habits.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "your_secret_key"  # Secret key for flashing messages

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# -------------------- Models --------------------

# Model to store habit details
class Habit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    frequency = db.Column(db.String(50), nullable=False)
    start_date = db.Column(db.String(50), nullable=False, default=datetime.now().strftime("%Y-%m-%d"))
    priority = db.Column(db.String(20), nullable=False, default="Medium")

    def __repr__(self):
        return f'<Habit {self.name}>'

# Model to track daily progress of a habit
class Progress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    habit_id = db.Column(db.Integer, db.ForeignKey('habit.id'), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    completed = db.Column(db.Boolean, nullable=False)
    notes = db.Column(db.String(200), nullable=True)
    
    # Relationship to access habit from progress
    habit = db.relationship('Habit', backref=db.backref('progress', lazy=True))

    def __repr__(self):
        return f'<Progress {self.date} for Habit {self.habit_id}>'

# Create database tables
with app.app_context():
    db.create_all()

# -------------------- Utility Functions --------------------

# Calculate the longest current streak of completed days
def calculate_streak(progress_entries):
    progress_dates = [entry.date for entry in progress_entries if entry.completed]
    streak = 0
    current_streak = 0
    last_date = None

    for date in sorted(progress_dates):
        if last_date:
            # Check if days are consecutive
            if (datetime.strptime(date, "%Y-%m-%d") - datetime.strptime(last_date, "%Y-%m-%d")).days == 1:
                current_streak += 1
            else:
                current_streak = 1
        else:
            current_streak = 1
        last_date = date
        streak = max(streak, current_streak)

    return streak

# Inject utility function into Jinja2 templates
@app.context_processor
def inject_functions():
    return dict(calculate_streak=calculate_streak)

# -------------------- Routes --------------------

# Home page: display all habits
@app.route('/')
def index():
    habits = Habit.query.all()
    return render_template('index.html', habits=habits)

# Add a new habit
@app.route('/add_habit', methods=['GET', 'POST'])
def add_habit():
    if request.method == 'POST':
        new_habit = Habit(
            name=request.form['name'],
            description=request.form['description'],
            frequency=request.form['frequency'],
            start_date=request.form['start_date'],
            priority=request.form['priority']
        )
        db.session.add(new_habit)
        db.session.commit()
        flash("Habit added successfully!", "success")
        return redirect(url_for('index'))
    return render_template('add_habit.html')

# Edit an existing habit
@app.route('/edit_habit/<int:habit_id>', methods=['GET', 'POST'])
def edit_habit(habit_id):
    habit = Habit.query.get_or_404(habit_id)
    if request.method == 'POST':
        habit.name = request.form['name']
        habit.description = request.form['description']
        habit.frequency = request.form['frequency']
        habit.start_date = request.form['start_date']
        habit.priority = request.form['priority']
        db.session.commit()
        flash('Habit updated successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('edit_habit.html', habit=habit)

# Delete a habit and its associated progress
@app.route('/delete_habit/<int:habit_id>', methods=['POST'])
def delete_habit(habit_id):
    habit = Habit.query.get_or_404(habit_id)
    Progress.query.filter_by(habit_id=habit.id).delete()
    db.session.delete(habit)
    db.session.commit()
    flash('Habit deleted successfully!', 'success')
    return redirect(url_for('index'))

# Log daily progress for a habit
@app.route('/log_progress', methods=['GET', 'POST'])
def log_progress():
    if request.method == 'POST':
        habit_id = request.form['habit_id']
        completed = request.form.get('completed') == 'true'
        date = datetime.now().strftime("%Y-%m-%d")
        notes = request.form.get('notes', '')
        new_progress = Progress(habit_id=habit_id, date=date, completed=completed, notes=notes)
        db.session.add(new_progress)
        db.session.commit()
        flash("Progress logged successfully!", "success")
        return redirect(url_for('view_progress'))
    habits = Habit.query.all()
    return render_template('log_progress.html', habits=habits)

# View all progress entries and streaks
@app.route('/view_progress')
def view_progress():
    habits = Habit.query.all()
    progress_data = {}
    for habit in habits:
        progress = Progress.query.filter_by(habit_id=habit.id).all()
        streak = calculate_streak(progress)
        progress_data[habit.name] = {'progress': progress, 'streak': streak}
    return render_template('view_progress.html', progress_data=progress_data)

# Show reminders for habits not completed today
@app.route('/reminders')
def reminders():
    today = datetime.now().strftime("%Y-%m-%d")
    habits = Habit.query.all()
    due_today = []
    for habit in habits:
        last_progress = Progress.query.filter_by(habit_id=habit.id, completed=True).order_by(Progress.date.desc()).first()
        if not last_progress or last_progress.date != today:
            due_today.append(habit)
    return render_template('reminders.html', habits=due_today)

# View all habits (alternate route)
@app.route('/all_habits')
def all_habits():
    habits = Habit.query.all()
    return render_template('all_habits.html', habits=habits)

# Display a static habit recommendation page
@app.route("/recommend_habit")
def recommend_habit():
    return render_template("recommend_habit.html")

# Run the app in debug mode
if __name__ == '__main__':
    app.run(debug=True)
