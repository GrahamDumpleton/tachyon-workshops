"""Count the words of the articles in the background.

The count takes a moment, so the gazette's pages do not wait for it.
A Refresher starts a thread to do the counting, and the counts are
there to be read once the thread has finished.
"""

import re
import threading

WORD = re.compile(r"[a-z]+")


class Refresher:
    def __init__(self, articles):
        self.articles = articles
        self.counts = {}
        self.thread = threading.Thread(target=self.count, name="refresher")

    def start(self):
        self.thread.start()

    def count(self):
        counts = {}
        for article in self.articles:
            for word in WORD.findall(article["body"].lower()):
                counts[word] = counts.get(word, 0) + 1
        self.counts = counts

    def join(self, timeout=None):
        self.thread.join(timeout)
        return not self.thread.is_alive()
