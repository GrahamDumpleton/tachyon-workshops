# The image mybinder.org builds for these workshops. repo2docker builds
# a Dockerfile under binder/ as a plain Docker build and ignores every
# other file in this directory, so this file carries what environment.yml
# and postBuild would otherwise have said. It exists because repo2docker
# refuses Python 3.15: its conda buildpack reads the version from
# environment.yml and looks for a frozen base environment it ships for
# that minor version, and it has them only up to 3.14, so any 3.15 spec
# fails before conda-forge (which has 3.15.0rc2) is asked. When
# repo2docker gains a 3.15 lock, this file can go and the conda route
# come back: environment.yml with python=3.15 and pip from
# requirements.txt, and the overrides below written by a postBuild.
#
# What Binder needs of a Dockerfile: a non-root user with uid 1000 whose
# home holds the repository, `jupyter notebook` on the PATH (BinderHub
# starts the container with that command, its own port, base URL and
# token as arguments, under the image's entrypoint), and nothing that
# assumes a particular command line. The image is Python 3.15 (the
# release candidate until 3.15.0 is published), JupyterLab, notebook and
# the pinned extension from the locked requirements `just requirements`
# exports beside this file, the same set container/Dockerfile installs
# for authoring. Every workshop's environment is built from the Python
# JupyterLab runs on, so JupyterLab itself runs on 3.15: the profiler and
# the program it profiles must be the same release.
FROM python:3.15-rc-slim

# curl for the pages that send requests to a server, procps for ps and
# pgrep on the pages about processes, and tini to reap the processes a
# workshop leaves behind, which would otherwise linger as zombies under
# JupyterLab (the authoring container runs with --init for the same
# reason).
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl procps ca-certificates tini \
    && rm -rf /var/lib/apt/lists/*

ENV NB_USER=jovyan \
    NB_UID=1000 \
    HOME=/home/jovyan \
    SHELL=/bin/bash

RUN useradd --create-home --uid ${NB_UID} --shell /bin/bash ${NB_USER}

COPY binder/requirements.txt /tmp/requirements.txt

RUN pip install --no-cache-dir --disable-pip-version-check --root-user-action=ignore \
        -r /tmp/requirements.txt \
    && rm -f /tmp/requirements.txt

# The JupyterLab overrides. JupyterLab starts in the workshop browser
# with the checkout's two collections listed as installed and ready to
# open, numbered in each collection's order, and trusts them without
# asking, since the visitor is the one who chose the link; a launch link
# naming a workshop still opens that workshop directly. The disabled
# features keep visitors to the supplied workshops: no other directories
# or URLs, no subscribing to collections or catalogs, no removing and no
# editing; Restart puts a workshop back as it started. The welcome
# message in binder/welcome.md greets the visitor once the session
# starts, with what the workshops are for and how to end the session.
#
# The analytics setting reports every session's progress events to the
# sink each collection index's analytics block names, the workshops'
# own analytics service, without asking, so it can be seen where the
# workshops are clear and where they are not. Sessions are anonymous and
# the events never carry file contents, cell output or form answers; the
# welcome message tells the visitor that progress is reported.
#
# HTML files open trusted in JupyterLab's HTML viewer, which is how the
# workshops show the profiler's flame graphs and heatmaps; untrusted,
# the viewer runs none of a file's scripts and the graph stays blank
# until Trust HTML is clicked. And the question about fetching Jupyter
# news is off, or a fresh container would put it in front of every
# visitor before the welcome message.
RUN mkdir -p /usr/local/share/jupyter/lab/settings \
    && printf '%s\n' '{' \
        '  "@jupyterlab-workshop/labextension:panel": {' \
        '    "defaultWorkshop": "",' \
        '    "browseOnStart": true,' \
        '    "workshopsDirectory": "workshops",' \
        '    "collections": ["collections/fundamentals/collection.json", "collections/applications/collection.json"],' \
        '    "welcome": "binder/welcome.md",' \
        '    "trustPolicy": { "forcedLevel": "trusted" },' \
        '    "disabledFeatures": [' \
        '      "open-directory",' \
        '      "open-url",' \
        '      "collections",' \
        '      "catalogs",' \
        '      "remove",' \
        '      "author"' \
        '    ],' \
        '    "analytics": { "report": "always" }' \
        '  },' \
        '  "@jupyterlab/apputils-extension:notification": { "fetchNews": "false" },' \
        '  "@jupyterlab/htmlviewer-extension:plugin": { "trustByDefault": true }' \
        '}' > /usr/local/share/jupyter/lab/settings/overrides.json

# The repository goes into the home directory, as repo2docker's own
# images have it, so the settings' relative paths and the launch links'
# `workshops/<name>` resolve against the server root. The root
# .dockerignore keeps the local environment, the scratch directory and
# the reference checkout out of it.
COPY --chown=${NB_UID}:${NB_UID} . ${HOME}

USER ${NB_USER}
WORKDIR ${HOME}

# Workshops build an environment of their own on first open, installing
# their requirements and ipykernel with pip. Download every workshop's
# requirements, and ipykernel, into a wheelhouse in the image and tell
# pip to look there first, so the install takes its files from disk
# rather than PyPI. It is find-links only, never no-index: pip still
# reaches PyPI for anything the wheelhouse lacks, so learners can
# install packages of their own, and a workshop whose requirements are
# not in the wheelhouse still works, only more slowly.
RUN mkdir -p ${HOME}/.wheels ${HOME}/.config/pip \
    && for requirements in workshops/*/requirements.txt; do \
        python -m pip download --disable-pip-version-check -d ${HOME}/.wheels -r "$requirements" || exit 1; \
    done \
    && python -m pip download --disable-pip-version-check -d ${HOME}/.wheels ipykernel \
    && printf '[global]\nfind-links = %s\n' "${HOME}/.wheels" > ${HOME}/.config/pip/pip.conf

EXPOSE 8888

# BinderHub supplies the command; this one is for running the image by
# hand, and takes the same overrides. Deleting goes straight to deletion
# rather than a .Trash directory a workshop's Restart would fill.
ENTRYPOINT ["tini", "--"]
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--no-browser", "--FileContentsManager.delete_to_trash=False"]
