"""Module containing additional functions."""
from __future__ import annotations

import copy
import json
from pathlib import Path

from yaml import Dumper
from yaml import dump as yml_dump

from cgenerator.config import CONFIG_MAPPING, ENV_FILE, MESSAGE_HDR, logger
from cgenerator.grafana import Datasource
from cgenerator.prometheus import Job


# https://github.com/yaml/pyyaml/issues/234
class IndentDumper(Dumper):
    """IndentDumper class."""

    def increase_indent(self, flow: bool = False, *args, **kwargs) -> None:
        """Increase indent level."""
        return super().increase_indent(flow=flow, indentless=False)


def env_dump(config: dict[str, dict], service: str) -> None:
    """Dump environment variables as a string."""
    env = config.get(ENV_FILE)
    if not env:
        logger.debug("Environment variables not found! Generating skipping ")
        return
    service_env = env.get(service)
    if not service_env:
        logger.debug(
            "Environment variables for '%s' not found! Generating skipping ",
            service)
        return
    filepath = Path(env.get("_filepath_", "./"), ENV_FILE)

    envfile_keys: set = set()
    if filepath.is_file():
        with filepath.open("r", encoding="utf-8") as f:
            for line in f.readlines():
                key, _, _ = line.partition("=")
                envfile_keys.add(key.strip())

    for name, value in dict(sorted(service_env.items())).items():
        if name in envfile_keys:
            continue
        with filepath.open("a", encoding="utf-8") as f:
            f.write(f"{name}={value}\n")

    logger.info("Environment variables for '%s' written to '%s'", service,
                filepath)


def data_dump(config: dict, filename: str, force: bool) -> None:
    """Save data to file."""
    file_ext = filename.split(".")[-1]
    data: dict = copy.deepcopy(config)
    if not data or data.get("data") is None:
        logger.warning(
            "Fileobject is empty or key 'data' not found! File '%s' skipped.",
            filename)
        return
    if file_ext not in ["yml", "json", "txt"]:
        logger.warning(
            "Unsupported file extension '%s'! File '%s' skipped.",
            file_ext,
            filename,
        )
        return
    dst_path: Path = Path(
        data.get("_filepath_", ""),
        filename,
    )
    if not dst_path.is_file() or force:
        data.pop("_filepath_", None)
        data.pop("bind_service", None)
        data.pop("bind_module", None)
        with dst_path.open("w", encoding="utf-8") as f:
            if file_ext == "yml":
                yml_dump(
                    data["data"],
                    f,
                    indent=2,
                    default_flow_style=False,
                    Dumper=IndentDumper,
                )
            elif file_ext == "json":
                json.dump(data.get("data", {}), f, indent=4)
            else:
                f.write(data["data"])
        logger.info("Data for '%s' written to '%s'", filename, dst_path)
        return
    logger.debug("File '%s' already exists", dst_path)


def prepare_config(default_config: dict, override_config: dict) -> dict:
    """Prepare config for jinja."""
    bind_service_field: str = "bind_service"
    bind_module_field: str = "bind_module"

    config: dict = copy.deepcopy(default_config)
    for key, value in override_config.items():
        if key in default_config:
            config[key] = merge(default_config[key], value)
        else:
            config[key] = value

        if bind_service_field not in config[
                key] and bind_module_field not in config[key] and key != ".env":
            config.pop(key)
            logger.debug(
                "Attribute '%s' and '%s' not found!"
                " Config '%s' removed ", bind_service_field, bind_module_field,
                key)
    return config


def merge(default_config: dict, override_config: dict, level: int = 3) -> dict:
    """Merge config."""
    if not isinstance(override_config, default_config.__class__):
        logger.debug("Merge config error. Type mismatch!")
        return default_config

    for key, value in override_config.items():
        if key not in default_config:
            default_config[key] = value
            continue

        if isinstance(value, dict) and level > 0:
            default_config[key] = merge(default_config[key], value, level - 1)
        if isinstance(value, dict) and level <= 0:
            logger.warning("Merge key '%s' skipped, level is 0", key)
            logger.debug("Config: %s", override_config)
        if isinstance(value, (int, float, str, tuple, list)):
            default_config[key] = value

    return default_config


def display_config_map(config_map: dict[str, set]) -> None:
    """Display of found configurations for docker compose services."""
    logger.debug("Next configurations was found for services:")
    for key, value in config_map.items():
        logger.debug(
            "  -> '%s': %s",
            key,
            ", ".join(value) if value else "None",
        )


def deploy_service(
    config_name: str,
    configs: dict,
    force: bool,
) -> None:
    """Deploy service."""
    config = configs[config_name]
    bind_module = config.get("bind_module")
    match bind_module:
        case "file":
            logger.debug(
                "%s Deploying file '%s' ",
                MESSAGE_HDR,
                config_name,
            )
            data_dump(config, config_name, force=force)
        case "promjob":
            logger.debug(
                "%s Deploying promjob '%s' ",
                MESSAGE_HDR,
                config_name,
            )
            promjob = Job(**config)
            promjob.generate(template_name=config_name)
            promjob.config_dump(filename=config_name, force=force)
            file_sd_configs = promjob.file_sd_configs
            if (file_sd_configs and file_sd_configs.files
                    and file_sd_configs.configs):
                for filepath in file_sd_configs.files:
                    _, filename = filepath.rsplit("/", 1)

                    if file_sd_configs.configs.get(filename):
                        data_dump(
                            file_sd_configs.configs[filename],
                            filename,
                            force=force,
                        )
        case "datasource":
            logger.debug(
                "%s Deploying datasource '%s' ",
                MESSAGE_HDR,
                config_name,
            )
            datasource = Datasource(**config)
            datasource.generate()
            datasource.config_dump(filename=config_name, force=force)
        case _:
            logger.warning(
                "Unknown bind module '%s' for config '%s'",
                bind_module,
                config_name,
            )


def deploy_services(service_name: str, configs: dict, force: bool) -> None:
    """Deploy services."""
    config_names: set | None = CONFIG_MAPPING.get(service_name)
    if not config_names:
        return
    logger.info("%s Begin deploy service '%s'  %s", MESSAGE_HDR, service_name,
                MESSAGE_HDR)
    for config_name in config_names:
        deploy_service(config_name, configs, force)

    env_dump(configs, service_name)
    logger.info("%s Deploy service '%s' done %s", MESSAGE_HDR, service_name,
                MESSAGE_HDR)
