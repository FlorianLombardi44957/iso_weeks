import datetime as dt
import unittest

from iso_weeks import (
    IsoWeek,
    week_of,
    from_ordinal,
    weeks_in_year,
    contains,
)


class TestWeeksInYear(unittest.TestCase):

    def test_known_53_week_years(self):
        # Years whose 1 January is a Thursday, or which are leap years
        # whose 1 January is a Wednesday, have 53 ISO weeks.
        self.assertEqual(weeks_in_year(2020), 53)
        self.assertEqual(weeks_in_year(2015), 53)
        self.assertEqual(weeks_in_year(2009), 53)
        self.assertEqual(weeks_in_year(2004), 53)

    def test_known_52_week_years(self):
        self.assertEqual(weeks_in_year(2021), 52)
        self.assertEqual(weeks_in_year(2022), 52)
        self.assertEqual(weeks_in_year(2010), 52)
        self.assertEqual(weeks_in_year(2042), 52)

    def test_every_year_in_a_window_is_52_or_53(self):
        for y in range(2000, 2101):
            n = weeks_in_year(y)
            self.assertIn(n, (52, 53), f"year {y}")

    def test_rejects_bad_types_and_ranges(self):
        with self.assertRaises(TypeError):
            weeks_in_year("2024")  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            weeks_in_year(True)  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            weeks_in_year(0)
        with self.assertRaises(ValueError):
            weeks_in_year(10000)


class TestIsoWeekConstruction(unittest.TestCase):

    def test_valid_pair(self):
        w = IsoWeek(2024, 7)
        self.assertEqual(w.year, 2024)
        self.assertEqual(w.week, 7)

    def test_week_zero_rejected(self):
        with self.assertRaises(ValueError):
            IsoWeek(2024, 0)

    def test_week_53_rejected_in_52_week_year(self):
        with self.assertRaises(ValueError):
            IsoWeek(2022, 53)  # 2022 has 52 weeks

    def test_week_53_allowed_in_53_week_year(self):
        w = IsoWeek(2020, 53)
        self.assertEqual((w.year, w.week), (2020, 53))

    def test_week_too_high_rejected(self):
        with self.assertRaises(ValueError):
            IsoWeek(2020, 54)  # even 53-week years stop at 53

    def test_year_out_of_range(self):
        with self.assertRaises(ValueError):
            IsoWeek(0, 1)
        with self.assertRaises(ValueError):
            IsoWeek(10000, 1)

    def test_bad_types_rejected(self):
        with self.assertRaises(TypeError):
            IsoWeek("2024", 1)  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            IsoWeek(2024, 1.0)  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            IsoWeek(True, 1)  # type: ignore[arg-type]


class TestStrAndRepr(unittest.TestCase):

    def test_str_format(self):
        self.assertEqual(str(IsoWeek(2024, 3)), "2024-W03")
        self.assertEqual(str(IsoWeek(2020, 53)), "2020-W53")

    def test_repr(self):
        self.assertEqual(repr(IsoWeek(2024, 3)), "IsoWeek(2024, 3)")


class TestOrderingAndEquality(unittest.TestCase):

    def test_equality(self):
        self.assertEqual(IsoWeek(2024, 3), IsoWeek(2024, 3))
        self.assertNotEqual(IsoWeek(2024, 3), IsoWeek(2024, 4))

    def test_ordering(self):
        self.assertLess(IsoWeek(2024, 3), IsoWeek(2024, 4))
        self.assertLess(IsoWeek(2023, 52), IsoWeek(2024, 1))
        self.assertGreater(IsoWeek(2024, 1), IsoWeek(2023, 52))

    def test_hashable(self):
        self.assertEqual(hash(IsoWeek(2024, 3)), hash(IsoWeek(2024, 3)))
        d = {IsoWeek(2024, 3): "x"}
        self.assertEqual(d[IsoWeek(2024, 3)], "x")

    def test_iterable(self):
        y, w = IsoWeek(2024, 3)
        self.assertEqual((y, w), (2024, 3))

    def test_to_tuple(self):
        self.assertEqual(IsoWeek(2024, 3).to_tuple(), (2024, 3))


