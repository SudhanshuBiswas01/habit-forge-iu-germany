<div align="center">

# Habit Forge

**Build habits. Track streaks. Actually stick to it.**

A command-line habit tracker built for **IU Germany** — object-oriented design meets functional analytics in plain Python.

[![Python](https://img.shields.io/badge/Python-3.7%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Click](https://img.shields.io/badge/CLI-Click-000000?style=for-the-badge)](https://click.palletsprojects.com/)
[![pytest](https://img.shields.io/badge/Tests-pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)](https://pytest.org/)
[![Portfolio](https://img.shields.io/badge/Type-Academic%20Project-purple?style=for-the-badge)]()
[![IU](https://img.shields.io/badge/IU-Germany-E30613?style=for-the-badge)](https://www.iu.org/)

[![Repo](https://img.shields.io/badge/GitHub-habit--forge--iu--germany-181717?style=flat-square&logo=github)](https://github.com/SudhanshuBiswas01/habit-forge-iu-germany)
[![Status](https://img.shields.io/badge/Status-Portfolio%20Project-blue?style=flat-square)]()
[![OOP](https://img.shields.io/badge/Paradigm-OOP%20%2B%20Functional-orange?style=flat-square)]()
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=flat-square)]()

[Features](#-features) · [Demo](#-demo-screenshots) · [HLD](#-high-level-design-hld) · [Install](#-installation) · [Usage](#-usage) · [Tests](#-testing) · [Structure](#-project-structure) · [Author](#-author)

</div>

---

## About

**Habit Forge** is a terminal-based habit tracker where you create daily or weekly habits, log completions, and watch your streaks grow (or crumble). No web server, no ORM — just Python, SQLite, and a Click-powered menu.

Built as a **5th semester elective** (2025/26) at IU Germany: *Object Oriented and Functional Programming with Python*.

**Dependencies:** `click`, `pytest` — SQLite is in the Python standard library.


---

## Features

| Feature | Description |
|---------|-------------|
| **Daily & weekly habits** | Two periodicities, different streak rules per type |
| **Streak engine** | Consecutive calendar days (daily) or Mon–Sun weeks (weekly) |
| **Broken detection** | See at a glance if you missed the current period |
| **Functional analytics** | `filter`, `map`, `reduce` — no classes in `analytics.py` |
| **Sample data** | 5 preloaded habits + ~4 weeks of realistic history on first run |
| **SQLite persistence** | Lightweight `habits.db`, created automatically |

---

## Tech stack

`Python` · `SQLite3` · `Click` · `pytest` · `datetime` · `functools`

---

## Demo (screenshots)

Step-by-step walkthrough of the CLI and tests.

### Step 1 — Run the CLI (`python cli.py`)

Main menu on first launch (sample habits load automatically):

![Main menu](screenshots/01-main-menu.png)

---

### Step 2 — Create a habit

Choose **1**, enter name, description, and periodicity. The habit is saved to SQLite:

![Create habit](screenshots/02-create-habit.png)

---

### Step 3 — View all habits

Choose **3** to see every habit with **streak** and **on track / broken** status:

![View all habits with streaks](screenshots/03-view-all-habits.png)

---

### Step 4 — Analytics menu

Choose **4** from the main menu.

**4a — Longest streak (all habits)** — option `c`:

![Analytics — longest streak](screenshots/04-analytics-longest-streak.png)

**4b — Filter by periodicity** — option `b`, then `daily`:

![Analytics — filter daily habits](screenshots/05-analytics-filter-daily.png)

---

### Step 5 — Run tests (`pytest -v`)

All unit tests pass (in-memory DB — your `habits.db` is not used):

![pytest results](screenshots/06-pytest.png)

---

## High-Level Design (HLD)

Architecture overview — layers, classes, database, and main flows (Mermaid).

### System context

```mermaid
flowchart LR
    User([User])
    CLI[cli.py\nClick menu]
    App[tracker.py\nHabitTracker]
    Model[habit.py\nHabit]
    DB[(habits.db\nSQLite)]
    Analytics[analytics.py\npure functions]
    Seed[preload.py\nsample data]

    User --> CLI
    CLI --> App
    CLI --> Analytics
    App --> Model
    App --> DB
    Model --> DB
    Analytics --> Model
    Analytics --> DB
    App --> Seed
    Seed --> DB
```

Single-user CLI. No network. Analytics uses `filter` / `map` / `reduce` — no classes in `analytics.py`.

### Layered architecture

```mermaid
flowchart TB
    subgraph presentation [Presentation]
        CLI[cli.py]
    end

    subgraph application [Application]
        TR[tracker.py]
        PL[preload.py]
    end

    subgraph domain [Domain - OOP]
        H[habit.py - Habit]
    end

    subgraph functional [Functional]
        AN[analytics.py]
    end

    subgraph persistence [Persistence]
        DB[db.py - Database]
        SQL[(habits.db)]
    end

    CLI --> TR
    CLI --> AN
    TR --> H
    TR --> DB
    TR --> PL
    PL --> DB
    H --> DB
    AN --> H
    DB --> SQL
```

| Layer | Module | Responsibility |
|-------|--------|----------------|
| Presentation | `cli.py` | Menus, user input, output |
| Application | `tracker.py` | Create / delete / complete habits |
| Application | `preload.py` | Seed sample data (empty DB only) |
| Domain | `habit.py` | Habit entity, streak & broken logic |
| Functional | `analytics.py` | Filter / map / reduce over habits |
| Persistence | `db.py` | SQLite CRUD |

### Class diagram (OOP)

```mermaid
classDiagram
    class Habit {
        +int habit_id
        +str name
        +str description
        +str periodicity
        +datetime created_at
        +complete(db)
        +get_streak(db) int
        +is_broken(db) bool
        +get_completions(db) list
    }

    class Database {
        +str db_path
        +Connection conn
        +connect()
        +save_habit(habit) int
        +delete_habit(habit_id)
        +load_all_habits() list
        +save_completion(habit_id, dt)
        +load_completions(habit_id) list
        +is_empty() bool
    }

    class HabitTracker {
        +Database db
        +create_habit(name, desc, period) Habit
        +delete_habit(habit_id)
        +complete_habit(habit_id)
        +get_all_habits() list
        +load_predefined_habits() bool
    }

    HabitTracker --> Database : uses
    Habit --> Database : completions
    HabitTracker ..> Habit : creates
    Database ..> Habit : loads
```

### Database schema

```mermaid
erDiagram
    HABITS ||--o{ COMPLETIONS : has

    HABITS {
        int habit_id PK
        text name
        text description
        text periodicity
        text created_at
    }

    COMPLETIONS {
        int completion_id PK
        int habit_id FK
        text completed_at
    }
```

Datetimes stored as **ISO 8601** text in SQLite.

### Flow — complete a habit

```mermaid
sequenceDiagram
    actor U as User
    participant C as cli.py
    participant T as HabitTracker
    participant H as Habit
    participant D as Database

    U->>C: Choose 2
    C->>T: get_all_habits()
    T->>D: load_all_habits()
    D-->>T: habits
    U->>C: habit_id
    C->>T: complete_habit(id)
    T->>H: complete(db)
    H->>D: save_completion(id, now)
```

### Flow — analytics (longest streak)

```mermaid
sequenceDiagram
    actor U as User
    participant C as cli.py
    participant T as HabitTracker
    participant A as analytics.py
    participant H as Habit
    participant D as Database

    U->>C: Analytics option c
    C->>T: get_all_habits()
    T->>D: load_all_habits()
    C->>A: get_longest_streak_all(habits, db)
    loop each habit
        A->>H: get_streak(db)
        H->>D: load_completions()
    end
    A-->>C: max streak
```

### Streak logic

```mermaid
flowchart TD
    Start([get_streak]) --> Load[Load completions]
    Load --> Empty{Any?}
    Empty -->|No| Zero[Return 0]
    Empty -->|Yes| Period[Find start period]
    Period --> Walk[Walk backward by period]
    Walk --> Done{Has completion?}
    Done -->|Yes| Inc[streak++]
    Inc --> Walk
    Done -->|No| Ret[Return streak]
```

| Periodicity | One period |
|-------------|------------|
| `daily` | Calendar day |
| `weekly` | Monday – Sunday |

### Design decisions

| Decision | Why |
|----------|-----|
| SQLite + raw SQL | Simple, no ORM |
| `Habit` owns streak logic | Domain stays on the entity |
| Separate `analytics.py` | OOP vs functional split for the course |
| `preload.py` isolated | Easy reset / demo data |
| Click CLI | Clean menus, less boilerplate |

---

## Installation

**Requirements:** Python 3.7+, pip

```bash
git clone https://github.com/SudhanshuBiswas01/habit-forge-iu-germany.git
cd habit-forge-iu-germany
pip install -r requirements.txt
python cli.py
```

> **Quick start:** clone → install → run `python cli.py`. Sample habits load automatically on first launch.

---

## Usage

Start the interactive CLI from the project root:

```bash
python cli.py
```

### Main menu

```
--- Habit Tracker ---
1. Create Habit
2. Complete a Habit
3. View All Habits
4. Analytics Menu
5. Delete a Habit
6. Exit
```

**Analytics submenu** — list all habits, filter by periodicity, longest streak (all habits or pick one).

Example habit line when viewing all:

```
Morning Workout  |  daily  |  streak: 12  |  on track
```

### First run

If the database is empty, the app seeds **5 sample habits** with about **4 weeks** of completion history:

| Habit | Period |
|-------|--------|
| Drink 2L of Water | daily |
| Morning Workout | daily |
| Read 20 Pages | daily |
| Weekly Review | weekly |
| Grocery Shopping | weekly |

### Reset / reseed

```bash
# delete the db, then run again
rm habits.db        # macOS / Linux
del habits.db       # Windows

python cli.py
```

Preload only runs when there are **zero** habits in the database.

---

## Testing

```bash
pytest -v
```

Tests use an **in-memory SQLite** database — your real `habits.db` is never touched.

```
tests/
├── test_habit.py       # model, completions, streaks, is_broken
└── test_analytics.py   # filter / map / reduce helpers
```

---

## Project structure

```
habit-forge-iu-germany/    # repo root (after git clone)
├── habit.py          # Habit class — streaks, completions, broken check
├── db.py             # Database — SQLite CRUD
├── tracker.py        # HabitTracker — create, complete, delete, preload
├── analytics.py      # Pure functions only (functional programming)
├── cli.py            # Click CLI — entry point
├── preload.py        # Seeds 5 habits + dummy history
├── tests/
│   ├── conftest.py
│   ├── test_habit.py
│   └── test_analytics.py
├── screenshots/      # CLI & pytest demo images
├── habits.db         # generated at runtime (gitignored)
├── requirements.txt
└── README.md
```

### How streaks work

- **Daily** — each calendar day is one period; need ≥1 completion that day.
- **Weekly** — each Monday–Sunday week is one period.
- **Streak** — count of consecutive periods (going backward) with at least one completion.
- **Current period empty?** — streak is calculated from the last completed period, not from today.

---

## Tags

Topics for this repo (GitHub **Settings → Topics**):

```
python habit-tracker cli sqlite click pytest
object-oriented-programming functional-programming
iu-germany portfolio-project terminal-app streak-tracker
```

---

## Author

**Sudhanshu Biswas** · [GitHub](https://github.com/SudhanshuBiswas01)  
IU International University of Applied Sciences — OOP & Functional Programming (Python)

[![GitHub](https://img.shields.io/badge/@SudhanshuBiswas01-181717?style=flat-square&logo=github)](https://github.com/SudhanshuBiswas01)

---

<div align="center">

*Small habits compound. This app just counts them.*

</div>
