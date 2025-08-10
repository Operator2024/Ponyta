# Ponyta

<div>

<img align="right" src="https://static.wikia.nocookie.net/pokemon/images/9/9c/Galarian_Ponyta.png/revision/latest?cb=20191009163451" alt="drawing" width="250"/>

<p align="left">

  **Ponyta** — a set of experts for monitoring (snmp, ping, node) headed by prometheus.</p>

</div>

---
<div align="center">

![Static Badge](https://img.shields.io/badge/version-1.1.1-lightgreen?style=flat)

</div>

### How it work

1. Fill in cgenerator.json. The repository contains a default configuration for cgenerator.json. This configuration allows you to generate configs for all exporters with http protocol and authorization.
1. Install python3 dependencies from requirements.txt file
1. Run config_generator.py with the required flags.

```bash
usage: config_generator.py [-h] [--export_default_config] [-v] [--force] [--prometheus] [--node-exporter] [--snmp-exporter] [--ping-exporter] [--blackbox-exporter] [--grafana]

Config generator for Ponyta services, version 1.1.1-rc1

options:
  -h, --help            show this help message and exit
  --export_default_config, -export
  -v, --verbose
  --force, -f           Force overwrite
  --prometheus, -p      Generate config for prometheus
  --node-exporter, -n   Generate config for node-exporter
  --snmp-exporter, -s   Generate config for snmp-exporter
  --ping-exporter, -pe  Generate config for ping-exporter
  --blackbox-exporter, -be
                        Generate config for blackbox-exporter
  --grafana, -g

```

> Default login data for grafana, prometheus

* Username - **admin**
* Password - **defaultpassword**

> It is highly recommended to change them for your configuration.

Additionally, there is a file for cloud-init, which allows you to deploy a cloud server and prepare it for running Ponyta.

> Default data when using cloud-init

* пользователь - **ponyta**,
* пароль - **defaultpass**,
* порт - **2222**

### Project hierarchy (for default config)

```bash
├── blackbox_exporter
│   └── blackbox.yml
├── cgenerator
│   ├── grafana.py
│   ├── __init__.py
│   ├── prometheus.py
│   ├── templates
│   │   ├── grafana
│   │   │   └── datasource.jinja
│   │   └── prometheus
│   │       ├── blackbox_exporter.jinja
│   │       ├── blackbox.jinja
│   │       ├── grafana.jinja
│   │       ├── node_exporter.jinja
│   │       ├── ping_exporter.jinja
│   │       ├── prometheus.jinja
│   │       ├── snmp_exporter.jinja
│   │       ├── snmp_extended.jinja
│   │       └── snmp_interface.jinja
│   └── utils.py
├── cgenerator.json
├── cgenerator.log
├── config_generator.py
├── compose.yml
├── grafana
│   └── datasource.yml
├── passgen.sh
├── ping_exporter
│   └── ping.yml
├── prometheus
│   ├── conf.d
│   │   └── prometheus.yml
│   ├── first.rules
│   ├── prometheus.yml
│   ├── secret.txt
│   └── targets.json
├── README.md
├── requirements.txt
├── requirements-dev.txt
├── snmp.yml
└── user_data.yml
```

### 🚨🚨🚨: Documentation in working progress

### File cgenerator.json

[**cgenerator.json**](cgenerator.json) - is used to transfer data from the user to the generation script, with subsequent overwriting of the default data with the user's data.
You can override both individual fields in the config and the entire config as a whole.
In order to override for existing configs:

* From the file [defaultconfig.md](defaultconfig.md) take the necessary part of the configuration or fill in the file cgenerator.json using the example (keeping the nesting)
* Replace the values of the required parameters
* Run the config_generator.py script with the required flags.
* Check generated configs
* Using the command that the script issued at the end, run the docker compose services

🚨 The **bind_service** parameter in the config tells the script to relate to a specific service.
🚨 The **bind_module** parameter allows the script to understand which module to use to process the data.

🚨🚨🚨 **When redefining existing configurations, the parameters above can be omitted, as they are already present in the default configuration.** 🚨🚨🚨

There are currently 3 values for the **bind_module** parameter

1. **promjob** - Prometheus job
2. **datasource** - Grafana datasource
3. **file** - Simple file, example data for ping_exporter - ping.yml, or any data.

Three extension types are supported for '**file**' - yml, json, txt
