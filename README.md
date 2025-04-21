Project Name:    Daily Habit Tracker: A Tool for Building and Maintaining Healthy Habits

Description:
The Habit Tracker is a web application built using Flask that helps users manage and track their habits. Users can add new habits, log progress, view their habit history, and monitor their streaks. The application allows tracking the frequency, start date, and priority of each habit, along with a dedicated space for logging progress and adding notes.

Purpose:
The goal of the Habit Tracker is to empower users to build positive habits and maintain consistency by providing a platform to track their progress. By visualizing their progress and streaks, users can stay motivated and committed to their goals.

Value:

Motivation & Accountability: Users can see their progress and streaks, making it easier to stay motivated.

Customization: Users can define the frequency, priority, and other details for each habit, making it adaptable to various habits.

Progress Insights: With a streak calculation feature, users can easily monitor their consistency over time.

Simple Interface: The application offers an intuitive user interface to manage habits without unnecessary complexity.

Technologies Used:

Flask: A Python web framework for building the application.

SQLAlchemy: An ORM used to interact with the SQLite database.

SQLite: A lightweight relational database used to store habit and progress data.

Jinja2: Templating engine for rendering HTML pages.

Bootstrap: (Potentially used in templates) for creating responsive and clean user interfaces.

Setup Instructions

Make sure Python 3.7 or higher is installed on your system. You can download it from the official site: https://www.python.org/downloads/.

To check if Python is installed, run:

python --version

Clone the Project from GitHub

Open your terminal (or Command Prompt) and run the following command to clone the repository:

git clone  https://github.com/Pmallela798/daily-habit-tracker

Then navigate to the project directory:

cd daily-habit-tracker

cd src

Install Required Packages

pip install -r requirements.txt



Run the Application

python habit_tracker.py 

This will launch the application at:http://127.0.0.1:5000

Open your browser and go to http://127.0.0.1:5000 to start using the Habit Tracker. You can now add habits, track progress, view reminders, and more.

