from datetime import datetime

from habit import Habit
from db import Database
from preload import seed_habits


class HabitTracker:
    def __init__(self, db_path="habits.db"):
        self.db = Database(db_path)
        self.db.connect()

    def create_habit(self, name, description, periodicity):
        habit = Habit(name, description, periodicity)
        self.db.save_habit(habit)
        return habit

    def delete_habit(self, habit_id):
        self.db.delete_habit(habit_id)

    def complete_habit(self, habit_id):
        habits = self.get_all_habits()
        for h in habits:
            if h.habit_id == habit_id:
                h.complete(self.db)
                return h
        return None

    def get_all_habits(self):
        return self.db.load_all_habits()

    def load_predefined_habits(self):
        if self.db.is_empty():
            seed_habits(self)
            return True
        return False

    def get_habit_by_id(self, habit_id):
        for h in self.get_all_habits():
            if h.habit_id == habit_id:
                return h
        return None
