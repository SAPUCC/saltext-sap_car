# SaltStack SAPCAR extension
This SaltStack extention allows the handling of SAPCAR archives over states. Right now,
only extraction is supported as it is the biggest use case.

**THIS PROJECT IS NOT ASSOCIATED WITH SAP IN ANY WAY**

## Installation
Run the following to install the SaltStack SAPCAR extension:
```bash
salt-call pip.install saltext-sap_car
```
Keep in mind that this package must be installed on every minion that should utilize the states and
execution modules.

## Usage
A state using the SAPCAR extension looks like this:
```jinja
SAProuter is extracted:
  sap_car.extracted:
    - name: /mnt/nfs/saprouter.sar
    - output_dir: /usr/sap/saprouter/
    - user: root
    - group: root
    - require:
      - pkg: SAPCAR is installed
```

## Docs
See https://saltext-sap-car.readthedocs.io/ for the documentation.

## Contributing
We would love to see your contribution to this project. Please refer to `CONTRIBUTING.md` for further details.

## License
This project is licensed under GPLv3. See `LICENSE.md` for the license text and `COPYRIGHT.md` for the general copyright notice.
