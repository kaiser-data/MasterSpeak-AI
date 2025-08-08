.PHONY: check-import check-import-docker test

check-import:
	PYTHONPATH=. python3 scripts/check_import.py

check-import-docker:
	@echo "Testing import path as Docker would see it..."
	cd backend && PYTHONPATH=/Users/marty/CodingProjects/claude-code-projects/MasterSpeak-AI python3 -c "import backend.main; print('✓ Docker-style import successful')"

test:
	PYTHONPATH=. python3 -m pytest backend/tests/ -v