import subprocess
import os
import csv
import re
import json
import argparse
from pathlib import Path

DEBUG = False
def debug_print(message):
    """Prints a debug message if debugging is enabled.

    Args:
        message (str): The message to print if debugging is enabled.
    """
    if DEBUG:
        print(f"[DEBUG] {message}")

columns = ['Module', 'core', 'gcc', 'gcc-mva2', 'gcc-ompi', 'intel', 'intel-mva2',
           'intel-ompi', 'nvhpc', 'nvhpc-hpcx']

base_paths = {
    "manual": Path('/usr/local/pace-apps/manual/modules'),
    "spack": Path('/usr/local/pace-apps/spack/modules')
}

def get_module_avail():
    """Prints a debug message if debugging is enabled.

    Args:
        message (str): The message to print if debugging is enabled.
    """
    modules = {
        'core': [],
        'gcc': [],
        'intel': [],
        'mvapich2': [],
        'openmpi': [],
        'nvhpc': [],
        'hpcx': []
    }

    print("Retrieving module information from Spack path.")
    print("Retrieving module information from Manual path.")
    for source, base_path in base_paths.items():
        module_files = Path(base_path).glob('**/*.lua')

        for module_file in module_files:
           
            try:
                parts = module_file.relative_to(base_path / 'lmod' / 'linux-rhel9-x86_64').parts
            except ValueError:
                continue
            
            debug_print(f"Path components: {parts}")                             # Debug
            category = None

            if parts[0] == "Core":
                category = "core"
                module_name = parts[1]
            elif parts[0] in ["mvapich2", "openmpi", "hpcx"]:
                category = parts[0]
                module_name = parts[4]
            elif parts[0] == "openmpi":
                category = "openmpi"
                module_name = parts[4]
            elif parts[0] in ["gcc", "intel", "nvhpc"]:
                category = parts[0]
                module_name = parts[2]
            else:
                category = None
                module_name = None

            # Add module to its category
            if category and module_name and module_name not in modules[category]:
                modules[category].append(module_name)

    debug_print(f"Modules sorted from paths: {modules}")  # Debug
    return modules

def classify_module(module_name, category, module_usage, parts, existing_matrix):
    """Classifies a module and updates the coverage matrix.

    Args:
        module_name (str): The name of the module.
        category (str): The category of the module (e.g., gcc, core).
        module_usage (dict): Placeholder for module usage data.
        parts (list): Path components of the module file.
        existing_matrix (list): The coverage matrix to be updated.

    Returns:
        list: The updated row for the module if applicable.
    """
    existing_entry = next(
        (row for row in existing_matrix[1:] if isinstance(row, list) and row[0] == module_name),
        None
    )
    if existing_entry:
        classifications = dict(zip(columns, existing_entry))  # Start with the existing entry
    else:
        classifications = {col: "" for col in columns[1:]}  # Initialize for new entry
        classifications["Module"] = module_name

    if category == 'core':
        classifications['core'] = 'FALSE'
    elif category == 'gcc':
        classifications['gcc'] = 'FALSE'
    elif category == 'intel':
        classifications['intel'] = 'FALSE'
    elif category == 'nvhpc':
        classifications['nvhpc'] = 'FALSE'
    elif category == 'hpcx':
        classifications['nvhpc-hpcx'] = 'FALSE'
    
    elif category == 'mvapich2':
        if 'gcc' in parts:
            classifications['gcc-mva2'] = 'FALSE'
        if 'intel' in parts:
            classifications['intel-mva2'] = 'FALSE'
    elif category == 'openmpi':
        if 'gcc' in parts:
            classifications['gcc-ompi'] = 'FALSE'
        if 'intel' in parts:
            classifications['intel-ompi'] = 'FALSE'

    if existing_entry:
        row_index = existing_matrix.index(existing_entry)
        existing_matrix[row_index] = [classifications[col] for col in columns]
    else:
        row_to_add = [classifications[col] for col in columns]
        if isinstance(row_to_add, list) and len(row_to_add) == len(columns):
            existing_matrix.append(row_to_add)
            return row_to_add
        

    
