import random
from datetime import datetime, timedelta


PREDEFINED_HABITS = [
    ("Drink 2L of Water", "Stay hydrated throughout the day", "daily"),
    ("Morning Workout", "30 min exercise before breakfast", "daily"),
    ("Read 20 Pages", "Fiction or non-fiction, doesn't matter", "daily"),
    ("Weekly Review", "Look back at goals and plan ahead", "weekly"),
    ("Grocery Shopping", "Stock up for the week", "weekly"),
]


def _week_start(d):
    return d - timedelta(days=d.weekday())


def generate_daily_completions(days_back=28, miss_count=3):
    """Roughly 28 days of completions, skip a few days at random."""
    today = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
    all_days = [today - timedelta(days=i) for i in range(days_back, 0, -1)]
    all_days.append(today)

    # pick which days to skip (not today — keeps current streak interesting)
    candidates = [d for d in all_days if d.date() != today.date()]
    skip = set(random.sample(candidates, min(miss_count, len(candidates))))

    completions = []
    for day in all_days:
        if day in skip:
            continue
        # vary the time a bit so it doesn't look copy-pasted
        hour = random.choice([7, 8, 9, 12, 18, 20])
        completions.append(day.replace(hour=hour, minute=random.randint(0, 59)))
    return completions


def generate_weekly_completions(weeks=4):
    today = datetime.now()
    completions = []
    for w in range(weeks):
        monday = _week_start(today.date()) - timedelta(weeks=w)
        # usually do it on saturday
        done_day = datetime.combine(monday + timedelta(days=5), datetime.min.time())
        done_day = done_day.replace(hour=11, minute=30)
        completions.append(done_day)
    return completions


def seed_habits(tracker):
    """Called when DB is empty — loads the 5 default habits + history."""
    from habit import Habit

    for name, desc, period in PREDEFINED_HABITS:
        h = tracker.create_habit(name, desc, period)
        if period == "daily":
            dates = generate_daily_completions()
        else:
            dates = generate_weekly_completions()
        for dt in dates:
            tracker.db.save_completion(h.habit_id, dt)
