"""Build the documentation to the docs/build directory.

Accepts the name of the release as a command-line argument.
If not specified, the name "dev" is used.

Build to the docs/build/dev directory
$ python build_docs.py

Build to the docs/build/v0.1.0 directory
$ python build_docs.py v0.1.0
"""

# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "lxml",
# ]
# ///
import os
import shutil
import sys
from pathlib import Path
from shutil import copyfile
from subprocess import run

from lxml import __version__, etree

os.chdir("docs")

# write to stderr instead of stdout because stderr is where the
# Java log messages are written to
print(f"lxml version {__version__}", file=sys.stderr)

# Check that java is available
try:
    _ = run(["java", "-version"])
except FileNotFoundError:
    sys.exit("You need java installed and available on PATH")

# Build SVG file
_ = run(
    [
        "java",
        "-jar",
        "bin/xsdvi.jar",
        "../equipment-register.xsd",
        "-useStyle",
        "styles/svg.css",
    ],
)

tag = "develop" if len(sys.argv) == 1 else sys.argv[1]
shutil.rmtree(f"build/{tag}", ignore_errors=True)
Path(f"build/{tag}/styles").mkdir(parents=True)

_ = Path("equipment-register.svg").replace(f"build/{tag}/diagram.svg")
_ = copyfile("styles/svg.css", f"build/{tag}/styles/svg.css")

# Build HTML file
xsd = etree.parse("../equipment-register.xsd")
xsl = etree.parse("styles/xs3p-msl.xsl")
transform = etree.XSLT(xsl)
result = transform(xsd)
result.write_output(f"build/{tag}/index.html")

# Update versions.json (only when running on GitHub Actions)
if os.getenv("GITHUB_ACTIONS") == "true":
    import json
    from urllib.request import urlopen, HTTPError

    owner, repo = os.environ["GITHUB_REPOSITORY"].split("/")
    version_file = "build/versions.json"
    versions: list[str] = []
    try:
        with urlopen(f"https://{owner}.github.io/{repo}/versions.json") as url:
            versions = json.load(url)
    except HTTPError:
        pass
    finally:
        if tag not in versions:
            versions.insert(1, tag)
            with open(version_file, "w") as fp:
                json.dump(versions, fp, indent=1)
            print(f"Inserted {tag!r} into {version_file}")


print(f"Saved to docs/build/{tag}")