def classify_environment(environment):
    """Classifies a programming environment into its testable category.

    Args:
        environment (str): The environment string to classify.

    Returns:
        str: The classification of the environment or "UNKNOWN" if not found.
    """
    classifications = {

        # These based off dry run

        # "serial+gcc-12": "gcc",
        # "parallel+gcc-12-ompi-4.1.5": "gcc-ompi",
        # "gpu-parallel+nvhpc-24.5-hpcx-2.19": "nvhpc-hpcx",
        # "parallel+intel-2021-mva2-2.3.7-1": "intel-mva2",
        # "parallel+intel-2021-ompi-4.1.5": "intel-ompi",
        # "serial+core": "core",
        # "gpu+nvhpc-24.5": "nvhpc"

        "gcc-12": "gcc",
        "intel-2021": "intel",
        "intel-2021-mva2-2.3.7-1": "intel-mva2",
        "intel-2021-ompi-4.1.5": "intel-ompi",
        "gcc-12-ompi-4.1.5": "gcc-ompi",
        "gcc-12-mva2-2.3.7-1": "gcc-mva2",
        "core": "core",
        "nvhpc-24.5": "nvhpc",
        "nvhpc-24.5-hpcx-2.19": "nvhpc-hpcx"

    }
    return classifications.get(environment, "UNKNOWN")


def run_reframe_describe():
    """Runs the ReFrame describe command and retrieves its output.

    This function executes the ReFrame `--describe` command with the specified 
    configuration file to retrieve information about all available tests. 
    The output includes details about test names, modules, and valid programming 
    environments, which are essential for generating the coverage matrix.

    How it works:
        1. The `reframe` command is executed with the `--describe` flag.
        2. The command's output is captured and split into lines.
        3. Invalid lines containing errors (e.g., FAILED, ERROR, or Traceback) 
           are filtered out.
        4. The remaining valid output lines are returned for further processing.

    Args:
        None

    Returns:
        list: A list of valid output lines from the `--describe` command, 
              which contain information about ReFrame tests.
    """
    command = "reframe -C pace/config/settings.py -c pace --describe"
    print("Retrieving test information from ReFrame.")
    debug_print(f"Running command: {command}")
    result = subprocess.run(command, capture_output=True, text=True, shell=True)
    
    output_lines = result.stdout.splitlines()
    error_lines = result.stderr.splitlines()

    if output_lines:
        valid_lines = [line for line in output_lines if not re.search(r'FAILED|ERROR|Traceback', line)]
        debug_print("Valid output from describe command:")
        debug_print("\n".join(valid_lines))
        return valid_lines

    else:
        print("No output from the describe command.")
        return []
   

def extract_describe_data(describe_output):
    """Extracts test and module data from ReFrame's describe output.

    Args:
        describe_output (list): The output from the ReFrame describe command.

    Returns:
        dict: A dictionary mapping test names to their associated modules and valid environments.
    """
    describe_data = {}

    try:
        # Parse the describe output as JSON
        data = json.loads("".join(describe_output))
        
        for test in data:
            test_name = test.get("unique_name", test.get("@class", "UnknownTest"))
            modules = test.get("modules", [])
            valid_prog_environs = test.get("valid_prog_environs", [])
            
            describe_data[test_name] = {
                'modules': modules,
                'valid_prog_environs': valid_prog_environs
            }

    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print("Raw Describe Output:")
        print("\n".join(describe_output))

    debug_print(f"Extracted Describe Data: {describe_data}")
    return describe_data

