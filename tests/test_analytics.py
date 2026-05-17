import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock

from habit import Habit
import analytics as ana


@pytest.fixture
def habit_list():
  return [
      Habit("A", "", "daily", habit_id=1),
      Habit("B", "", "weekly", habit_id=2),
      Habit("C", "", "daily", habit_id=3),
  ]


def test_get_all_habits(habit_list):
    result = ana.get_all_habits(habit_list)
    assert len(result) == 3


def test_filter_by_periodicity(habit_list):
    daily = ana.get_habits_by_periodicity(habit_list, "daily")
    assert len(daily) == 2
    assert all(h.periodicity == "daily" for h in daily)

    weekly = ana.get_habits_by_periodicity(habit_list, "weekly")
    assert len(weekly) == 1


def test_longest_streak_for():
    h = Habit("S", "", "daily", habit_id=1)
    db = MagicMock()
    h.get_streak = MagicMock(return_value=7)
    assert ana.get_longest_streak_for(h, db) == 7


def test_longest_streak_all(habit_list):
    db = MagicMock()
    habit_list[0].get_streak = lambda db: 3
    habit_list[1].get_streak = lambda db: 10
    habit_list[2].get_streak = lambda db: 5
    assert ana.get_longest_streak_all(habit_list, db) == 10


def test_longest_streak_all_empty():
    assert ana.get_longest_streak_all([], MagicMock()) == 0
