from datetime import datetime, date, timedelta


class Habit:
    def __init__(self, name, description, periodicity, habit_id=None, created_at=None):
        self.habit_id = habit_id
        self.name = name
        self.description = description
        if periodicity not in ("daily", "weekly"):
            raise ValueError("periodicity must be 'daily' or 'weekly'")
        self.periodicity = periodicity
        self.created_at = created_at or datetime.now()

    def complete(self, db):
        db.save_completion(self.habit_id, datetime.now())

    def get_completions(self, db):
        return db.load_completions(self.habit_id)

    def _completion_dates(self, db):
        return {c.date() for c in self.get_completions(db)}

    def _week_start(self, d):
        # monday of the week
        return d - timedelta(days=d.weekday())

    def _period_has_completion(self, completion_dates, period_start, periodicity):
        if periodicity == "daily":
            return period_start in completion_dates
        week_end = period_start + timedelta(days=6)
        return any(period_start <= d <= week_end for d in completion_dates)

    def _walk_periods_back(self, start, periodicity):
        if periodicity == "daily":
            while True:
                yield start
                start = start - timedelta(days=1)
        else:
            while True:
                yield start
                start = start - timedelta(days=7)

    def _streak_start_period(self, completion_dates):
        today = date.today()
        if self.periodicity == "daily":
            if today in completion_dates:
                return today
            return today - timedelta(days=1)
        this_week = self._week_start(today)
        weeks = {self._week_start(d) for d in completion_dates}
        if this_week in weeks:
            return this_week
        return this_week - timedelta(days=7)

    def get_streak(self, db):
        completion_dates = self._completion_dates(db)
        if not completion_dates:
            return 0

        streak = 0
        for period_start in self._walk_periods_back(
            self._streak_start_period(completion_dates), self.periodicity
        ):
            if self._period_has_completion(completion_dates, period_start, self.periodicity):
                streak += 1
            else:
                break
        return streak

    def is_broken(self, db):
        completion_dates = self._completion_dates(db)
        today = date.today()

        if self.periodicity == "daily":
            period = today
        else:
            period = self._week_start(today)

        return not self._period_has_completion(completion_dates, period, self.periodicity)

    def __repr__(self):
        return f"<Habit {self.name!r} ({self.periodicity})>"