class TestDateAccess(unittest.TestCase):

    def test_monday_and_sunday(self):
        w = IsoWeek(2024, 3)
        self.assertEqual(w.monday, dt.date(2024, 1, 15))
        self.assertEqual(w.sunday, dt.date(2024, 1, 21))

    def test_day(self):
        w = IsoWeek(2024, 3)
        self.assertEqual(w.day(1), dt.date(2024, 1, 15))
        self.assertEqual(w.day(4), dt.date(2024, 1, 18))
        self.assertEqual(w.day(7), dt.date(2024, 1, 21))

    def test_day_out_of_range(self):
        with self.assertRaises(ValueError):
            IsoWeek(2024, 3).day(0)
        with self.assertRaises(ValueError):
            IsoWeek(2024, 3).day(8)
        with self.assertRaises(TypeError):
            IsoWeek(2024, 3).day(3.0)  # type: ignore[arg-type]

    def test_days_list_has_seven_entries_mon_to_sun(self):
        w = IsoWeek(2024, 3)
        days = w.days()
        self.assertEqual(len(days), 7)
        self.assertEqual(days[0], dt.date(2024, 1, 15))
        self.assertEqual(days[-1], dt.date(2024, 1, 21))
        self.assertEqual([d.weekday() for d in days], [0, 1, 2, 3, 4, 5, 6])

    def test_leap_week_monday(self):
        # 2020-W53 exists and its Monday is 2020-12-28.
        w = IsoWeek(2020, 53)
        self.assertEqual(w.monday, dt.date(2020, 12, 28))
        self.assertEqual(w.sunday, dt.date(2021, 1, 3))


class TestFromDate(unittest.TestCase):

    def test_midweek_date(self):
        self.assertEqual(IsoWeek.from_date(dt.date(2024, 1, 17)), IsoWeek(2024, 3))

    def test_late_december_belongs_to_next_year_week_1(self):
        # 2024-12-30 is a Monday and is in ISO 2025-W01.
        self.assertEqual(IsoWeek.from_date(dt.date(2024, 12, 30)), IsoWeek(2025, 1))

    def test_early_january_belongs_to_previous_year(self):
        # 2021-01-01 is a Friday and is in ISO 2020-W53.
        self.assertEqual(IsoWeek.from_date(dt.date(2021, 1, 1)), IsoWeek(2020, 53))

    def test_accepts_datetime(self):
        # datetime is a subclass of date; we accept it and use its date part.
        self.assertEqual(
            IsoWeek.from_date(dt.datetime(2024, 1, 17, 12, 0, 0)),
            IsoWeek(2024, 3),
        )

    def test_rejects_non_date(self):
        with self.assertRaises(TypeError):
            IsoWeek.from_date("2024-01-17")  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            IsoWeek.from_date(20240117)  # type: ignore[arg-type]

    def test_round_trip_via_monday(self):
        for y in range(2010, 2030):
            for w in range(1, weeks_in_year(y) + 1):
                iw = IsoWeek(y, w)
                self.assertEqual(IsoWeek.from_date(iw.monday), iw)
                self.assertEqual(IsoWeek.from_date(iw.sunday), iw)


class TestParse(unittest.TestCase):

    def test_extended_form(self):
        self.assertEqual(IsoWeek.parse("2024-W03"), IsoWeek(2024, 3))
        self.assertEqual(IsoWeek.parse(" 2024-W03 "), IsoWeek(2024, 3))

    def test_compact_form(self):
        self.assertEqual(IsoWeek.parse("2024W03"), IsoWeek(2024, 3))

    def test_leap_week_string(self):
        self.assertEqual(IsoWeek.parse("2020-W53"), IsoWeek(2020, 53))

    def test_rejects_three_digit_week(self):
        with self.assertRaises(ValueError):
            IsoWeek.parse("2024-W003")

    def test_rejects_zero_week(self):
        with self.assertRaises(ValueError):
            IsoWeek.parse("2024-W00")

    def test_rejects_overlong_year(self):
        with self.assertRaises(ValueError):
            IsoWeek.parse("20240-W03")

    def test_rejects_missing_w_prefix(self):
        with self.assertRaises(ValueError):
            IsoWeek.parse("2024-03")

    def test_rejects_extra_pieces(self):
        with self.assertRaises(ValueError):
            IsoWeek.parse("2024-W03-extra")

    def test_rejects_non_string(self):
        with self.assertRaises(TypeError):
            IsoWeek.parse(2024)  # type: ignore[arg-type]


