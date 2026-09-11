.PHONY: catalog check serve

# Regenerate the README skill catalog from each SKILL.md frontmatter.
catalog:
	@python3 scripts/build_catalog.py

# Fail if the catalog is stale, or if any SKILL.md frontmatter won't parse.
# Frontmatter errors fail SOFT in Claude Code — a broken skill still answers to
# /name while auto-invocation silently stops — so this is the only place it surfaces.
check:
	@python3 scripts/build_catalog.py --check
	@python3 scripts/check_frontmatter.py

serve:
	@echo "Serving at http://localhost:8000"
	@python3 -m http.server 8000
