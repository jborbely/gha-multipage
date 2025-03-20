"""Build the documentation to the docs/build directory.

Accepts the name of the release as a command-line argument.
If not specified, the name "dev" is used.

Build docs to the docs/build/dev directory
$ python build_docs.py

Build docs to the docs/build/v0.1.0 directory
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

tag = "dev" if len(sys.argv) == 1 else sys.argv[1]
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

print(f"Docs saved to docs/build/{tag}")
