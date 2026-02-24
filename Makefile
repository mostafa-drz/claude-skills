.PHONY: serve

serve:
	@echo "Serving at http://localhost:8000"
	@python3 -m http.server 8000
