# The image the workshops are written, tested and run in on a machine
# that cannot run the profiler itself. Tachyon reads another process's
# memory, which macOS refuses without root or a debugger entitlement,
# so on a Mac the workshops run here, in a Linux container, where a
# non-root user may profile any process they start. The image is Python
# 3.15 (the release candidate until 3.15.0 is published), JupyterLab and
# the pinned extension from the same locked requirements the Binder
# image installs, the browser the self-test drives, and a few tools the
# workshops' terminals expect. The checkout is mounted at the working
# directory, so `_workshop/` state, `work/` files and profiles written
# by a workshop land in it as they would from a local JupyterLab, and
# nothing is baked in: rebuild only when the requirements change.
#
#   just container-build          build the image
#   just container-lab            JupyterLab on http://127.0.0.1:8888/?token=tachyon
#   just container-test <name>    self-test one workshop inside it
#   just container-shell          a shell, for trying the profiler by hand
#
# The published ghcr.io/grahamdumpleton/jupyterlab-workshop image is not
# the base because it runs JupyterLab on the conda Python the Jupyter
# docker-stacks ship, 3.13 at present, and every workshop's environment
# is built from the Python JupyterLab runs on; the profiler and the
# program it profiles must be the same Python 3.15.
FROM python:3.15-rc-slim

# curl for the pages that send requests to a server, procps for ps and
# pgrep on the pages about processes, git for the reference checkouts,
# and the shared libraries Chromium needs, installed by Playwright.
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl git procps ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY binder/requirements.txt /tmp/requirements.txt

# The self-test extra brings Playwright; the browser is downloaded to a
# shared location so the non-root user below can run it too, and its
# system dependencies are installed while still root.
ENV PLAYWRIGHT_BROWSERS_PATH=/opt/playwright
RUN pip install --no-cache-dir --disable-pip-version-check --root-user-action=ignore \
        -r /tmp/requirements.txt "jupyterlab-workshop[test]==0.13.0" \
    && playwright install --with-deps chromium \
    && rm -rf /var/lib/apt/lists/* /tmp/requirements.txt

# The same JupyterLab overrides the Binder image writes, as far as they
# apply here. JupyterLab starts in the workshop browser with the
# checkout's collections listed, whichever URL is opened (the launch
# link in jupyter_lab_config.py does the same only from the server
# root); HTML files open trusted in the HTML viewer, so a flame graph's
# scripts run without a click; and the Jupyter news prompt is off.
# Trust and author mode are left alone: this is an authoring image as
# much as a learner's, so nothing is forced and nothing is disabled.
RUN mkdir -p /usr/local/share/jupyter/lab/settings \
    && printf '%s\n' '{' \
        '  "@jupyterlab-workshop/labextension:panel": {' \
        '    "defaultWorkshop": "",' \
        '    "browseOnStart": true,' \
        '    "workshopsDirectory": "workshops",' \
        '    "collections": ["collections/fundamentals/collection.json", "collections/applications/collection.json"]' \
        '  },' \
        '  "@jupyterlab/htmlviewer-extension:plugin": { "trustByDefault": true },' \
        '  "@jupyterlab/apputils-extension:notification": { "fetchNews": "false" }' \
        '}' > /usr/local/share/jupyter/lab/settings/overrides.json

# A non-root user, as a learner is on Binder and in a codespace. uid
# 1000 matches the first user on most Linux desktops; Docker Desktop on
# macOS maps the mounted checkout's ownership either way.
RUN useradd --create-home --uid 1000 --shell /bin/bash learner
USER learner
# SHELL is what JupyterLab's terminals start; without it they fall back
# to /bin/sh, and the pages assume bash.
ENV HOME=/home/learner SHELL=/bin/bash
WORKDIR /home/learner/tachyon-workshops

EXPOSE 8888

# The same config the local `just lab` uses, listening on every
# interface of the container so the published port reaches it. The
# token comes from JUPYTER_TOKEN when set, which the Justfile sets to
# a fixed word so the link is the same every start. Deleting goes
# straight to deletion: the trash JupyterLab would otherwise use is a
# `.Trash-1000` directory at the root of the mounted checkout, which a
# workshop's Restart fills with a copy of everything it shipped.
# Run the container with `--init`, as the Justfile does, so processes a
# workshop leaves behind are reaped instead of lingering as zombies
# under JupyterLab.
CMD ["jupyter", "lab", "--config=jupyter_lab_config.py", "--ServerApp.ip=0.0.0.0", "--no-browser", "--FileContentsManager.delete_to_trash=False"]
