from functools import reduce


def get_all_habits(habits):
    return list(habits)


def get_habits_by_periodicity(habits, period):
    return list(filter(lambda h: h.periodicity == period, habits))


def get_longest_streak_for(habit, db):
    return habit.get_streak(db)


def get_longest_streak_all(habits, db):
    if not habits:
        return 0
    streaks = map(lambda h: h.get_streak(db), habits)
    return reduce(max, streaks)
