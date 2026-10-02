from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass

_DAYS_IN_WEEK = 7

def weeks_in_year(year: int) -> int:
    """Number of ISO-8601 weeks in *year* (52 or 53).

    A year has 53 weeks iff 1 January is a Thursday, or it is a leap
    year and 1 January is a Wednesday; otherwise it has 52 weeks.
    Python's `date.weekday()` returns 0 for Monday, so Thursday is 3
    and Wednesday is 2.
    """
    if not isinstance(year, int) or isinstance(year, bool):
        raise TypeError(f"year must be int, got {type(year).__name__}")
    if year < 1 or year > 9999:
        raise ValueError(
            f"year out of range 1..9999, got {year}"
        )
    jan1 = _dt.date(year, 1, 1)
    weekday = jan1.weekday()
    is_leap = (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
    if weekday == 3 or (is_leap and weekday == 2):
        return 53
    return 52


@dataclass(frozen=True, order=True)
class IsoWeek:
    """A single ISO-8601 week, identified by (iso_year, week).

    Immutable and totally ordered. Two IsoWeeks compare by (year, week),
    which is the same as chronological order. Equality is by value, so
    IsoWeek(2024, 1) == IsoWeek(2024, 1) holds.
    """

    year: int
    week: int

    def __post_init__(self) -> None:
        if not isinstance(self.year, int) or isinstance(self.year, bool):
            raise TypeError(f"year must be int, got {type(self.year).__name__}")
        if not isinstance(self.week, int) or isinstance(self.week, bool):
            raise TypeError(f"week must be int, got {type(self.week).__name__}")
        if self.year < 1 or self.year > 9999:
            raise ValueError(
                f"year out of range 1..9999, got {self.year}"
            )
        if self.week < 1 or self.week > weeks_in_year(self.year):
            raise ValueError(
                f"week out of range 1..{weeks_in_year(self.year)} for year {self.year}, "
                f"got {self.week}"
            )

    def __str__(self) -> str:
        return f"{self.year:04d}-W{self.week:02d}"

    def __repr__(self) -> str:
        return f"IsoWeek({self.year}, {self.week})"

    def __iter__(self):
        yield self.year
        yield self.week

    def to_tuple(self) -> tuple[int, int]:
        """Return (year, week) as a plain tuple."""
        return (self.year, self.week)

    @property
    def monday(self) -> _dt.date:
        """The Monday (day 1) of this ISO week as a `datetime.date`."""
        return _dt.date.fromisocalendar(self.year, self.week, 1)

    @property
    def sunday(self) -> _dt.date:
        """The Sunday (day 7) of this ISO week as a `datetime.date`."""
        return _dt.date.fromisocalendar(self.year, self.week, 7)

    def day(self, d: int) -> _dt.date:
        """Return the *d*-th day of this week (1=Monday .. 7=Sunday)."""
        if not isinstance(d, int) or isinstance(d, bool):
            raise TypeError(f"day must be int, got {type(d).__name__}")
        if d < 1 or d > _DAYS_IN_WEEK:
            raise ValueError(f"day out of range 1..7, got {d}")
        return _dt.date.fromisocalendar(self.year, self.week, d)

    def days(self) -> list[_dt.date]:
        """All seven dates of this week, Monday through Sunday."""
        base = self.monday
        return [base + _dt.timedelta(days=i) for i in range(_DAYS_IN_WEEK)]

    def contains(self, date: _dt.date) -> bool:
        """True iff *date* falls inside this ISO week."""
        return self.monday <= date <= self.sunday

    def next(self) -> "IsoWeek":
        """The ISO week immediately after this one."""
        max_w = weeks_in_year(self.year)
        if self.week < max_w:
            return IsoWeek(self.year, self.week + 1)
        return IsoWeek(self.year + 1, 1)

    def previous(self) -> "IsoWeek":
        """The ISO week immediately before this one."""
        if self.week > 1:
            return IsoWeek(self.year, self.week - 1)
        return IsoWeek(self.year - 1, weeks_in_year(self.year - 1))

    def shift(self, n: int) -> "IsoWeek":
        """Return the IsoWeek *n* weeks away (negative for earlier)."""
        if not isinstance(n, int) or isinstance(n, bool):
            raise TypeError(f"n must be int, got {type(n).__name__}")
        target = self.monday + _dt.timedelta(weeks=n)
        y, w, _d = target.isocalendar()
        return IsoWeek(y, w)

    @classmethod
    def from_date(cls, date: _dt.date) -> "IsoWeek":
        """The ISO week containing *date*."""
        if not isinstance(date, _dt.date):
            raise TypeError(f"date must be datetime.date, got {type(date).__name__}")
        y, w, _d = date.isocalendar()
        return cls(y, w)

    @classmethod
    def parse(cls, s: str) -> "IsoWeek":
        """Parse a strict `YYYY-Www` or `YYYYWww` ISO-8601 week string."""
        if not isinstance(s, str):
            raise TypeError(f"s must be str, got {type(s).__name__}")
        cleaned = s.strip()
        if "-" in cleaned:
            parts = cleaned.split("-")
            if len(parts) != 2 or not parts[0].isdigit() or not parts[1].startswith("W"):
                raise ValueError(f"not a YYYY-Www string: {s!r}")
            year_str, week_str = parts
            week_digits = week_str[1:]
        else:
            if "W" not in cleaned or not cleaned.startswith("W", 4):
                raise ValueError(f"not a YYYYWww string: {s!r}")
            w_idx = cleaned.index("W")
            year_str = cleaned[:w_idx]
            week_digits = cleaned[w_idx + 1:]
            if not year_str.isdigit():
                raise ValueError(f"not a YYYYWww string: {s!r}")
        if len(week_digits) != 2 or not week_digits.isdigit():
            raise ValueError(f"week must be two digits, got {s!r}")
        return cls(int(year_str), int(week_digits))


def week_of(date: _dt.date) -> IsoWeek:
    """Convenience: the ISO week containing *date* (alias of `IsoWeek.from_date`)."""
    return IsoWeek.from_date(date)


def from_ordinal(year: int, week: int) -> IsoWeek:
    """Construct an `IsoWeek` from raw (year, week) ints, validating the range."""
    return IsoWeek(year, week)


def contains(week: IsoWeek, date: _dt.date) -> bool:
    """Free-function form of `IsoWeek.contains`.

    Provided for callers who prefer a function-style API over method calls.
    """
    return week.contains(date)
