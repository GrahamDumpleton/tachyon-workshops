# Guided JupyterLab workshops for Tachyon, the sampling profiler in Python 3.15. Run `just` to list targets.

repo := "https://github.com/GrahamDumpleton/tachyon-workshops"

# The catalog names every collection in this repository, so one URL
# offers them all; each collection has an index of its own under
# collections/<name>/, with an id that never changes.
catalog_title := "Tachyon workshops"
catalog_description := "Guided JupyterLab workshops for Tachyon, the sampling profiler in Python 3.15: what a sampling profiler is and how to read one, then profiling real applications with it."

fundamentals_id := "grahamdumpleton.me/tachyon/fundamentals"
fundamentals_title := "Profiling with Tachyon"
fundamentals_description := "Guided JupyterLab workshops on Tachyon, the sampling profiler in Python 3.15: what a sample is and why sampling costs nothing, reading the table, the flame graph and the heatmap, choosing wall, CPU, GIL or exception time, threads, async code, native code and the garbage collector, bytecode, comparing two profiles, and watching a program live."

# The fundamentals collection, in the order to take it. OUTLINE.md is
# the design this list follows; `just index` writes the index in this
# order, skipping any not written yet, so the order lives here and
# nowhere else.
fundamentals := "your-first-profile sampling-or-tracing reading-a-process-from-outside reading-a-flame-graph down-to-the-line record-now-look-later waiting-or-working who-holds-the-gil the-price-of-an-exception following-the-awaits native-code-and-the-collector down-to-the-bytecode did-the-fix-work watching-it-live"

applications_id := "grahamdumpleton.me/tachyon/applications"
applications_title := "Tachyon on real applications"
applications_description := "Guided JupyterLab workshops that point Tachyon at the programs people run: a Flask application under load, a slow endpoint found and fixed, an async service that stalls, worker processes, a test suite, attaching to a process that is already running, and a profile carried from production to your desk."

# The applications collection, in the order to take it.
applications := "a-flask-application-under-load the-slow-endpoint an-async-service-that-stalls workers-and-subprocesses profiling-a-test-suite attaching-to-a-running-process a-profile-from-production"

# The image the workshops are written, tested and run in on a machine
# that cannot run the profiler itself (macOS, without root); see
# container/Dockerfile and the "Run in a container" section of the README.
image := "tachyon-workshops:dev"

# List available targets.
default:
    @just --list

# Set up the environment: sync uv, fetch the reference checkout, download the self-test browser, link the authoring skill.
install:
    uv sync
    git submodule update --init
    uv run playwright install chromium
    just skill

# The skill ships inside the jupyterlab-workshop package. Linking it into
# .claude/skills lets Claude Code load it without a copy in this repository,
# and it tracks the pinned release; rerun after bumping the version.
# Link the authoring skill from the installed package into .claude/skills.
skill:
    #!/usr/bin/env bash
    set -euo pipefail
    target=$(uv run python -c 'import jupyterlab_workshop, pathlib; print(pathlib.Path(jupyterlab_workshop.__file__).parent / "skills" / "jupyterlab-workshop-authoring")')
    mkdir -p .claude/skills
    ln -sfn "$target" .claude/skills/jupyterlab-workshop-authoring
    echo "Linked .claude/skills/jupyterlab-workshop-authoring -> $target"

# JupyterLab must run from this directory: the extension lists workshops/
# as installed, and the MCP live tools open workshops by paths relative
# to this root, such as workshops/<name>. On macOS the profiler cannot
# read another process without root, so the workshops will not run
# here; use `just container-lab` instead.
# Start JupyterLab from the checkout, listing the workshops in each collection's order.
lab *ARGS:
    uv run jupyter lab --config=jupyter_lab_config.py {{ARGS}}

# Scaffold a new workshop under workshops/; extra args go to `jupyter workshop init`.
new NAME *ARGS:
    uv run jupyter workshop init workshops/{{NAME}} {{ARGS}}

