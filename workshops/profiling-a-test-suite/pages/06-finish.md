---
title: Finish
requires: [quiz:which-habit]
---

# Finish

Three habits, each of which looks harmless in the test where it is
written, and each multiplied by the number of tests.

- **A fixture made for every test** that could be made once. Look
  for it under `pytest_runtest_setup`, and give what tests only read
  a wider scope.

- **A sleep in place of a wait.** A test that sleeps is guessing.
  Wait for the thing itself: join the thread, wait on the event,
  ask the server until it answers.

- **Work repeated for every case** of a parametrised test. Move it
  to a fixture.

## Reading a test run

- Profile the whole run with `run -m pytest`, in the binary format,
  and make the pictures with `replay`.

- In the flame graph, search for `test_`. The branch under
  `pytest_runtest_call` is the tests, and the branch under
  `pytest_runtest_setup` is their fixtures.

- Use the heatmap of `conftest.py` to see which fixture, and which
  line of it.

- Without `-a` the profile is of the main thread, which is where
  pytest runs the tests. A suite that spreads its tests over
  processes needs `--subprocesses`, and gets a file for each.

It is worth doing once a release, and worth keeping the recording.
A binary recording is a few tens of kilobytes, and the next time
the suite feels slow there is something to compare it with.

```{quiz}
:id: which-habit
question: "A suite of two thousand tests takes six minutes. `--durations` shows no test slower than a fifth of a second. In the flame graph, `pytest_runtest_setup` is four fifths of the width, all of it above a fixture called `client` that starts the application. What do you try first?"
options:
  - { text: "Run the tests on several processors", explanation: "That would help, and would hide the cause. Every process would still start the application once for each of its tests." }
  - { text: "Find the slowest tests and rewrite them", explanation: "No test is slow. The time is in what is made before each one." }
  - { text: "Give `client` a wider scope, so that the application is started once and not two thousand times", correct: true }
  - { text: "Profile again with `--mode cpu`", explanation: "That would show whether starting the application computes or waits. You know already what is taking the time and how often it is done." }
explanation: "Four fifths of six minutes over two thousand tests is a seventh of a second of setup for each, which no list of slow tests would show. If the tests change what the application holds, the fixture has to put that back between tests, which is usually far cheaper than starting again."
```

Next in these workshops is **Attaching to a running process**,
which profiles a program that the profiler did not start. Press
Finish to go there.
