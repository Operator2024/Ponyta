import argparse
import logging
import logging.config
import sys
from pathlib import Path

import yaml

import cgenerator
from cgenerator import WEB_CONFIG_FILE, utils
from cgenerator.grafana import Grafana
from cgenerator.prometheus import Prometheus

logging.config.dictConfig(cgenerator.logging_config)
logger = logging.getLogger()

ALLOWED_SERVICES: set[str] = set()
COMPOSE: Path = Path("compose.yml")
CONFIG: Path = Path("cgenerator.json")


def load_config() -> dict:
    config = {}
    with open(CONFIG) as f:
        config = yaml.load(f, Loader=yaml.Loader)
        logger.info("Service config loaded!")
    return config


def get_allowed_services(cmd_args: list) -> None:
    global ALLOWED_SERVICES

    prom_job_mapping: dict[str, set] = {
        "prometheus": set(["prometheus"]),
        "node_exporter": set(["node_exporter"]),
        "snmp_exporter":
        set(["snmp_exporter", "snmp_extended", "snmp_interface"], ),
        "ping_exporter": set(["ping_exporter"]),
        "blackbox_exporter": set(["blackbox_exporter", "blackbox"]),
        "grafana": set(["grafana"]),
    }

    if COMPOSE.exists():
        compose = {}
        with open(COMPOSE) as f:
            compose = yaml.load(f, Loader=yaml.Loader)
        for service in compose["services"]:
            if service in cmd_args:
                ALLOWED_SERVICES.update(prom_job_mapping[service])
    return


def main() -> None:
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

    logger.info("Allowed services: " + ", ".join(ALLOWED_SERVICES))
    service_config = load_config()
    service_extension = ".yml"
    for service in ALLOWED_SERVICES:
        srv_name: str = service + service_extension
        if not utils.is_key_exists(
                config=service_config,
                service=service,
                service_ext=service_extension,
        ):
            continue
        logger.info(
            msg_hdr + " " + "Service '%s' generator started" + " " + msg_hdr,
            service)
        match service:
            case "prometheus":
                prom = Prometheus(**service_config[srv_name])
                prom.secret_dump(config=service_config, force=args.force)
                prom.generate(service=service)
                prom.config_dump(filename=srv_name, force=args.force)
                utils.env_dump(config=service_config, service=service)
                utils.data_dump(
                    config=service_config,
                    filename=WEB_CONFIG_FILE,
                    force=args.force,
                )
            case "node_exporter":
                node = Prometheus(**service_config[srv_name])
                node.generate(service=service)
                node.config_dump(filename=srv_name, force=args.force)
            case "snmp_exporter" | "snmp_extended" | "snmp_interface":
                snmp = Prometheus(**service_config[srv_name])
                snmp.generate(service=service)
                snmp.config_dump(filename=srv_name, force=args.force)
                if snmp.file_sd_configs:
                    utils.data_dump(
                        config=service_config,
                        filename="snmp_targets.json",
                        force=args.force,
                    )
                    utils.env_dump(config=service_config, service=service)
            case "ping_exporter":
                ping = Prometheus(**service_config[srv_name])
                ping.generate(service=service)
                ping.config_dump(filename=srv_name, force=args.force)
                utils.data_dump(
                    config=service_config,
                    filename="ping.yml",
                    force=args.force,
                )
            case "blackbox_exporter" | "blackbox":
                blackbox = Prometheus(**service_config[srv_name])
                blackbox.generate(service=service)
                blackbox.config_dump(filename=srv_name, force=args.force)
                if blackbox.file_sd_configs:
                    utils.data_dump(
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
                grafana = Prometheus(**service_config[srv_name])
                grafana.generate(service=service)
                grafana.config_dump(filename=srv_name, force=args.force)
                utils.env_dump(config=service_config, service=service)
        logger.info(
            msg_hdr + " " + "Service '%s' generator finished" + " " + msg_hdr,
            service)


if __name__ == "__main__":
    main()
