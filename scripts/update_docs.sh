#!/bin/bash

# This script automates the generation of Sphinx documentation source files (.rst)
# for both the client and server packages, creating a hierarchical structure.
#
# Usage:
# ./scripts/update_docs.sh

set -e

# Get the absolute path of the project root directory
ROOT_DIR=$(git rev-parse --show-toplevel)

echo "Updating client documentation source..."
sphinx-apidoc -o "${ROOT_DIR}/sphinx_docs/client/source" -f "${ROOT_DIR}/packages/client/lean_runner"
# Replace the default 'modules' toctree entry with the main package name
sed -i 's/   modules/   lean_runner/' "${ROOT_DIR}/sphinx_docs/client/source/index.rst"
rm -f "${ROOT_DIR}/sphinx_docs/client/source/modules.rst"

echo "Updating server documentation source..."
sphinx-apidoc -o "${ROOT_DIR}/sphinx_docs/server/source" -f "${ROOT_DIR}/packages/server/lean_server"
# Replace the default 'modules' toctree entry with the main package name
sed -i 's/   modules/   lean_server/' "${ROOT_DIR}/sphinx_docs/server/source/index.rst"
rm -f "${ROOT_DIR}/sphinx_docs/server/source/modules.rst"

echo "✅ Sphinx documentation source files updated successfully."
echo "You can now build the HTML documentation by running:"
echo "sphinx-build -b html sphinx_docs/client/source sphinx_docs/client/build/html"
echo "sphinx-build -b html sphinx_docs/server/source sphinx_docs/server/build/html"
