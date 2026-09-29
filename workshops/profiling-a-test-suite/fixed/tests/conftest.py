"""Fixtures shared by the gazette's tests."""

import pytest

from gazette import store


@pytest.fixture(scope="session")
def articles():
    """The gazette's articles, as a list of dictionaries."""
    return store.load_articles()


@pytest.fixture(scope="session")
def db(tmp_path_factory, articles):
    """A database holding the articles."""
    path = tmp_path_factory.mktemp("store") / "gazette.db"
    store.build(path, articles)
    connection = store.connect(path)
    yield connection
    connection.close()
