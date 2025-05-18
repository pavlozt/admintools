# [Atop](https://github.com/Atoptool/atop) data analysis with Python

Despite the fact that there are many traditional monitoring systems that store data in a convenient form for analysis, sometimes you need to make a decision when there is only the [atop](https://github.com/Atoptool/atop) program and it has already accumulated a lot of data.

The repository contains a module for interaction with Atop ([pandas_atop_reader.py](pandas_atop_reader.py)) and notebooks with usage examples:

- [CPU scaling report](cpu_scaling.ipynb)


## Prerequisites

- `atop` installed on the remote and local machines.
- Python with `pandas` and `matplotlib`.
- SSH access to the target server with `ssh-agent` configured for passwordless authentication.


## Implementation specific

Sometimes, when the Atop version is different remotely and locally, incompatibility may occur. In this case, you will have to use the `atopconvert(1)` program. The raw input file should be at least of version 2.0. You can also execute converting metrics into text on remote host.