"""Dates are printed the way the gazette prints them."""

import pytest

from gazette import dates, store


@pytest.mark.parametrize("number", range(0, 2000, 20))
def test_printed_date_of_an_article(number):
    article = store.load_articles()[number]
    text = dates.printed(article["date"])
    day, number_of_day, month, year = text.split()
    assert day in dates.DAYS
    assert month in dates.MONTHS
    assert int(number_of_day) == int(article["date"][8:])
    assert year == article["date"][:4]


def test_issue_is_the_day_of_the_year():
    assert dates.issue("2026-01-01") == 1
    assert dates.issue("2026-12-31") == 365
