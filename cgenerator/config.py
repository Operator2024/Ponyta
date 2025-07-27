"""The module contains configuration data."""
import logging
import os

logging_config: dict = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "datefmt": "[%d/%b/%Y %H:%M:%S %z]",
            "format": "%(asctime)s - %(message)s",
        },
        "verbose": {
            "datefmt":
            "[%d/%b/%Y %H:%M:%S %z]",
            "format":
            "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "NOTSET",
            "formatter": "simple",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "level": "NOTSET",
            "formatter": "verbose",
            "when": "D",
            "backupCount": 0,
            "filename": "cgenerator.log",
        },
    },
    "loggers": {
        "root": {
            "level": "INFO",
            "handlers": ["console"],
        },
    },
}

logger: logging.Logger = logging.getLogger()

default_config: dict = {
    ".env": {
        "_filepath_": "./",
        "prometheus": {
            "PROM_PORT": "9090",
            "PROM_URL": "",
        },
        "grafana": {
            "PROM_PORT": "9090",
            "DOMAIN": "",
            "GF_PORT": "80",
            "GF_USER": "admin",
            "GF_SECRET": "defaultpassword",
            "GF_SUB_PATH": "/grafana",
            "SMTP_HOST": "",
            "SMTP_USER": "",
            "SMTP_PASSWORD": "",
            "SMTP_FROM_ADDRESS": "",
            "GF_SERVER_CERT_FILE": "/etc/grafana/certs/tls.crt",
            "GF_SERVER_CERT_KEY": "/etc/grafana/certs/tls.key",
            "GF_SERVER_PROTOCOL": "http",
        },
        "snmp_exporter": {
            "SNMP_SECRET": "defaultpassword",
            "SNMP_USER": "admin",
        },
    },
    "web.yml": {
        "_filepath_": "./prometheus",
        "basic_auth_users": {
            "admin":
            "$2y$12$TEqV7JcONj2KMwSMczSm0OB1FdSwI/aqhfNWv8n9QbU0SAD6TqEV2",
        },
        "bind_service": "prometheus",
        "bind_module": "file"
    },
    "secret.txt": {
        "_filepath_": "./prometheus",
        "username": "admin",
        "secret": "defaultpassword",
        "bind_service": ["prometheus", "grafana"],
        "bind_module": "promjob"
    },
    "ping.yml": {
        "_filepath_": "./ping_exporter/",
        "targets": [
            "8.8.8.8",
            "8.8.4.4",
            "google.com",
            "vk.com",
            "selectel.ru",
        ],
        "dns": {
            "nameserver": "9.9.9.9",
            "refresh": "30s",
        },
        "ping": {
            "interval": "2s",
            "timeout": "5s",
            "history-size": 42,
            "payload-size": 120,
        },
        "options": {
            "disableIPv6": True,
        },
        "bind_service": "ping_exporter",
        "bind_module": "file",
    },
    "ping_exporter.yml": {
        "_filepath_": "./prometheus/conf.d/",
        "bind_service": "ping_exporter",
        "bind_module": "promjob",
        "static_configs": {
            "targets": ["ping_exporter:9427"],
            "labels": {
                "status": "production",
                "type": "internal"
            }
        }
    },
    "prometheus.yml": {
        "_filepath_": "./prometheus/conf.d/",
        "scrape_interval": "5s",
        "server_name": "",
        "scheme": "http",
        "basic_auth": {
            "username": "admin",
            "password_file": "/etc/prometheus/secret.txt",
        },
        "static_configs": {
            "targets": ["localhost:9090"],
            "labels": {
                "status": "production",
                "type": "internal"
            }
        },
        "bind_service": "prometheus",
        "bind_module": "promjob"
    },
    "node_exporter.yml": {
        "_filepath_": "./prometheus/conf.d/",
        "bind_service": "node_exporter",
        "bind_module": "promjob",
        "static_configs": {
            "targets": ["172.18.0.1:9100"],
            "labels": {
                "status": "production",
                "type": "internal"
            }
        }
    },
    "snmp_exporter.yml": {
        "_filepath_": "./prometheus/conf.d/",
        "bind_service": "snmp_exporter",
        "bind_module": "promjob",
        "static_configs": {
            "targets": ["snmp_exporter:9116"],
            "labels": {
                "status": "production",
                "type": "internal"
            }
        }
    },
    "snmp_extended.yml": {
        "_filepath_": "./prometheus/conf.d/",
        "scrape_interval": "60s",
        "file_sd_configs": {
            "files": ["../snmp_targets.json"],
            "refresh_interval": "120s",
            "configs": {
                "snmp_targets.json": {
                    "_filepath_":
                    "./prometheus",
                    "data": [{
                        "labels": {
                            "status": "production",
                            "type": "external"
                        },
                        "targets": []
                    }]
                }
            }
        },
        "bind_service": "snmp_exporter",
        "bind_module": "promjob"
    },
    "snmp_interface.yml": {
        "_filepath_": "./prometheus/conf.d/",
        "scrape_interval": "20s",
        "file_sd_configs": {
            "files": ["../snmp_targets.json"],
            "refresh_interval": "120s"
        },
        "bind_service": "snmp_exporter",
        "bind_module": "promjob"
    },
    "blackbox_exporter.yml": {
        "_filepath_": "./prometheus/conf.d/",
        "bind_service": "blackbox_exporter",
        "bind_module": "promjob",
        "file_sd_configs": {
            "files": ["../blackbox_targets.json"],
            "refresh_interval": "120s",
            "configs": {
                "blackbox_targets.json": {
                    "_filepath_":
                    "./prometheus",
                    "data": [{
                        "labels": {
                            "job": "blackbox",
                            "status": "production",
                            "type": "external"
                        },
                        "targets":
                        ["http://prometheus.io", "https://prometheus.io"]
                    }]
                }
            }
        }
    },
    "blackbox.yml": {
        "_filepath_": "./prometheus/conf.d/",
        "bind_service": "blackbox_exporter",
        "bind_module": "promjob",
        "static_configs": {
            "targets": ["172.18.0.5:9115"],
            "labels": {
                "status": "production",
                "type": "internal"
            }
        }
    },
    "grafana.yml": {
        "_filepath_": "./prometheus/conf.d/",
        "server_name": "",
        "scheme": "http",
        "basic_auth": {
            "username": "admin",
            "password_file": "/etc/prometheus/secret.txt",
        },
        "static_configs": {
            "targets": ["grafana:3000"],
            "labels": {
                "status": "production",
                "type": "internal"
            }
        },
        "bind_service": "grafana",
        "bind_module": "promjob"
    },
    "datasource.yml": {
        "_filepath_": "./grafana/",
        "scheme": "http",
        "bind_service": "grafana",
        "bind_module": "datasource"
    },
}

WEB_CONFIG_FILE = os.environ.get("WEB_CONFIG_FILE", "web.yml")
ENV_FILE = os.environ.get("ENV_FILE", ".env")
DOCKER_ENV: dict = {}

CONFIG_MAPPING: dict[str, set] = {
    "prometheus": set(),
    "node_exporter": set(),
    "snmp_exporter": set(),
    "ping_exporter": set(),
    "blackbox_exporter": set(),
    "grafana": set(),
}
MESSAGE_HDR: str = "===" * 3
