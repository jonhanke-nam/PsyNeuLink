# docs-new Makefile
# Build the modernized PsyNeuLink documentation.
#
# Usage:
#   make html          Build HTML docs into build/html/
#   make livehtml      Build and serve with auto-reload on changes
#   make clean         Remove build artifacts
#
# Prerequisites:
#   pip install -r requirements.txt
#   (or from the repo root: make install-dev)

SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = build

.PHONY: help html livehtml clean

help:
	@echo "docs-new build targets:"
	@echo "  html       Build HTML documentation"
	@echo "  livehtml   Build and serve with auto-reload"
	@echo "  clean      Remove build artifacts"

html:
	$(SPHINXBUILD) -b html $(SOURCEDIR) $(BUILDDIR)/html $(SPHINXOPTS)
	@echo ""
	@echo "Build finished. Open $(BUILDDIR)/html/index.html in your browser."

livehtml:
	sphinx-autobuild $(SOURCEDIR) $(BUILDDIR)/html $(SPHINXOPTS)

clean:
	rm -rf $(BUILDDIR)
