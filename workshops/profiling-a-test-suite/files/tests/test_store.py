"""The database gives back what was put into it."""

import pytest

from gazette import store

SECTIONS = ["Business", "Culture", "Local", "Politics", "Science", "Sport", "Technology", "Weather"]


def test_article_by_number(db):
    found = store.article(db, 1)
    assert found["id"] == 1
    assert found["title"]


def test_article_that_is_missing(db):
    assert store.article(db, 999999) is None


def test_newest_are_in_order(db):
    found = store.newest(db)
    dates = [row["date"] for row in found]
    assert len(found) == 20
    assert dates == sorted(dates, reverse=True)


def test_newest_takes_a_count(db):
    assert len(store.newest(db, 5)) == 5


@pytest.mark.parametrize("section", SECTIONS)
def test_every_section_has_articles(db, section):
    found = store.in_section(db, section)
    assert found
    assert all(row["section"] == section for row in found)


def test_mentioning_finds_the_word(db):
    found = store.mentioning(db, "council")
    assert len(found) == 20
    assert all("council" in row["body"].lower() for row in found)


def test_mentioning_ignores_case(db):
    assert store.mentions(db, "Council") == store.mentions(db, "council")


def test_a_word_nobody_used(db):
    assert store.mentions(db, "zyzzyva") == 0
    assert store.mentioning(db, "zyzzyva") == []
