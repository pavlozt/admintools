# [Atop](https://github.com/Atoptool/atop) Data Analysis with Python

Despite the fact that there are many traditional monitoring systems that store data in a convenient form for analysis, sometimes you need to make a decision when there is only the [atop](https://github.com/Atoptool/atop) program and it has already accumulated a lot of data.

In this examples, we will process data from such servers and make conclusions:

- [CPU scaling report](cpu_scaling.ipynb)


## Prerequisites

- `atop` installed on the remote and local machines.
- Python with `pandas` and `matplotlib`.
- SSH access to the target server with `ssh-agent` configured for passwordless authentication.


## Implementation specific

Sometimes, when the ATOP version is different remotely and locally, incompatibility may occur. In this case, you will have to use the `atopconvert(1)` program. The raw input file should be at least of version 2.0.
