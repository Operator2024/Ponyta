"""The module contains classes for generating Grafana configuration files."""
from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

from cgenerator.utils import logger


class Datasource(BaseModel):
    """Grafana class for generating datasource file."""

    model_config = ConfigDict(
        validate_assignment=True,
        use_enum_values=True,
    )

    name: str = Field(description="Name for datasource", default="Prometheus")
    url: str = Field(description="Full URL for datasource")
    scheme: str = Field(description="Scheme: http or https", default="http")
    basic_auth_user: str | None = Field(description="Basic auth username",
                                        min_length=5,
                                        default=None)
    basic_auth_password: str | None = Field(description="Basic auth password",
                                            default=None)
    server_name: str | None = Field(
        description="Server name in specify the certificate", default=None)
    is_default: bool = Field(description="Is default datasource", default=True)

    template_name: str = Field(alias="_template_name_", default="datasource")
    filepath: str = Field(alias="_filepath_")
    _service_cfg: str = PrivateAttr()

    def generate(self) -> None:
        """Generate config files for prometheus."""
        self.__generate_from_template(self.template_name)

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
                    "templates/grafana"),
            ]),
            autoescape=True,
            trim_blocks=True,
            lstrip_blocks=True,
        )
        template = environment.get_template(f"{template_name}.jinja")
        self._service_cfg = template.render(self.model_dump())
        logger.info("Config for %s generated", template)
