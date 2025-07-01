from __future__ import annotations

import logging
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

logger = logging.getLogger()


class BasicAuth(BaseModel):
    """Basic auth class for generating config files."""

    username: str = Field(description="Basic auth username", min_length=5)
    password: str | None = Field(description="Basic auth password",
                                 min_length=8,
                                 default=None)
    password_file: str | None = Field(description="Basic auth password file",
                                      default=None)

    def secret_dump(self, config: dict, filename: str, force: bool) -> None:
        """Dump secret to file."""
        if not self.password_file:
            return

        password_file = config.get(filename, {})
        if not password_file:
            logger.warning("Data for %s not found! Generating skipping ...",
                           filename)
            return
        dst_path: Path = Path(password_file.get("_filepath_"), filename)
        if not dst_path.is_file() or force:
            with dst_path.open("w", encoding="utf-8") as f:
                f.write(password_file["secret"])
            logger.info("Data for %s written to %s", filename, dst_path)
            return
        logger.info("File %s already exists", dst_path)


class Prometheus(BaseModel):
    """Prometheus class for generating config files."""

    model_config = ConfigDict(
        validate_assignment=True,
        use_enum_values=True,
    )

    scrape_interval: str = Field(description="Scrape interval", default="15s")
    server_name: str | None = Field(description="Server name", default=None)
    scheme: str = Field(description="Scheme", default="http")
    basic_auth: BasicAuth | None = Field(description="Basic auth",
                                         default=None)

    filepath: str = Field(alias="_filepath_")
    file_sd_configs: bool = Field(alias="_file_sd_configs_", default=False)
    _service_cfg: str = PrivateAttr()

    def secret_dump(self, config: dict, force: bool) -> None:
        """Dump secret to file."""
        if not self.basic_auth:
            logger.warning("No basic auth configured")
            return
        password_file = self.basic_auth.password_file
        if password_file is not None:

            logger.info("Password file is set - %s", password_file)
            filename = password_file.split("/")[-1]

            self.basic_auth.secret_dump(config=config,
                                        filename=filename,
                                        force=force)

    def generate(self, service: str) -> None:
        """Generate config files for prometheus."""
        environment = Environment(
            loader=FileSystemLoader([
                Path(
                    Path(Path(__file__).resolve()).parent,
                    "templates/prometheus"),
            ]),
            autoescape=True,
            trim_blocks=True,
            lstrip_blocks=True,
        )
        template = environment.get_template(f"{service}.jinja")
        self._service_cfg = template.render(self.model_dump())
        logger.info("Config for %s generated", service)

    def config_dump(self, filename: str, force: bool) -> None:
        """Dump jinja generated config to file."""

        path_to_file: Path = Path(self.filepath, filename)
        if path_to_file.is_file() and not force:
            logger.info("File %s already exists. Skipping ...", path_to_file)
            return
        if not Path(self.filepath).exists():
            logger.info("Creating directory %s", self.filepath)
            Path(self.filepath).mkdir(parents=True)

        with path_to_file.open("w", encoding="utf-8") as f:
            f.write(self._service_cfg)

        logger.info("Config for %s written to %s", filename, path_to_file)
