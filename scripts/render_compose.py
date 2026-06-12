"""Render Compose file for multi-tenant Airflow platform."""

from pathlib import Path

import yaml


AIRFLOW_IMAGE = "apache/airflow:3.0.3"

with open("config/tenants.yml") as f:
    tenants = yaml.safe_load(f)["tenants"]

services = {}

for index, tenant in enumerate(tenants):
    name = tenant["name"]
    workers = tenant["workers"]

    db_name = f"{name}-db"

    redis_db_index = index

    common_env = {
        "AIRFLOW__CORE__EXECUTOR": "CeleryExecutor",
        "AIRFLOW__DATABASE__SQL_ALCHEMY_CONN": f"postgresql+psycopg2://airflow:airflow@{db_name}/airflow",
        "AIRFLOW__CELERY__RESULT_BACKEND": f"db+postgresql://airflow:airflow@{db_name}/airflow",
        "AIRFLOW__CELERY__BROKER_URL": f"redis://redis:6379/{redis_db_index}",
        "AIRFLOW__CORE__LOAD_EXAMPLES": "true",
        "AIRFLOW__CORE__SIMPLE_AUTH_MANAGER_ALL_ADMINS": "true",
    }

    network_config = {"networks": ["airflow-platform-net"]}

    # Postgres Engine per Tenant
    services[db_name] = {
        "image": "postgres:16",
        "restart": "always",
        "environment": {
            "POSTGRES_USER": "airflow",
            "POSTGRES_PASSWORD": "airflow",
            "POSTGRES_DB": "airflow",
        },
        **network_config,
    }

    # Init container
    services[f"{name}-init"] = {
        "image": AIRFLOW_IMAGE,
        "restart": "no",
        "depends_on": [db_name, "redis"],
        "environment": common_env,
        "command": "bash -c 'airflow db migrate'",
        **network_config,
    }

    # API Server with Traefik Labels
    services[f"{name}-api-server"] = {
        "image": AIRFLOW_IMAGE,
        "command": "api-server",
        "restart": "always",
        "depends_on": [f"{name}-init"],
        "environment": common_env,
        "labels": [
            "traefik.enable=true",
            f"traefik.http.routers.{name}.rule=Host(`{name}.localhost`)",
            f"traefik.http.routers.{name}.entrypoints=web",
            f"traefik.http.services.{name}.loadbalancer.server.port=8080",
        ],
        **network_config,
    }

    # Scheduler
    services[f"{name}-scheduler"] = {
        "image": AIRFLOW_IMAGE,
        "command": "scheduler",
        "restart": "always",
        "depends_on": [f"{name}-init"],
        "environment": common_env,
        **network_config,
    }

    # Triggerer
    services[f"{name}-triggerer"] = {
        "image": AIRFLOW_IMAGE,
        "command": "triggerer",
        "restart": "always",
        "depends_on": [f"{name}-init"],
        "environment": common_env,
        **network_config,
    }

    # DAG processor
    services[f"{name}-dag-processor"] = {
        "image": AIRFLOW_IMAGE,
        "command": "dag-processor",
        "restart": "always",
        "depends_on": [f"{name}-init"],
        "environment": common_env,
        **network_config,
    }

    # Workers
    for i in range(1, workers + 1):
        services[f"{name}-worker-{i}"] = {
            "image": AIRFLOW_IMAGE,
            "command": "celery worker",
            "restart": "always",
            "depends_on": [f"{name}-init"],
            "environment": common_env,
            **network_config,
        }

# Instruct the generated file to hook directly into top-level external network
output = {
    "services": services,
    "networks": {"airflow-platform-net": {"external": True}},
}

Path("generated").mkdir(exist_ok=True)

with open("generated/docker-compose.tenants.yml", "w") as f:
    yaml.dump(output, f, sort_keys=False)

print("Compose file generated successfully with global proxy networking.")
