import click

from tracker import HabitTracker
import analytics as ana


def _pick_habit(tracker, prompt="Pick a habit"):
    habits = tracker.get_all_habits()
    if not habits:
        click.echo("No habits yet — create one first.")
        return None
    for h in habits:
        broken = "BROKEN" if h.is_broken(tracker.db) else "ok"
        click.echo(f"  [{h.habit_id}] {h.name} ({h.periodicity}) — streak {h.get_streak(tracker.db)}, {broken}")
    hid = click.prompt(prompt, type=int)
    return tracker.get_habit_by_id(hid)


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """Habit Tracker — keep your routines on track."""
    ctx.ensure_object(dict)
    if ctx.obj.get("tracker") is None:
        ctx.obj["tracker"] = HabitTracker()
        if ctx.obj["tracker"].load_predefined_habits():
            click.echo("(Loaded sample habits — first run only)\n")

    if ctx.invoked_subcommand is None:
        _main_menu(ctx)


def _main_menu(ctx):
    tracker = ctx.obj["tracker"]
    while True:
        click.echo("\n--- Habit Tracker ---")
        click.echo("1. Create Habit")
        click.echo("2. Complete a Habit")
        click.echo("3. View All Habits")
        click.echo("4. Analytics Menu")
        click.echo("5. Delete a Habit")
        click.echo("6. Exit")
        choice = click.prompt("Choose", type=int)

        if choice == 1:
            _create_habit(tracker)
        elif choice == 2:
            _complete_habit(tracker)
        elif choice == 3:
            _view_all(tracker)
        elif choice == 4:
            _analytics_menu(tracker)
        elif choice == 5:
            _delete_habit(tracker)
        elif choice == 6:
            click.echo("Bye!")
            break
        else:
            click.echo("That's not on the menu.")


def _create_habit(tracker):
    name = click.prompt("Habit name")
    desc = click.prompt("Description", default="")
    period = click.prompt("Periodicity (daily/weekly)", type=click.Choice(["daily", "weekly"]))
    h = tracker.create_habit(name, desc, period)
    click.echo(f"Created '{h.name}' with id {h.habit_id}")


def _complete_habit(tracker):
    h = _pick_habit(tracker, "Habit id to complete")
    if h:
        h.complete(tracker.db)
        click.echo(f"Nice — logged completion for {h.name}.")


def _view_all(tracker):
    habits = tracker.get_all_habits()
    if not habits:
        click.echo("Nothing here yet.")
        return
    click.echo("")
    for h in habits:
        streak = h.get_streak(tracker.db)
        status = "broken" if h.is_broken(tracker.db) else "on track"
        click.echo(f"  {h.name}  |  {h.periodicity}  |  streak: {streak}  |  {status}")


def _analytics_menu(tracker):
    while True:
        click.echo("\n--- Analytics ---")
        click.echo("  a. List all habits")
        click.echo("  b. Filter by periodicity")
        click.echo("  c. Longest streak (all)")
        click.echo("  d. Longest streak (one habit)")
        click.echo("  e. Back")
        sub = click.prompt("Choice", type=str).strip().lower()

        habits = tracker.get_all_habits()
        if sub == "a":
            for h in ana.get_all_habits(habits):
                click.echo(f"  - {h.name}")
        elif sub == "b":
            period = click.prompt("daily or weekly", type=click.Choice(["daily", "weekly"]))
            filtered = ana.get_habits_by_periodicity(habits, period)
            for h in filtered:
                click.echo(f"  - {h.name}")
        elif sub == "c":
            best = ana.get_longest_streak_all(habits, tracker.db)
            click.echo(f"Longest streak across all habits: {best}")
        elif sub == "d":
            h = _pick_habit(tracker)
            if h:
                s = ana.get_longest_streak_for(h, tracker.db)
                click.echo(f"{h.name}: streak {s}")
        elif sub == "e":
            break


def _delete_habit(tracker):
    h = _pick_habit(tracker, "Habit id to delete")
    if h:
        if click.confirm(f"Delete '{h.name}' and all its history?"):
            tracker.delete_habit(h.habit_id)
            click.echo("Gone.")


@cli.command()
@click.pass_context
def menu(ctx):
    """Open the interactive menu."""
    _main_menu(ctx)


if __name__ == "__main__":
    cli(obj={})
