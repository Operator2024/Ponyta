import json
from pathlib import Path

from yaml import dump as yml_dump

CONFIG: Path = Path("cgenerator.json")
BASE_FIELD: tuple = ("__filepath__", )


class CGenerator:

    def __init__(self, path: Path, name: str, *args, **kwargs) -> None:
        self.path = path / name
        self.args = args
        self.kwargs = kwargs

    def to_yaml(self) -> None:
        with open(self.path, "w") as f:
            yml_dump(self.kwargs, f)

    def to_plaintext(self, with_keys=True) -> None:
        with open(self.path, "w") as f:
            for field in self.kwargs:
                if with_keys:
                    f.write(f"{field}={self.kwargs[field]}\n")
                else:
                    f.write(f"{self.kwargs[field]}\n")

    def to_env(self) -> None:
        return self.to_plaintext()


def load_config() -> dict[str, dict[str, str]]:
    config = {}
    if Path(CONFIG).exists():
        with open(CONFIG) as cfg:
            config = json.load(cfg)
            return config
    print(f"Config file {str(CONFIG)!r} not found")
    return config


def check_basefield(cfg: dict[str, str]) -> bool:
    for field in BASE_FIELD:
        if field not in cfg:
            return False
    return True


def main() -> None:
    config: dict[str, dict[str, str]] = load_config()
    for section, cfg in config.items():
        if not check_basefield(cfg):
            continue
        _filepath = Path(cfg.pop("__filepath__"))
        match section:
            case "web.yml":
                CGenerator(path=_filepath, name=f"{section}", **cfg).to_yaml()
            case ".env":
                CGenerator(path=_filepath, name=f"{section}",
                           **cfg).to_plaintext()
            case _:
                CGenerator(path=_filepath, name=f"{section}",
                           **cfg).to_plaintext(with_keys=False)


if __name__ == "__main__":
    main()
