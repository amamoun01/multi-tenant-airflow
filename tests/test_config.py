"""Test configuration files."""

import yaml


def test_tenants_exist():
    with open("config/tenants.yml") as f:
        data = yaml.safe_load(f)

    assert len(data["tenants"]) > 0
