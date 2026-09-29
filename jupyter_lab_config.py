# Configuration for JupyterLab started from this checkout. Jupyter does
# not look in the current directory for config files, so this one is
# named explicitly: `just lab` passes `--config=jupyter_lab_config.py`,
# and so does the container image's command.
#
# Open the workshop browser with the checkout's collections added for
# the session, in the order to take them, and the catalog. A
# collection lists its workshops in the order to take them, numbered,
# rather than the order the workshops directory gives, and the browser
# groups the installed workshops under each collection's heading in the
# order the link names them. A collection added to this repository is
# added to the link here. They are added for the session only, kept in
# the workspace's saved state across reloads; the browser offers
# Subscribe to keep them for good.
c.LabApp.default_url = (
    "/lab?catalog=catalog.json"
    "&collection=collections/fundamentals/collection.json"
    "&collection=collections/applications/collection.json"
)