class TestArithmetic(unittest.TestCase):

    def test_next_within_year(self):
        self.assertEqual(IsoWeek(2024, 3).next(), IsoWeek(2024, 4))

    def test_next_across_year_seam_52(self):
        self.assertEqual(IsoWeek(2022, 52).next(), IsoWeek(2023, 1))

    def test_next_across_year_seam_53(self):
        self.assertEqual(IsoWeek(2020, 53).next(), IsoWeek(2021, 1))

    def test_previous_within_year(self):
        self.assertEqual(IsoWeek(2024, 3).previous(), IsoWeek(2024, 2))

    def test_previous_across_year_seam_52(self):
        self.assertEqual(IsoWeek(2023, 1).previous(), IsoWeek(2022, 52))

    def test_previous_across_year_seam_53(self):
        self.assertEqual(IsoWeek(2021, 1).previous(), IsoWeek(2020, 53))

    def test_shift_zero_is_identity(self):
        w = IsoWeek(2024, 7)
        self.assertEqual(w.shift(0), w)

    def test_shift_positive(self):
        self.assertEqual(IsoWeek(2024, 1).shift(2), IsoWeek(2024, 3))

    def test_shift_negative(self):
        self.assertEqual(IsoWeek(2024, 3).shift(-2), IsoWeek(2024, 1))

    def test_shift_across_year_seam(self):
        self.assertEqual(IsoWeek(2022, 52).shift(1), IsoWeek(2023, 1))
        self.assertEqual(IsoWeek(2023, 1).shift(-1), IsoWeek(2022, 52))

    def test_shift_across_leap_week_seam(self):
        self.assertEqual(IsoWeek(2020, 53).shift(1), IsoWeek(2021, 1))
        self.assertEqual(IsoWeek(2021, 1).shift(-1), IsoWeek(2020, 53))

    def test_shift_large(self):
        self.assertEqual(IsoWeek(2024, 3).shift(52 * 2 + 5), IsoWeek(2026, 8))

    def test_shift_rejects_non_int(self):
        with self.assertRaises(TypeError):
            IsoWeek(2024, 3).shift(1.0)  # type: ignore[arg-type]


class TestContains(unittest.TestCase):

    def test_method_inside(self):
        w = IsoWeek(2024, 3)
        self.assertTrue(w.contains(dt.date(2024, 1, 15)))
        self.assertTrue(w.contains(dt.date(2024, 1, 21)))

    def test_method_outside(self):
        w = IsoWeek(2024, 3)
        self.assertFalse(w.contains(dt.date(2024, 1, 14)))
        self.assertFalse(w.contains(dt.date(2024, 1, 22)))

    def test_free_function(self):
        w = IsoWeek(2024, 3)
        self.assertTrue(contains(w, dt.date(2024, 1, 18)))
        self.assertFalse(contains(w, dt.date(2024, 1, 22)))


class TestModuleAliases(unittest.TestCase):

    def test_week_of_alias(self):
        self.assertEqual(week_of(dt.date(2024, 1, 17)), IsoWeek(2024, 3))

    def test_from_ordinal_alias(self):
        self.assertEqual(from_ordinal(2024, 3), IsoWeek(2024, 3))

    def test_from_ordinal_validates(self):
        with self.assertRaises(ValueError):
            from_ordinal(2022, 53)


class TestKnownAwkwardCases(unittest.TestCase):

    def test_2024_12_30_is_2025_w01(self):
        # The classic late-December surprise.
        self.assertEqual(IsoWeek.from_date(dt.date(2024, 12, 30)), IsoWeek(2025, 1))

    def test_2021_01_01_is_2020_w53(self):
        # The classic early-January surprise.
        self.assertEqual(IsoWeek.from_date(dt.date(2021, 1, 1)), IsoWeek(2020, 53))

    def test_2021_01_04_is_2021_w01(self):
        self.assertEqual(IsoWeek.from_date(dt.date(2021, 1, 4)), IsoWeek(2021, 1))

    def test_string_round_trip(self):
        for s in ["2024-W03", "2020-W53", "2025-W01", "2022-W52"]:
            self.assertEqual(str(IsoWeek.parse(s)), s)


if __name__ == "__main__":
    unittest.main()
