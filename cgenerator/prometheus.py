"""The module contains classes for generating basic Prometheus configuration files."""
from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

from cgenerator.utils import logger


class StaticConfigs(BaseModel):
    """Class for attributes of static config files."""

    model_config = ConfigDict(validate_assignment=True)

    targets: list[str]
    labels: dict[str, str]


class FileSDConfigs(BaseModel):
    """Class for attributes of file SD config files."""

    model_config = ConfigDict(validate_assignment=True)

    files: list[str]
    refresh_interval: str
    configs: dict[str, dict] | None = None


class BasicAuth(BaseModel):
    """Basic auth class for generating config files."""

    username: str = Field(description="Basic auth username", min_length=5)
    password: str | None = Field(
        description="Basic auth password",
        min_length=8,
        default=None,
    )
    password_file: str | None = Field(
        description="Basic auth password file",
        default=None,
    )


class Job(BaseModel):
    """Prometheus class for generating job files."""

    model_config = ConfigDict(
        validate_assignment=True,
        use_enum_values=True,
    )

    scrape_interval: str = Field(description="Scrape interval", default="15s")
    server_name: str | None = Field(description="Server name", default=None)
    scheme: str = Field(description="Scheme", default="http")
    basic_auth: BasicAuth | None = Field(
        description="Basic auth",
        default=None,
    )
    static_configs: StaticConfigs | None = Field(
        description="Static configs",
        default=None,
    )
    file_sd_configs: FileSDConfigs | None = Field(
        description="File SD configs",
        default=None,
    )

    filepath: str = Field(alias="_filepath_")
    _service_cfg: str = PrivateAttr()

    def generate(self, template_name: str) -> None:
        """Generate config files for prometheus."""
        if template_name.find("."):
            template_name = template_name.split(".")[0]
        self.__generate_from_template(template_name)

    def config_dump(self, filename: str, force: bool) -> None:
        """Dump jinja generated config to file."""
        path_to_file: Path = Path(self.filepath, filename)
        if path_to_file.is_file() and not force:
            logger.info("File %s already exists. Skipping ", path_to_file)
            return
        if not Path(self.filepath).exists():
            logger.debug("Creating directory %s", self.filepath)
            Path(self.filepath).mkdir(parents=True)

        with path_to_file.open("w", encoding="utf-8") as f:
            f.write(self._service_cfg)

        logger.info("Config for %s written to %s", filename, path_to_file)

    def __generate_from_template(self, template_name: str) -> None:
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
        template = environment.get_template(f"{template_name}.jinja")
        self._service_cfg = template.render(self.model_dump())
        logger.info("Config for %s generated", template)
