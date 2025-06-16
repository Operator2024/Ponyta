#!/usr/bin/env python3
"""Cgenerator main module."""

import argparse
import logging
import logging.config
import sys
from pathlib import Path

import yaml

from cgenerator.config import WEB_CONFIG_FILE, logging_config
from cgenerator.grafana import Grafana
from cgenerator.prometheus import Prometheus
from cgenerator.utils import data_dump, env_dump, is_key_exists

logging.config.dictConfig(logging_config)
logger = logging.getLogger()

ALLOWED_SERVICES: set[str] = set()
COMPOSE_CMD: str = "docker-compose up -d "
COMPOSE: Path = Path("compose.yml")
CONFIG: Path = Path("cgenerator.json")


def load_config() -> dict:
    """Load config file."""
    config = {}
    with CONFIG.open("r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
        logger.info("Service config loaded!")
    return config


def get_allowed_services(cmd_args: list) -> None:
    """Get list of allowed services based on docker-compose file."""
    global COMPOSE_CMD
    prom_job_mapping: dict[str, set] = {
        "prometheus": {"prometheus"},
        "node_exporter": {"node_exporter"},
        "snmp_exporter": {"snmp_exporter", "snmp_extended", "snmp_interface"},
        "ping_exporter": {"ping_exporter"},
        "blackbox_exporter": {"blackbox_exporter", "blackbox"},
        "grafana": {"grafana"},
    }

    if COMPOSE.exists():
        compose = {}
        with COMPOSE.open("r", encoding="utf-8") as f:
            compose = yaml.safe_load(f)
        for service in compose["services"]:
            if service in cmd_args:
                ALLOWED_SERVICES.update(prom_job_mapping[service])
                COMPOSE_CMD += service + " "


def main() -> None:
    """Do main work for generating config files."""
    msg_hdr: str = "===" * 3
    logger.info("Starting config generator")
    parser = argparse.ArgumentParser(
        description="Config generator for Ponyta services",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("--force",
                        "-f",
                        action="store_true",
                        default=False,
                        help="Force overwrite")
    parser.add_argument(
        "--prometheus",
        "-p",
        action="store_true",
        default=False,
        help="Generate config for prometheus",
    )
    parser.add_argument(
        "--node-exporter",
        "-n",
        action="store_true",
        default=False,
        help="Generate config for node-exporter",
    )
    parser.add_argument(
        "--snmp-exporter",
        "-s",
        action="store_true",
        default=False,
        help="Generate config for snmp-exporter",
    )
    parser.add_argument(
        "--ping-exporter",
        "-pe",
        action="store_true",
        default=False,
        help="Generate config for ping-exporter",
    )
    parser.add_argument(
        "--blackbox-exporter",
        "-be",
        action="store_true",
        default=False,
        help="Generate config for blackbox-exporter",
    )
    parser.add_argument("--grafana", "-g", action="store_true", default=False)
    args = parser.parse_args()
    get_allowed_services([name for name, value in vars(args).items() if value])
    if not ALLOWED_SERVICES:
        logger.warning("No allowed services found")
        sys.exit(0)
    msg_allowed_services: str = ", ".join(ALLOWED_SERVICES)
    logger.info("Allowed services: %s", msg_allowed_services)
    service_config = load_config()
    service_extension = ".yml"
    for service in ALLOWED_SERVICES:
        srv_name: str = service + service_extension
        if not is_key_exists(
                config=service_config,
                service=service,
                service_ext=service_extension,
        ):
            continue
        logger.info("%s Service '%s' genetrator started %s", msg_hdr, service,
                    msg_hdr)

        prom = Prometheus(**service_config[srv_name])
        prom.generate(service=service)
        prom.config_dump(filename=srv_name, force=args.force)

        match service:
            case "prometheus":
                prom.secret_dump(config=service_config, force=args.force)
                env_dump(config=service_config, service=service)
                data_dump(
                    config=service_config,
                    filename=WEB_CONFIG_FILE,
                    force=args.force,
                )
            case "snmp_exporter" | "snmp_extended" | "snmp_interface":
                snmp = prom
                if snmp.file_sd_configs:
                    data_dump(
                        config=service_config,
                        filename="snmp_targets.json",
                        force=args.force,
                    )
                    env_dump(config=service_config, service=service)
            case "ping_exporter":
                data_dump(
                    config=service_config,
                    filename="ping.yml",
                    force=args.force,
                )
            case "blackbox_exporter" | "blackbox":
                blackbox = prom
                if blackbox.file_sd_configs:
                    data_dump(
                        config=service_config,
                        filename="blackbox_targets.json",
                        force=args.force,
                    )
            case "grafana":
                datasource = Grafana(**service_config["datasource.yml"])
                datasource.generate(service="datasource")
                datasource.config_dump(
                    filename="datasource.yml",
                    force=args.force,
                )
                env_dump(config=service_config, service=service)
        logger.info("%s Service '%s' genetrator finished %s", msg_hdr, service,
                    msg_hdr)
    logger.info("Docker compose command for services: %s", COMPOSE_CMD)


if __name__ == "__main__":
    main()
