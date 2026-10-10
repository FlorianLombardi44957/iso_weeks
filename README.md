# ISO Weeks

A small, zero-dependency Python library for working with ISO-8601 week dates: `(iso_year, week)` pairs and the conversions to and from Gregorian dates that go with them.

```python
from datetime import date
from iso_weeks import IsoWeek, week_of, weeks_in_year

w = week_of(date(2024, 1, 17))      # IsoWeek(2024, 3)
str(w)                              # '2024-W03'
w.monday                            # datetime.date(2024, 1, 15)
w.sunday                            # datetime.date(2024, 1, 21)
w.next()                            # IsoWeek(2024, 4)
w.shift(10)                         # IsoWeek(2024, 13)
w.contains(date(2024, 1, 18))       # True
IsoWeek.parse('2020-W53')           # IsoWeek(2020, 53)
weeks_in_year(2020)                 # 53
```

Exported names: `IsoWeek`, `week_of`, `from_ordinal`, `weeks_in_year`, `contains`.

## Why this exists

The ISO-8601 week calendar is the right calendar for reporting periods, sprint planning, retail 4-4-5 calendars, and any domain where "a week" is the unit of work. It is also full of traps. A year has 52 or 53 weeks. Week 1 of an ISO year is the week containing the year's first Thursday, which means 30 December 2024 belongs to ISO year 2025, week 01, and 1 January 2021 belongs to ISO year 2020, week 53.

Python's standard library computes the correct values via `datetime.date.isocalendar()`, but it returns a bare tuple and leaves you to repeat the validation and formatting boilerplate everywhere. This library wraps that machinery in a small, immutable, ordered value type so week arithmetic, parsing, formatting, and range checks live in one place.

The trade-off: `IsoWeek` stores the ISO year exactly as the standard library reports it. We do not remap a week like `2025-W01` to its dominant Gregorian year when it overlaps late December 2024. A date in late December can legitimately belong to *next* year's week 01, and a date in early January can belong to *last* year's week 52 or 53. If your reports need weeks clamped to a single Gregorian year, that is a presentation concern you should handle at display time, not a concern of this value object.

## The awkward edge

The seam between ISO years and Gregorian years is the one that bites. Concretely:

- `2024-12-30` is `2025-W01`.
- `2021-01-01` is `2020-W53`.

Both are correct under ISO-8601 and both are what this library returns. If you are grouping dates by ISO week and then labelling the group with the Gregorian year of the week's Monday, you will occasionally label December dates with the next year. That is not a bug here; it is the calendar you chose. The library exposes the ISO year on purpose so this distinction is explicit rather than hidden.

## Running the tests

```
PYTHONPATH=src python -m unittest discover -s tests
```

Python 3.8 or later. No third-party dependencies.

## Performance

The window keeps a bounded buffer, so `push` is constant time and memory does not
grow with the length of the stream. `peak` and `trough` are linear in the window
size, which is the trade that keeps `push` cheap.

