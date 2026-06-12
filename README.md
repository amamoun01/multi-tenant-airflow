# Multi-Tenant Airflow

A lightweight, automated platform designed to spin up multiple completely isolated [`Apache Airflow`](https://airflow.apache.org/docs/) environments while sharing a centralized local database and message broker footprint.

## 🏗️ System Architecture

* **Ingress Layer:** [Traefik](https://doc.traefik.io/) v3 acts as a reverse proxy, routing requests dynamically via local subdomains (`tenant-a.localhost`, `tenant-b.localhost`, `tenant-c.localhost`).
* **Database Engine:** A shared [PostgreSQL](https://www.postgresql.org/docs/) instance isolates tenant state workflows utilizing independent databases per tenant.
* **Message Broker:** A single [Redis](https://redis.io/docs/latest/) container acts as the Celery task runner broker, leveraging independent database channels (`/0`, `/1`, `/2`) to keep queues distinct.

![Architecture Diagram](https://github.com/multi-tenant-airflow/blob/main/assets/architecture.png)

## 🚀 Quick Start

### 1. Update Local DNS Routing

Because the reverse proxy routes traffic based on domain names, you must tell your machine to resolve the tenant domains locally. Add this line to your hosts file (`/etc/hosts` on Linux/macOS, or `C:\Windows\System32\drivers\etc\hosts` on Windows):

```text
127.0.0.1 tenant-a.localhost tenant-b.localhost tenant-c.localhost
```

### 2. Spin Up the Platform

The complete setup, resource compilation, and container management lifecycle are automated through a single tool interface using `make`:

```bash
# Install local development tools
pip install -r requirements-dev.txt
pre-commit install

# Compile the multi-tenant configuration and boot the system
make up
```

### 3. Access the Web Interfaces

Open your browser to navigate directly into your isolated environments:

* Traefik Proxy Dashboard: http://localhost:8080/dashboard/

* Tenant A Airflow: http://tenant-a.localhost

* Tenant B Airflow: http://tenant-b.localhost

* Tenant C Airflow: http://tenant-c.localhost

## 🛠️ Management Commands

| Command | Action |
| :--- | :--- |
| `make generate` | Parses `config/tenants.yml` and renders the tenant docker-compose layout. |
| `make up` | Automatically runs the generation script and provisions all active containers. |
| `make down` | Safely stops execution threads and de-allocates local networks without losing data. |
| `make destroy` | Clears all containers, networks, and flushes persistent volumes entirely. |
| `make lint` | Runs automatic style and syntax verification passes using `Ruff` and `Yamllint`. |
| `make security` | Evaluates code security postures utilizing the `Bandit` SAST engine. |
---

## 🛡️ CI/CD Quality Gates

The codebase enforces quality control using an optimized GitHub Actions workflow pipeline:

* **Code Analysis**: Runs fast, parallelized code linting (Ruff), configuration validation (Yamllint), and security vulnerability detection (Bandit).

* **Structural Validation**: Performs an automated generation dry-run to guarantee the Python compilation script outputs flawless docker schemas.

* **Unit Testing**: Executes your backend test suite via pytest only after styling and security checks have successfully cleared.

## 🔮 Next Steps & Scaling Roadmap

To transition this platform from a localized development layout into a resilient, cloud-native orchestration ecosystem, the following architectural milestones are planned:

* **Kubernetes Orchestration & Auto-scaling:** Migrate the decoupled tenant layers into a managed Kubernetes cluster leveraging the official **Airflow Helm Chart**. Integrate **KEDA (Kubernetes Event-driven Autoscaling)** to dynamically scale dedicated worker pods on-demand based on Celery queue depths.
* **Centralized Identity & Access Management:** Modernize access controls by upgrading the local `SimpleAuthManager` to a federated OpenID Connect (OIDC) / OAuth2 workflow utilizing an identity provider to securely enforce multi-tenant isolation.
* **Unified Observability Platform:** Implement **Prometheus** to capture real-time system metrics, **Grafana** to provide multi-tenant performance visualization dashboards, and a **Loki/FluentBit** log aggregation pipeline for centralized troubleshooting.
