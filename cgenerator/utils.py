"""Module containing additional functions."""
from __future__ import annotations

import json
import logging
from pathlib import Path

from yaml import Dumper
from yaml import dump as yml_dump

from cgenerator.config import ENV_FILE  # noqa: PLE611

logger = logging.getLogger()


# https://github.com/yaml/pyyaml/issues/234
class IndentDumper(Dumper):
    """IndentDumper class."""

    def increase_indent(self, flow=False, indentless=False) -> None:
        """Increase indent level."""
        return super().increase_indent(flow, False)


def is_key_exists(config: dict, service: str, service_ext: str) -> bool:
    """Check if key exists in config."""
    if service + service_ext not in config:
        logger.warning("No config found for job '%s' ", service)
        return False
    return True


def env_dump(config: dict[str, dict], service: str) -> None:
    """Dump environment variables as a string."""
    env = config.get(ENV_FILE)
    if not env:
        logger.warning(
            "Environment variables not found! Generating skipping ...")
        return
    service_env = env.get(service)
    if not service_env:
        logger.warning(
            "Environment variables for '%s' not found! Generating skipping ...",
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
    data = config.get(filename)
    if not data:
        logger.warning("Data for '%s' not found! "
                       "Generating skipping ...", filename)
        return
    dst_path: Path = Path(
        data.get("_filepath_"),
        filename,
    )
    if not dst_path.is_file() or force:
        with dst_path.open("w", encoding="utf-8") as f:
            data.pop("_filepath_")
            if file_ext == "yml":
                yml_dump(
                    data,
                    f,
                    indent=2,
                    default_flow_style=False,
                    Dumper=IndentDumper,
                )
            else:
                json.dump(data.get("data", {}), f, indent=4)
        logger.info("Data for '%s' written to '%s'", filename, dst_path)
        return
    logger.info("File '%s' already exists", dst_path)
