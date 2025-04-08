# reframe-coverage-report

This utility is designed to generate a test coverage matrix for software modules within Georgia Tech’s High-Performance Computing (HPC) environment, PACE. The tool integrates with the [ReFrame](https://reframe-hpc.readthedocs.io/) testing framework and extracts information from installed module paths to determine which software modules have test coverage under different compiler and MPI environments.

---

## 🔍 About PACE

[PACE](https://pace.gatech.edu/) (Partnership for an Advanced Computing Environment) is Georgia Tech’s centralized HPC cluster, designed to support computational research. PACE supports multiple software toolchains (e.g., GCC, Intel, NVHPC), as well as MPI libraries (e.g., OpenMPI, MVAPICH2, HPCX), and uses the [LMOD](https://lmod.readthedocs.io/en/latest/) environment module system to organize software modules in a structured hierarchy.

This script navigates these module hierarchies and cross-references the data with the ReFrame testing suite to produce a CSV matrix representing test coverage.

---

## Prerequisites

- **Access to PACE**: This script is designed to run within the PACE HPC environment. You must be a Georgia Tech researcher with login access.
- **ReFrame Installed**: The ReFrame testing framework must be installed and configured.
- **Python 3.8+**: Used to execute the coverage script.
- **PACE Module Access**: The module system should be accessible and the appropriate modules must be loaded.

---

## Directory Structure Assumptions

This script assumes that PACE follows the typical `LMOD`-compliant hierarchy:

```
/usr/local/pace-apps/manual/packages/<app>/pace-modules/lmod/linux-rhel9-x86_64/Core/<app>/<version>.lua
/usr/local/pace-apps/manual/packages/<app>/pace-modules/lmod/linux-rhel9-x86_64/<compiler>/<version>/<app>/<version>.lua
/usr/local/pace-apps/manual/packages/<app>/pace-modules/lmod/linux-rhel9-x86_64/<mpi>/<mpi-version>/<compiler>/<compiler-version>/<app>/<version>.lua
```

---

##  How to Run the Coverage Matrix Script

Follow these instructions to generate a test coverage matrix from a PACE login node.

---

### Step 1: SSH into PACE

SSH into **Phoenix** using either of the following login nodes:

```bash
ssh <your-gt-username>@login-phoenix-rh9.pace.gatech.edu
```

OR (dev node)

```bash
ssh <your-gt-username>@login-phx-dev-rh9.pace.gatech.edu
```

---

### Step 2: Navigate to Your ReFrame Directory

Change into the directory containing your ReFrame installation and configuration:

```bash
cd /path/to/your/reframe
```

---

### Step 3: Load ReFrame Module

Load the ReFrame module provided by PACE. This makes the `reframe` command available and ensures proper paths are set:

```bash
module load reframe
```

---

### Step 4: Run the Coverage Script

The script used to generate the test coverage matrix is located in:

```
temp_utilities/test_coverage_matrix.py
```

Run it with the following command:

```bash
python3 temp_utilities/test_coverage_matrix.py -C pace/config/settings.py
```

- The `-C` flag specifies the path to your ReFrame configuration file.
- This command will scan available modules and generate a CSV matrix showing whether each module has test coverage under each programming environment (core, gcc, intel, etc.).

---

### Debug Mode

For verbose output and internal debug logging, use the `--debug` flag:

```bash
python3 temp_utilities/test_coverage_matrix.py -C pace/config/settings.py --debug
```

This will print statements showing how modules are being parsed, categorized, and matched with existing tests.

---

## Output

The script will output a file named `test_coverage_matrix.csv` in your working directory.

- Rows = Software modules
- Columns = Programming environments (core, gcc, intel, gcc-mva2, gcc-ompi, etc.)
- Values = `TRUE` (test exists), `FALSE` (required but no test), `NULL` (not applicable)

You can open this file with any spreadsheet program (Excel, Google Sheets, etc.) or use Python's `pandas` or `matplotlib` for visualization.

---

##  Example Use Case

Let’s say you're a system administrator at Georgia Tech and want to see whether the `netcdf-c` module has been tested under `intel` and `gcc-mva2`. After running the script, you’ll be able to check the output CSV and find that `netcdf-c` has test coverage under `gcc-mva2` but **not** under `intel`. This allows you to prioritize writing tests where they are missing.

---

## 👥 Authors

**Edison Lee**  
Bachelor of Science in Computer Science  
Georgia Institute of Technology

---

## 📘 References

- [ReFrame Documentation](https://reframe-hpc.readthedocs.io/en/stable/)
- [PACE at Georgia Tech](https://pace.gatech.edu/)
- [LMOD Documentation](https://lmod.readthedocs.io/en/latest/)
- [Python Software Foundation](https://www.python.org/)
