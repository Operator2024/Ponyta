#!/usr/bin/env python3
"""Cgenerator main module."""

__version__ = "1.1.1-rc1"

import argparse
import json
import logging
import logging.config
import sys

import yaml

from cgenerator.config import (
    COMPOSE,
    COMPOSE_CMD,
    CONFIG,
    CONFIG_MAPPING,
    default_config,
    logger,
    logging_config,
)
from cgenerator.utils import (
    deploy_services,
    display_config_map,
    prepare_config,
)

ALLOWED_SERVICES: set[str] = set()


def load_config() -> dict:
    """Load config file."""
    config = {}
    with CONFIG.open("r", encoding="utf-8") as f:
        config: dict = yaml.safe_load(f)
        logger.info("Service config loaded!")
    return prepare_config(
        default_config=default_config,
        override_config=config,
    )


def set_allowed_services(cmd_args: list, config: dict) -> None:
    """Get list of allowed services based on docker-compose file."""
    global COMPOSE_CMD

    if COMPOSE.exists():
        compose = {}
        with COMPOSE.open("r", encoding="utf-8") as f:
            compose = yaml.safe_load(f)
        for filename, data in config.items():
            bind_service: str = data.get("bind_service", "")
            if bind_service in cmd_args and bind_service in compose["services"]:
                ALLOWED_SERVICES.add(bind_service)
                CONFIG_MAPPING[bind_service].add(filename)
        COMPOSE_CMD += " ".join(ALLOWED_SERVICES)


def main() -> None:
    """Do main work for generating config files."""
    parser = argparse.ArgumentParser(
        description=
        f"Config generator for Ponyta services, version {__version__}",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("--export_default_config",
                        "-export",
                        action="store_true",
                        default=False)
    parser.add_argument("-v", "--verbose", action="store_true", default=False)
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

    if args.verbose:
        logging_config["loggers"]["root"]["level"] = "DEBUG"
    logging.config.dictConfig(logging_config)
    logger.info("Starting config generator")

    services: list = [
        name for name, value in vars(args).items()
        if value and name not in ["verbose"]
    ]
    if not services:
        parser.print_help()
        sys.exit(0)
    if args.export_default_config:
        with open("default_config.json", "w", encoding="utf-8") as f:
            json.dump(default_config, f, indent=4)
        logger.info("Default config exported to default_config.json. Bye!")
        sys.exit(0)
    configs = load_config()
    set_allowed_services(
        services,
        configs,
    )
    if not ALLOWED_SERVICES:
        logger.warning("No selected services found")
        sys.exit(0)
    msg_allowed_services: str = ", ".join(ALLOWED_SERVICES)
    logger.info("Selected services: %s", msg_allowed_services)
    display_config_map(config_map=CONFIG_MAPPING)

    for service_name in ALLOWED_SERVICES:
        deploy_services(service_name=service_name,
                        configs=configs,
                        force=args.force)
    logger.info("Docker compose command for services: %s", COMPOSE_CMD)


if __name__ == "__main__":
    main()
