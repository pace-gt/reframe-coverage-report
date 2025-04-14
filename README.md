# reframe-coverage-report

This utility is designed to generate a test coverage matrix for software modules within a HPC environment. The tool integrates with the [ReFrame](https://reframe-hpc.readthedocs.io/) testing framework and extracts information from installed module paths to determine which software modules have test coverage under different compiler and MPI environments.

---

## 🔍 About PACE

[PACE](https://pace.gatech.edu/) (Partnership for an Advanced Computing Environment) is Georgia Tech’s centralized HPC cluster, designed to support computational research. PACE supports multiple software toolchains (e.g., GCC, Intel, NVHPC), as well as MPI libraries (e.g., OpenMPI, MVAPICH2, HPCX), and uses the [LMOD](https://lmod.readthedocs.io/en/latest/) environment module system to organize software modules in a structured hierarchy.

This script navigates these module hierarchies and cross-references the data with the ReFrame testing suite to produce a CSV matrix representing test coverage.

---

## Prerequisites

- Python 3.8+
- ReFrame installed and accessible via `module load reframe`
- Access to an HPC environment that uses the LMOD module system

---

## Directory Structure Assumptions

The tool assumes your modulefiles follow the LMOD hierarchical pathing standard. These are typically structured as:

```text
<path to module>/lmod/linux-rhel9-x86_64/Core/<app>/<version>.lua
<path to module>/lmod/linux-rhel9-x86_64/<compiler>/<version>/<app>/<version>.lua
<path to module>/lmod/linux-rhel9-x86_64/<mpi>/<mpi-version>/<compiler>/<compiler-version>/<app>/<version>.lua
```

---

##  How to Run the Coverage Matrix Script

Follow these instructions to generate a test coverage matrix.

---

### Step 1: SSH into your HPC environment’s login node

 ```bash
 ssh <your-username>@<login-node>
 ```
---

### Step 2: Navigate to Your ReFrame Directory

Change into the directory containing your ReFrame installation and configuration:

```bash
cd <path-to-your-reframe-directory>
```

---

### Step 3: Load ReFrame Module

Load the ReFrame module. This makes the `reframe` command available and ensures proper paths are set:

```bash
module load reframe
```

---

### Step 4: Run the Coverage Script

Once you're in the ReFrame repository directory and have loaded the necessary modules, run the coverage matrix script using the following command format:

```bash
python3 <path-to-script>/test_coverage_matrix.py -C <path-to-config>/settings.py
```

- The `-C` flag specifies the path to your ReFrame configuration file.
- This command will scan available modules and generate a CSV matrix showing whether each module has test coverage under each programming environment (i.e., core, gcc, intel, etc.).

---

### Debug Mode

For verbose output and internal debug logging, use the `--debug` flag:

```bash
python3 <path-to-script>/test_coverage_matrix.py -C <path-to-config>/settings.py
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

If you want to see whether the `netcdf-c` module has been tested under `intel` and `gcc-mva2`. After running the script, you’ll be able to check the output CSV and find that `netcdf-c` may have test coverage under `gcc-mva2` but **not** under `intel`, effectively allowing you to prioritize writing tests where they are missing.

---

## 👥 Author

**Edison Lee**  
Bachelor of Science in Computer Science  
Georgia Institute of Technology

---
## Acknowledgements

This project was made possible thanks to the guidance and support of my advisors:

- **Dr. Fang Liu**, Senior Research Scientist, Georgia Tech PACE
- **Ronald Rahman**, Research Scientist II, Georgia Tech PACE

---

## 📘 References

- [ReFrame Documentation](https://reframe-hpc.readthedocs.io/en/stable/)
- [PACE at Georgia Tech](https://pace.gatech.edu/)
- [LMOD Documentation](https://lmod.readthedocs.io/en/latest/)
- [Python Software Foundation](https://www.python.org/)