def list_modules_with_classifications(describe_data):
    """Classifies modules based on their valid programming environments.

    Args:
        describe_data (dict): The extracted describe data from ReFrame.

    Returns:
        dict: A dictionary mapping module names to their classified environments.
    """
    module_classifications = {}
    print("Classifying modules and their valid programming environments.")
    for test, data in describe_data.items():
        modules = data['modules']
        environs = data['valid_prog_environs']

        for module in modules:
            if module not in module_classifications:
                module_classifications[module] = set()

            for environ in environs:
                classified_env = classify_environment(environ)
                if classified_env != "UNKNOWN":
                    module_classifications[module].add(classified_env)

    # Print formatted results
    for module, classifications in module_classifications.items():
        debug_print(f"Tests Exists for module: {module}, Classifications: {sorted(classifications)}")
    return module_classifications

def update_matrix_with_classifications(matrix, module_classifications):
    """Updates the coverage matrix with classification data.

    Args:
        matrix (list): The coverage matrix to update.
        module_classifications (dict): The module classifications.

    Returns:
        list: The updated coverage matrix.
    """
    column_indices = {col: idx for idx, col in enumerate(matrix[0])}

    for module, classifications in module_classifications.items():
        row_idx = next((i for i, row in enumerate(matrix) if row[0] == module), None)

        if row_idx is not None:
            for classification in classifications:
                if classification in column_indices:
                    col_idx = column_indices[classification]

                    if matrix[row_idx][col_idx] == "FALSE":
                        matrix[row_idx][col_idx] = "TRUE"
    return matrix

def create_module_matrix(describe_data):
    """Creates the initial module coverage matrix.

    Args:
        describe_data (dict): The extracted describe data from ReFrame.

    Returns:
        list: The initialized coverage matrix.
    """
    module_avail = get_module_avail()
    matrix = [columns]

    for category, module_list in module_avail.items():
        for module in module_list:
            parts = []
            classify_module(module, category, {}, parts, matrix)

    return matrix
def save_to_csv(matrix, filename='test_coverage_matrix.csv'):
    """Saves the coverage matrix to a CSV file.

    Args:
        matrix (list): The coverage matrix to save.
        filename (str): The filename for the CSV file. Defaults to 'test_coverage_matrix.csv'.
    """
    try:
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(matrix)
        print(f"Test Coverage Matrix successfully created and saved to '{filename}'")
    except IOError as e:
        print(f"Error writing to CSV file: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Generates a ReFrame Coverage Matrix by analyzing module availability, "
            "compilers, and environments using ReFrame commands. "
            "The matrix tracks module coverage across different compilation and execution environments."
        ),
        epilog=(
           "How It Works:\n"
            "1. Initializes the coverage matrix with NULL values.\n"
            "2. Marks 'FALSE' for environments needing tests based on available modules.\n"
            "3. Extracts modules and environments from ReFrame's `--describe` output.\n"
            "4. Updates the matrix with 'TRUE' where tests exist.\n"
            "5. Saves the final coverage matrix to 'test_coverage_matrix.csv'.\n"
            "\nExample Usage:\n"
            "  python3 finalCoverageMatrix.py\n"
            "  python3 finalCoverageMatrix.py -C path/to/your/config-file.py\n"
            "  python3 finalCoverageMatrix.py --config-file path/to/your/config-file.py"
        ),
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        "-C", "--config-file", default="pace/config/settings.py",
        help=(
            "Path to the ReFrame configuration file. "
            "Defaults to 'pace/config/settings.py' if not specified."
        )
    )
    
    parser.add_argument(
        "--debug", 
        action="store_true", 
        help="Enable debug messages for detailed output."
    )
    args = parser.parse_args()

    DEBUG = args.debug

    print("Starting Test Coverage Matrix Generation Process")
    
    describe_output = run_reframe_describe()
    describe_data = extract_describe_data(describe_output)
    initial_matrix = create_module_matrix(describe_data)

    module_classifications = list_modules_with_classifications(describe_data)
    final_matrix = update_matrix_with_classifications(initial_matrix, module_classifications)
    save_to_csv(final_matrix)
