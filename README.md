# Habit Tracker

A small command-line habit tracker built for an IU Germany OOP/functional programming project. Track daily and weekly habits, log completions, and check streaks with a bit of analytics on the side.

## Requirements

- Python 3.7+
- pip

## Install

```bash
cd habit_tracker
pip install -r requirements.txt
```

## Run

From the `habit_tracker` folder:

```bash
python cli.py
```

On first run the app seeds five sample habits with about four weeks of history (only when the database is empty).

## Tests

```bash
pytest
```

Run from `habit_tracker` so imports resolve correctly.

## Reset / reseed data

Delete `habits.db` in the project folder and start the app again. Preload runs only when there are no habits in the database.

## Project structure

```
habit_tracker/
├── habit.py          # Habit model + streak logic
├── db.py             # SQLite persistence
├── tracker.py        # HabitTracker service
├── analytics.py      # Functional helpers (filter/map/reduce)
├── cli.py            # Click CLI entry point
├── preload.py        # Sample data seeding
├── tests/
│   ├── test_habit.py
│   └── test_analytics.py
├── habits.db         # created at runtime
├── requirements.txt
└── README.md
```
