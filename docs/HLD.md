# High-Level Design (HLD) — Habit Forge

Overview of how the habit tracker is structured: layers, classes, data, and main flows.

---

## 1. System context

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

**Summary:** Single-user CLI app. No network layer. SQLite file on disk. Analytics reads habit objects and calls `get_streak()` — no shared global state in `analytics.py`.

---

## 2. Layered architecture

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
| Application | `tracker.py` | Create / delete / complete habits, orchestration |
| Application | `preload.py` | Seed 5 habits + 4 weeks of completions (empty DB only) |
| Domain | `habit.py` | Habit entity, streak & broken logic |
| Functional | `analytics.py` | Filter / map / reduce over habit lists |
| Persistence | `db.py` | SQL CRUD, ISO datetime storage |

---

## 3. Class diagram (OOP)

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
    Habit --> Database : reads/writes completions
    HabitTracker ..> Habit : creates
    Database ..> Habit : loads
```

`analytics.py` has **no classes** — only functions that accept `habits` list + `db`.

---

## 4. Database schema

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

Datetimes stored as **ISO 8601** strings in SQLite.

---

## 5. Sequence — complete a habit

```mermaid
sequenceDiagram
    actor U as User
    participant C as cli.py
    participant T as HabitTracker
    participant H as Habit
    participant D as Database

    U->>C: Choose 2 (Complete)
    C->>T: get_all_habits()
    T->>D: load_all_habits()
    D-->>T: list of Habit
    T-->>C: habits
    C->>U: show list + pick id
    U->>C: habit_id
    C->>T: complete_habit(id)
    T->>H: complete(db)
    H->>D: save_completion(id, now)
    D-->>H: ok
    C->>U: confirmation message
```

---

## 6. Sequence — view streaks (analytics)

```mermaid
sequenceDiagram
    actor U as User
    participant C as cli.py
    participant T as HabitTracker
    participant A as analytics.py
    participant H as Habit
    participant D as Database

    U->>C: Analytics → longest streak (c)
    C->>T: get_all_habits()
    T->>D: load_all_habits()
    D-->>T: habits
    C->>A: get_longest_streak_all(habits, db)
    loop each habit
        A->>H: get_streak(db)
        H->>D: load_completions()
        D-->>H: datetimes
        H-->>A: streak int
    end
    A-->>C: max streak
    C->>U: print result
```

---

## 7. Streak calculation (domain logic)

```mermaid
flowchart TD
    Start([get_streak]) --> Load[Load completion dates from DB]
    Load --> Empty{Any completions?}
    Empty -->|No| Zero[Return 0]
    Empty -->|Yes| StartPeriod[Find streak start period]
    StartPeriod --> Daily{Daily habit?}
    Daily -->|Yes| TodayDone{Completed today?}
    TodayDone -->|Yes| FromToday[Start from today]
    TodayDone -->|No| FromYesterday[Start from yesterday]
    Daily -->|No| WeekDone{Completed this week?}
    WeekDone -->|Yes| FromThisWeek[Start from this Monday]
    WeekDone -->|No| FromLastWeek[Start from last Monday]
    FromToday --> Loop
    FromYesterday --> Loop
    FromThisWeek --> Loop
    FromLastWeek --> Loop
    Loop[Walk backward period by period] --> HasDone{Completion in period?}
    HasDone -->|Yes| Inc[streak += 1]
    Inc --> Loop
    HasDone -->|No| Done[Return streak]
```

**Period rules**

| Periodicity | One period = |
|-------------|----------------|
| `daily` | One calendar day |
| `weekly` | Monday → Sunday |

---

## 8. Functional analytics (no classes)

```mermaid
flowchart LR
    Habits[list of Habit]
    Habits --> F1[get_all_habits\nidentity list]
    Habits --> F2[get_habits_by_periodicity\nfilter]
    Habits --> F3[get_longest_streak_all\nmap + reduce max]
    H1[one Habit] --> F4[get_longest_streak_for\nhabit.get_streak]
    DB[(Database)] --> F3
    DB --> F4
```

Built-ins used: `filter`, `map`, `functools.reduce`, `max`.

---

## 9. First-run bootstrap

```mermaid
flowchart TD
    Run([python cli.py]) --> Init[HabitTracker.connect]
    Init --> Empty{db.is_empty?}
    Empty -->|Yes| Seed[preload.seed_habits]
    Seed --> H5[Create 5 habits]
    H5 --> C28[Insert ~4 weeks completions]
    Empty -->|No| Menu[Show main menu]
    C28 --> Menu
```

---

## 10. Deployment view

```mermaid
flowchart TB
    subgraph local [Developer machine]
        PY[Python 3.7+]
        APP[Habit Forge CLI]
        FILE[(habits.db)]
        PY --> APP
        APP --> FILE
    end
```

No server, containers, or cloud — local CLI only.

---

## Design decisions

| Decision | Why |
|----------|-----|
| SQLite + raw SQL | Simple, no ORM, fits course scope |
| `Habit` owns streak logic | Domain behaviour stays on the entity |
| Separate `analytics.py` | Clear split: OOP domain vs functional reporting |
| `preload.py` isolated | Demo data optional, easy to reset |
| Click for CLI | Readable menus without boilerplate |

---

[← Back to README](../README.md)
