"""Fixtures shared by the gazette's tests."""

import pytest

from gazette import store


@pytest.fixture
def articles():
    """The gazette's articles, as a list of dictionaries."""
    return store.load_articles()


@pytest.fixture
def db(tmp_path, articles):
    """A database holding the articles."""
    path = tmp_path / "gazette.db"
    store.build(path, articles)
    connection = store.connect(path)
    yield connection
    connection.close()
