---
title: Reading the instructions
requires: [quiz:what-the-name-says]
---

# Reading the instructions

In the heatmap, every line that has samples has a small arrow at its
left edge, before the code. Click the one on line 91.

```python
        if word in article.words:
```

A panel opens under the line. Its heading gives the share of the
line's samples that were on specialised instructions, about nine
tenths here, and beneath is a row for each instruction that was
sampled, the most sampled first. A specialised instruction is
written with the general one it came from in brackets, and a badge.

- **`CONTAINS_OP_SET (CONTAINS_OP)`** has most of the samples. It
  is the `in`. The interpreter saw that the right hand side was
  always a set, and replaced the general instruction, which would
  ask the object how to test for membership, with one that goes
  straight to the set's lookup.

- **`LOAD_ATTR_INSTANCE_VALUE (LOAD_ATTR)`** is `article.words`.
  The attribute was always found in the instance, and always in an
  instance of the same class.

- **`LOAD_FAST_BORROW_LOAD_FAST_BORROW`** fetches the two local
  variables, `word` and `article`. It has no badge. It is not a
  specialised instruction but two instructions the compiler joined
  into one, and it is as quick as an instruction gets.

Now open the panel on line 90, the `for`. Its heading says nothing,
or next to nothing, was specialised. `FOR_ITER`, which fetches the
next item, has specialised forms for lists, tuples, ranges and
generators, and `reader.words` is a frozenset, so the general
instruction is what runs. Line 93 has one of each: the subtraction
is `BINARY_OP_SUBTRACT_INT`, and the `//` beside it is plain
`BINARY_OP`, since there is no specialised division.

None of this is a fault. An instruction that is not specialised
still works, a little slower, and whether that matters depends on
how much of the program's time it has. Here the loop's `FOR_ITER`
has about a tenth of it.

```{quiz}
:id: what-the-name-says
question: A line's panel shows `BINARY_OP_ADD_FLOAT (BINARY_OP)` with most of the line's samples. What has the interpreter found out about that line?
options:
  - { text: "That the line is slow and should be rewritten", explanation: "The name says what the instruction is, not that it is slow. A specialised instruction is the quick form." }
  - { text: "That both operands of the `+` have been floats each time it looked, so it replaced the general instruction with one for adding floats", correct: true }
  - { text: "That the result of the `+` is converted to a float", explanation: "Nothing is converted. The instruction was chosen because of what the operands already were." }
  - { text: "That the source says `float(a) + float(b)`", explanation: "The interpreter specialises on the values it meets as the program runs, whatever the source says about them." }
explanation: "A specialised instruction records what the interpreter has seen at that place in the code. It checks that the operands are still floats, adds them directly, and falls back to the general way if they are not."
```
