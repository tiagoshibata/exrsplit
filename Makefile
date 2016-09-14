.PHONY: doc
doc: README.rst

README.rst:
	pandoc --from=markdown --to=rst --output=README.rst README.md
