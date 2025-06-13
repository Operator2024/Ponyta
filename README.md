# Ponyta

<div>

<img align="right" src="https://static.wikia.nocookie.net/pokemon/images/9/9c/Galarian_Ponyta.png/revision/latest?cb=20191009163451" alt="drawing" width="250"/>

<p align="left">

  **Ponyta** — a set of experts for monitoring (snmp, ping, node) headed by prometheus.</p>

</div>

---
<div align="center">

![Static Badge](https://img.shields.io/badge/version-1.0-lightgreen?style=flat)

</div>

### How it work

1. Fill in cgenerator.json. The repository contains a default configuration for cgenerator.json. This configuration allows you to generate configs for all exporters with http protocol and authorization.
1. Install python3 dependencies from requirements.txt file
1. Run cgenerator.py with the required flags.

```bash
usage: cgenerator.py [-h] [--force] [--prometheus] [--node-exporter] [--snmp-exporter] [--ping-exporter] [--blackbox-exporter] [--grafana]

Config generator for Ponyta services

options:
  -h, --help            show this help message and exit
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
