.PHONY: catalog check serve deps

# Both scripts parse frontmatter with PyYAML. Using the same parser for generation and
# validation is deliberate: a regex reader can publish a value the validator read
# differently, so the manifest could disagree with the YAML it was checked against.
deps:
	@python3 -c "import yaml" 2>/dev/null || pip install pyyaml

# Regenerate the README skill catalog from each SKILL.md frontmatter.
catalog:
	@python3 scripts/build_catalog.py
	@python3 scripts/sync_guide.py

# Fail if the catalog is stale, or if any SKILL.md frontmatter won't parse.
# Frontmatter errors fail SOFT in Claude Code — a broken skill still answers to
# /name while auto-invocation silently stops — so this is the only place it surfaces.
check:
	@python3 scripts/build_catalog.py --check
	@python3 scripts/sync_guide.py --check
	@python3 scripts/check_frontmatter.py

serve:
	@echo "Serving at http://localhost:8000"
	@python3 -m http.server 8000
