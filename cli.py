import os
import sys
import json
import click
from typing import List, Dict, Any, Tuple
from ruamel.yaml import YAML 
import io

# --- Configuration ---
SPEC_FILE_NAME = "env.spec"
DOTENV_FILE_NAME = ".env"
VALID_FORMATS = ['text', 'json', 'yaml']

# Define valid types and conversion attempts
VALID_TYPES = {
    "string": str,
    "integer": int,
    "float": float,
    "boolean": bool
}

def check_value_type(key: str, value: str, expected_type: str) -> Tuple[bool, str]:
    """Checks if the given value conforms to the expected type."""
    if expected_type == 'string':
        # All non-empty values are valid strings
        return True, ""
    
    # Try type conversion for numerical and boolean types
    try:
        if expected_type == 'integer':
            # Check for float format in integer type
            if '.' in value:
                 return False, f"Value '{value}' contains a decimal point. Expected strict integer."

            int(value) # Will raise ValueError if conversion fails
        elif expected_type == 'float':
            float(value)
        elif expected_type == 'boolean':
            # Accept case-insensitive 'true', 'false', '1', '0'
            lower_value = value.lower()
            if lower_value not in ('true', 'false', '1', '0'):
                return False, f"Value '{value}' is not a valid boolean (expected true/false/1/0)."
        return True, ""
    except ValueError:
        return False, f"Value '{value}' cannot be converted to type '{expected_type}'."
    except Exception as e:
        return False, f"An unexpected error occurred during type check: {e}"


def load_spec_file(spec_path: str) -> Dict[str, str]:
    """Loads required variables and their types from the env.spec YAML file."""
    yaml = YAML()
    try:
        with open(spec_path, 'r', encoding='utf-8') as f:
            data = yaml.load(f)
        
        if not isinstance(data, dict):
             raise ValueError(f"Specification file '{spec_path}' content must be a dictionary (YAML object).")

        # Normalize keys to strings, values (types) to lowercase strings
        normalized_data = {}
        for k, v in data.items():
            if isinstance(v, str):
                normalized_data[str(k).strip()] = v.lower().strip()
            else:
                raise ValueError(f"Type for variable '{k}' must be a string, not '{type(v).__name__}'.")

        # Basic validation of types
        for var, expected_type in normalized_data.items():
            if expected_type not in VALID_TYPES:
                 raise ValueError(f"Variable '{var}' specifies an unknown type: '{expected_type}'. Valid types are: {', '.join(VALID_TYPES.keys())}")

        return normalized_data
        
    except FileNotFoundError:
        click.echo(f"Error: Specification file not found at '{spec_path}'.", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error reading specification file: {e}", err=True)
        sys.exit(1)


def load_dotenv_vars(dotenv_path: str) -> Dict[str, str]:
    """Loads variables from the optional .env file (simple implementation)."""
    dotenv_vars = {}
    if os.path.exists(dotenv_path):
        try:
            with open(dotenv_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Basic parsing, handling key=value
                        if '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip().strip('"').strip("'") # Simple removal of quotes
                            if key:
                                dotenv_vars[key] = value
        except Exception as e:
            click.echo(f"Warning: Could not parse .env file: {e}", err=True)
    return dotenv_vars

def format_output(data: Dict[str, Any], output_format: str) -> str:
    """Formats the check report based on the requested output format."""
    
    if output_format == 'json':
        return json.dumps(data, indent=4)
    
    if output_format == 'yaml':
        yaml = YAML()
        yaml.indent(mapping=2, sequence=4, offset=2)
        
        # Prepare YAML output string
        output_buffer = io.StringIO()
        yaml.dump(data, output_buffer)
        return output_buffer.getvalue()

    # Default 'text' format
    report = f"\n--- 🛡️ EnvSanityCheck: Starting Sanity Check ---\n"
    
    if data['status'] == 'SUCCESS':
        report += f"\n✅ SUCCESS! All {data['required_count']} required variables are set correctly."
    else:
        report += "\n❌ VALIDATION FAILURE:\n"
        
        if data['missing']:
            report += "\n❌ MISSING VARIABLES:\n"
            for var in data['missing']:
                report += f"  - {var}\n"
            report += "  -> Please add these variables to your environment or .env file.\n"

        if data['empty']:
            report += "\n⚠️ EMPTY VARIABLES:\n"
            for var in data['empty']:
                report += f"  - {var}\n"
            report += "  -> These variables are set but empty. They must have a value.\n"

        if data['type_errors']:
            report += "\n⚠️ TYPE MISMATCH ERRORS:\n"
            for error in data['type_errors']:
                report += f"  - {error['key']} | Expected: {error['expected']} | Found: '{error['actual_value']}'\n"
                report += f"    Reason: {error['message']}\n"

        report += f"\n--- EnvSanityCheck: {len(data['missing'])} Missing, {len(data['empty'])} Empty, {len(data['type_errors'])} Type Errors (Total Errors: {len(data['missing']) + len(data['empty']) + len(data['type_errors'])}) ---\n"
        report += "Please fix the errors listed above."

    report += "\n--- EnvSanityCheck: Finished ---\n"
    
    return report

@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.option('--spec', default=SPEC_FILE_NAME, help='Name of the specification file listing required variables. Default: env.spec')
@click.option('--format', type=click.Choice(VALID_FORMATS), default='text', help="Output format: 'text' (default), 'json', or 'yaml'.")
def envsanitycheck(spec: str, format: str):
    """
    EnvSanityCheck: Checks if all required environment variables for the project are set.
    """
    
    required_vars_with_types = load_spec_file(spec)

    # Load variables from .env file and then os.environ (OS environment wins)
    dotenv_vars = load_dotenv_vars(DOTENV_FILE_NAME)
    all_available_vars = {**dotenv_vars, **os.environ}
    
    missing_vars = []
    empty_vars = []
    type_errors = []
    found_count = 0
    
    for var, expected_type in required_vars_with_types.items():
        if var not in all_available_vars:
            missing_vars.append(var)
        else:
            value = all_available_vars[var]
            if not value:
                empty_vars.append(var)
            else:
                # New: Type Check
                is_valid, message = check_value_type(var, value, expected_type)
                if not is_valid:
                    type_errors.append({"key": var, "expected": expected_type, "actual_value": value, "message": message})
                else:
                    found_count += 1
    
    is_failing = bool(missing_vars or empty_vars or type_errors)

    # Prepare Structured Data
    report_data = {
        "status": "FAILURE" if is_failing else "SUCCESS",
        "required_count": len(required_vars_with_types),
        "found_count": found_count,
        "missing": missing_vars,
        "empty": empty_vars,
        "type_errors": type_errors,
        "all_checks_passed": not is_failing
    }
    
    # Output the report
    report = format_output(report_data, format)
    click.echo(report)
    
    # Exit with appropriate code for CI/CD pipeline
    if is_failing:
        sys.exit(1)
    
    # Success exit code 0 is implied if sys.exit(1) is not called.


if __name__ == '__main__':
    envsanitycheck()