# Lint the catalog, every collection index and every workshop, or only the workshops named.
lint *NAMES:
    #!/usr/bin/env bash
    set -euo pipefail
    shopt -s nullglob
    names=({{NAMES}})
    if [ ${#names[@]} -eq 0 ]; then
        if [ -f catalog.json ]; then
            uv run jupyter workshop lint catalog.json
        fi
        for index in collections/*/collection.json; do
            uv run jupyter workshop lint "$index"
        done
        dirs=(workshops/*/)
    else
        dirs=("${names[@]/#/workshops/}")
    fi
    if [ ${#dirs[@]} -eq 0 ]; then
        echo "No workshops under workshops/ yet"
        exit 0
    fi
    for dir in "${dirs[@]}"; do
        echo "== $dir"
        uv run jupyter workshop lint "$dir"
    done

# Render one workshop as HTML to check what a page looks like; extra args go to `jupyter workshop render`.
render NAME *ARGS:
    uv run jupyter workshop render workshops/{{NAME}} {{ARGS}}

# The self-test runs the workshop's actions and checks for real, as you,
# on this machine; only the workshop directory is protected, by a
# temporary copy. Read the workshop first. On macOS the profiler steps
# fail for want of permission, so test in the container instead.
# Self-test one workshop in a JupyterLab of its own; extra args go to `jupyter workshop test`.
test NAME *ARGS:
    uv run jupyter workshop test workshops/{{NAME}} {{ARGS}}

# Self-test every workshop, writing a JUnit report for each.
test-all:
    #!/usr/bin/env bash
    set -euo pipefail
    shopt -s nullglob
    for dir in workshops/*/; do
        name=$(basename "$dir")
        echo "== $dir"
        uv run jupyter workshop test "$dir" --junit "results-$name.xml"
    done

# Write or refresh every collection index and the catalog.
index: index-fundamentals index-applications catalog

# The workshop directories are named one by one, in the collection's
# order, which is how `jupyter workshop index` is told the order to
# write; naming only the directories that exist lets the index be
# refreshed while the collection is still being written. The repository
# URL is given explicitly so the index does not depend on a git remote
# being configured in the checkout.
# Write or refresh collections/fundamentals/collection.json in the collection's order.
index-fundamentals:
    #!/usr/bin/env bash
    set -euo pipefail
    dirs=()
    for name in {{fundamentals}}; do
        if [ -d "workshops/$name" ]; then
            dirs+=("workshops/$name")
        fi
    done
    if [ ${#dirs[@]} -eq 0 ]; then
        echo "No fundamentals workshops under workshops/ yet; collections/fundamentals/collection.json is left as it is"
        exit 0
    fi
    mkdir -p collections/fundamentals
    uv run jupyter workshop index "${dirs[@]}" --root . --out collections/fundamentals/collection.json --repo "{{repo}}" --id "{{fundamentals_id}}" --title "{{fundamentals_title}}" --description "{{fundamentals_description}}" --homepage "{{repo}}" --tag python --tag tachyon --tag profiling --ordered

# Write or refresh collections/applications/collection.json in the collection's order.
index-applications:
    #!/usr/bin/env bash
    set -euo pipefail
    dirs=()
    for name in {{applications}}; do
        if [ -d "workshops/$name" ]; then
            dirs+=("workshops/$name")
        fi
    done
    if [ ${#dirs[@]} -eq 0 ]; then
        echo "No applications workshops under workshops/ yet; collections/applications/collection.json is left as it is"
        exit 0
    fi
    mkdir -p collections/applications
    uv run jupyter workshop index "${dirs[@]}" --root . --out collections/applications/collection.json --repo "{{repo}}" --id "{{applications_id}}" --title "{{applications_title}}" --description "{{applications_description}}" --homepage "{{repo}}" --tag python --tag tachyon --tag profiling --tag web --ordered

# Write or refresh catalog.json from the collection indexes, recorded by relative path.
catalog:
    uv run jupyter workshop catalog catalog.json collections/*/collection.json --relative --title "{{catalog_title}}" --description "{{catalog_description}}" --homepage "{{repo}}"

# Binder installs from binder/requirements.txt, so it is the locked
# runtime set (no dev group) exported from uv.lock, and is regenerated
# whenever the lock changes. The container image installs the same file.
# Relock and export the runtime dependencies to binder/requirements.txt.
requirements:
    uv lock
    uv export --no-dev --no-hashes --no-annotate -o binder/requirements.txt

# The extension's reference checkout is what agents read for the workshop
# format beyond the skill (docs/, examples/ and the source), so it is
# kept at the tag of the pinned release and moves with the pin.
# Pin a new jupyterlab-workshop release, relock, export, relink the skill and move the reference checkout.
bump VERSION:
    uv add "jupyterlab-workshop=={{VERSION}}"
    just requirements
    just skill
    git -C reference/jupyterlab-workshop fetch --tags
    git -C reference/jupyterlab-workshop checkout "{{VERSION}}"
    git add reference/jupyterlab-workshop

# The profiler reads another process's memory, which macOS refuses
# without root or a debugger entitlement, so on a Mac the workshops are
# written and tested inside a Linux container built from
# container/Dockerfile: Python 3.15, JupyterLab, the pinned extension,
# the self-test browser, and a non-root user. The checkout is mounted
# into it, so files written there land in this directory as they would
# from a local JupyterLab.
# Build the container image the workshops are run and tested in.
container-build:
    docker build -t {{image}} -f container/Dockerfile .

# Start JupyterLab in the container on http://127.0.0.1:8888/lab?token=tachyon with this checkout mounted.
container-lab *ARGS:
    docker run --rm -it -p 127.0.0.1:8888:8888 -e JUPYTER_TOKEN=tachyon -v "$PWD":/home/learner/tachyon-workshops {{image}} {{ARGS}}

# Self-test one workshop inside the container; extra args go to `jupyter workshop test`.
container-test NAME *ARGS:
    docker run --rm -v "$PWD":/home/learner/tachyon-workshops {{image}} jupyter workshop test workshops/{{NAME}} {{ARGS}}

# Lint everything inside the container, as `just lint` does here.
container-lint:
    docker run --rm -v "$PWD":/home/learner/tachyon-workshops {{image}} bash -c 'set -e; jupyter workshop lint catalog.json; for i in collections/*/collection.json; do jupyter workshop lint "$i"; done; for w in workshops/*/; do echo "== $w"; jupyter workshop lint "$w"; done'

# Open a shell in the container, for trying the profiler by hand.
container-shell:
    docker run --rm -it -v "$PWD":/home/learner/tachyon-workshops {{image}} bash

# A workshop's kernelspec is registered for the user, outside the
# checkout, so removing the environment directory leaves a kernel in
# the launcher that points at a Python that no longer exists. The prune
# unregisters only the workshop kernelspecs whose environment is gone.
# Remove what opening, running and publishing the workshops leaves behind, and the kernelspecs left pointing at removed environments.
clean:
    rm -rf workshops/*/_workshop workshops/*/work workshops/*/dist workshops/*/scratch
    rm -f results-*.xml
    find . -type d -name .ipynb_checkpoints -not -path "./.venv/*" -exec rm -rf {} +
    find . -type d -name __pycache__ -not -path "./.venv/*" -not -path "./scratch/*" -exec rm -rf {} +
    uv run jupyter workshop kernels --prune

# Also remove the environment and the skill link; run `just install` afterwards.
distclean: clean
    rm -rf .venv .claude/skills/jupyterlab-workshop-authoring
    git submodule deinit -f reference/jupyterlab-workshop
