# SaltStack SAPCAR extension
This SaltStack extention allows the handling of SAPCAR archives over states. Right now,
only extraction is supported as it is the biggest use case.

**THIS PROJECT IS NOT ASSOCIATED WITH SAP IN ANY WAY**

## Installation
Run the following to install the SaltStack SAPCAR extension:
```bash
salt-call pip.install saltext.sap-car
```
Keep in mind that this package must be installed on every minion that should utilize the states and
execution modules.

Alternatively, you can add this repository directly over gitfs
```yaml
gitfs_remotes:
  - https://github.com/SAPUCC/saltext-sap_car.git:
    - root: src/saltext/sap_car
```
In order to enable this, logical links under `src/saltext/sap_car/` from `<dir_type>` (where the code lives) to `<dir_type>` have been placed, e.g. `modules` -> `_modules`. This will double the source data during build, but:
 * `_modules` is required for integrating the repo over gitfs
 * `modules` is required for the salt loader to find the modules / states

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
