from __future__ import annotations

import logging
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

logger = logging.getLogger()


class Grafana(BaseModel):
    """Grafana class for generating datasource file."""

    model_config = ConfigDict(
        validate_assignment=True,
        use_enum_values=True,
    )

    scheme: str = Field(description="Scheme", default="http")

    filepath: str = Field(alias="_filepath_")
    file_sd_configs: bool = Field(alias="_file_sd_configs_", default=False)
    _service_cfg: str = PrivateAttr()

    def generate(self, service: str) -> None:
        """Generate config files for prometheus."""
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
