# Makefile for setting up and activating a Python virtual environment

# Set the desired Python interpreter (change if needed)
PYTHON := python3.12

# Virtual environment directory
VENV := .venv

STAGE?=prod

# Default target
all: venv activate local_install

venv: # Create new Python virtual environment
	uv venv --seed --python $(PYTHON) $(VENV)

activate: # Activate Python virtual environment
	@. $(VENV)/bin/activate

local_install: # Install minimal set of local development dependencies
	pip install --upgrade pip
	pip install uv
	uv pip install --upgrade pip
	uv pip install -r airmonitor_forwarder/requirements.txt

pre-commit: # Run code quality checks on all Python files
	pre-commit install
	pre-commit run --files *
	pre-commit run --files airmonitor_forwarder/*

update: # Update all dependencies and tools to latest versions
	pre-commit autoupdate
	pur -r airmonitor_forwarder/requirements.txt


clean: # Remove virtual environment and cleanup project files
	rm -rf $(VENV)

help: # Display this help message
	@printf "\n\033[1;32mAvailable commands: \033[00m\n\n"
	@awk 'BEGIN {FS = ":.*#"; printf "\033[36m%-30s\033[0m %s\n", "target", "help"} /^[a-zA-Z0-9_-]+:.*?#/ { printf "\033[36m%-30s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)
