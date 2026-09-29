"""The word counts are there once the refresher has finished."""

from gazette.refresh import Refresher


def test_counts_are_there_after_a_refresh(articles):
    refresher = Refresher(articles)
    refresher.start()
    assert refresher.join(timeout=5)
    assert refresher.counts["council"] > 1000


def test_a_refresh_of_nothing(articles):
    refresher = Refresher([])
    refresher.start()
    assert refresher.join(timeout=5)
    assert refresher.counts == {}
