#!/bin/bash
# Run once when the codespace is created. Does what the Binder postBuild
# does, in the codespace: installs JupyterLab and the extension from the
# same pinned requirements the Binder image uses, fills a wheelhouse for
# the workshops' environments, and writes the JupyterLab overrides, with
# two differences, both because a codespace belongs to the person who
# created it, tied to their GitHub account, and persists, where a Binder
# session is an anonymous, temporary container. The welcome message is
# the Codespaces one. And workshops are not forced to trusted, so the
# learner is shown what a workshop asks to do and decides before it runs
# anything in their codespace.
#
# The dev container image carries no Python 3.15, and none of the
# published Python dev container images has it yet, so the interpreter
# is installed first with uv's Python installer, and a virtual
# environment with pip is made from it in the home directory to hold
# JupyterLab. Every workshop's own environment is then built from that
# interpreter, which is what the profiler needs: it and the program it
# profiles must be the same Python. The workshops themselves never use
# uv; it is only how this codespace gets its interpreter.
#
# The analytics setting is Binder's: it reports every session's
# progress events to the sink each collection index's analytics block
# names, without asking; the events say they came from a codespace.
# .devcontainer/welcome.md tells the learner that progress is reported.
# The third block trusts HTML files opened in JupyterLab's HTML viewer,
# which is how the workshops show the profiler's flame graphs and
# heatmaps; untrusted, the viewer runs none of a file's scripts and the
# graph stays blank until Trust HTML is clicked.
# The second block is JupyterLab's own: it turns off the question about
# fetching Jupyter news, which would otherwise come before the welcome
# message the first time the codespace's JupyterLab opens.
set -euo pipefail

cd "$(dirname "$0")/.."

if ! command -v uv >/dev/null 2>&1; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi

export PATH="${HOME}/.local/bin:${PATH}"

uv python install 3.15

# --seed gives the environment pip, which the workshops use to build
# their own environments and which a uv venv otherwise leaves out.
uv venv --seed --python 3.15 "${HOME}/.venv"

python="${HOME}/.venv/bin/python"

"$python" -m pip install --no-cache-dir --disable-pip-version-check -r binder/requirements.txt

# Workshops build an environment of their own on first open, installing
# their requirements and ipykernel with pip. Download every workshop's
# requirements, and ipykernel, into a wheelhouse in the home directory
# and tell pip to look there first, so the install takes its wheels
# from disk rather than PyPI. It is find-links only, never no-index:
# pip still reaches PyPI for anything the wheelhouse lacks. This is the
# same arrangement as binder/postBuild.
shopt -s nullglob

wheels="${HOME}/.wheels"

mkdir -p "$wheels"

for requirements in workshops/*/requirements.txt; do
  "$python" -m pip download --disable-pip-version-check -d "$wheels" -r "$requirements"
done

"$python" -m pip download --disable-pip-version-check -d "$wheels" ipykernel

mkdir -p "${HOME}/.config/pip"

cat > "${HOME}/.config/pip/pip.conf" <<CONF
[global]
find-links = ${wheels}
CONF

# The overrides live in JupyterLab's application settings directory. Ask
# JupyterLab for it rather than assuming the prefix. sudo covers a
# directory this user cannot write, which a venv in the home directory
# never is, but costs nothing to keep.
settings="$("$python" -c 'import os; from jupyterlab.commands import get_app_dir; print(os.path.join(get_app_dir(), "settings"))')"

overrides="$(mktemp)"

cat > "$overrides" <<'JSON'
{
  "@jupyterlab-workshop/labextension:panel": {
    "defaultWorkshop": "",
    "browseOnStart": true,
    "workshopsDirectory": "workshops",
    "collections": ["collections/fundamentals/collection.json", "collections/applications/collection.json"],
    "welcome": ".devcontainer/welcome.md",
    "disabledFeatures": [
      "open-directory",
      "open-url",
      "collections",
      "catalogs",
      "remove",
      "author"
    ],
    "analytics": { "report": "always" }
  },
  "@jupyterlab/apputils-extension:notification": {
    "fetchNews": "false"
  },
  "@jupyterlab/htmlviewer-extension:plugin": {
    "trustByDefault": true
  }
}
JSON

if mkdir -p "$settings" 2>/dev/null && [ -w "$settings" ]; then
  install -m 644 "$overrides" "$settings/overrides.json"
else
  sudo mkdir -p "$settings"
  sudo install -m 644 "$overrides" "$settings/overrides.json"
fi

rm -f "$overrides"

echo "Wrote the JupyterLab overrides to $settings/overrides.json"
