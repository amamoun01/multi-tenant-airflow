# =================================================================
# Multi-Tenant Airflow Orchestration Platform Management Interface.
# =================================================================

generate:
	python scripts/render_compose.py

up: generate
	docker compose -f docker-compose.yml -f generated/docker-compose.tenants.yml up -d

down:
	docker compose -f docker-compose.yml -f generated/docker-compose.tenants.yml down

destroy:
	docker compose -f docker-compose.yml -f generated/docker-compose.tenants.yml down -v

restart: down up

lint:
	pre-commit run ruff --all-files
	pre-commit run yamllint --all-files

security:
	pre-commit run bandit --all-files

test:
	pytest
