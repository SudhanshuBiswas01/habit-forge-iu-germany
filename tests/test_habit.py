import pytest
from datetime import datetime, timedelta

from habit import Habit
from db import Database


@pytest.fixture
def db():
    database = Database(":memory:")
    database.connect()
    yield database
    database.close()


@pytest.fixture
def daily_habit(db):
    h = Habit("Test Water", "drink stuff", "daily")
    db.save_habit(h)
    return h


def test_habit_creation():
    h = Habit("Read", "books", "weekly")
    assert h.name == "Read"
    assert h.periodicity == "weekly"
    assert h.habit_id is None
    assert h.created_at is not None


def test_completion_saved(daily_habit, db):
    ts = datetime(2025, 5, 10, 8, 0)
    db.save_completion(daily_habit.habit_id, ts)
    comps = daily_habit.get_completions(db)
    assert len(comps) == 1
    assert comps[0] == ts


def test_streak_daily(daily_habit, db):
    # three consecutive days ending yesterday (so today empty won't matter for start)
    base = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
    for i in range(1, 4):
        db.save_completion(daily_habit.habit_id, base - timedelta(days=i))
    # also today so streak includes current period
    db.save_completion(daily_habit.habit_id, base)
    assert daily_habit.get_streak(db) >= 3


def test_is_broken_daily(daily_habit, db):
    # no completions at all -> broken for current day
    assert daily_habit.is_broken(db) is True

    db.save_completion(daily_habit.habit_id, datetime.now())
    assert daily_habit.is_broken(db) is False


def test_invalid_periodicity():
    with pytest.raises(ValueError):
        Habit("x", "y", "monthly")
