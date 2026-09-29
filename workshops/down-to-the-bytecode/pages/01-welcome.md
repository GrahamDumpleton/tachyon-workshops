---
title: Welcome
requires: [verify:env-ready]
---

# Down to the bytecode

Python does not run your source. It compiles each function to
*bytecode*, a list of small instructions, `LOAD_ATTR` to fetch an
attribute, `BINARY_OP` to add or multiply, `CALL` to call, and the
interpreter executes those one at a time. A line of source is
usually a handful of them.

Written generally, each instruction is slow. `LOAD_ATTR` has to
allow for the attribute being in the instance, or the class, or a
parent of the class, or a property, or made up by `__getattr__`. So
since Python 3.11 the interpreter *specialises*. When an instruction
has run a few times, the interpreter looks at what it met, and if
the attribute was always in the instance it rewrites the
instruction in place as `LOAD_ATTR_INSTANCE_VALUE`, which checks
that the object is of the class it expects and fetches the value
directly. `BINARY_OP` on two integers becomes `BINARY_OP_ADD_INT`.
If the check ever fails, the instruction does the work the general
way that time, and after enough failures the interpreter goes back
to the general instruction and tries again.

All of this happens as the program runs and none of it shows in the
source. The profiler can show it. With `--opcodes` it records, along
with the line, which instruction was executing at each sample.

This is a fine tool for a narrow job: tuning a loop that is already
known to be where the time goes, or finding why two functions that
look alike do not run alike. For most slow programs the answer is a
better algorithm, and the line is as far down as you need to go.

## The program

{open}`gazette/scores.py` is open in the editor. For each of 2,500
readers it scores every article: `score` takes the weight the reader
gives the article's section, adds three for each of the reader's
words the article uses, and takes off a little for the article's
age. `best_for` keeps the highest. Five million calls to `score`,
each a few attribute loads and a short loop.

The program can make its articles in two ways, chosen on the command
line. With `one-class`, every article is an `Article`. With
`by-section`, each is an instance of the class for its section,
`Business`, `Sport` and six more, all subclasses of `Article` that
differ in one class attribute.

## The environment

Create the workshop's environment, which installs nothing and makes
the `python` in the terminal Python 3.15, the one with the profiler.

```{environment-create}
:id: create-env
:title: Set up the workshop environment
```

```{verify}
:id: env-ready
:label: The terminal's Python is 3.15 and has the profiler
:trigger: after:create-env
:substrate: shell
python -c "import sys, profiling.sampling; assert sys.version_info[:2] == (3, 15), sys.version; print('Python', sys.version.split()[0], 'with profiling.sampling')"
```
