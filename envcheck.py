# envcheck.py
# made by Lokesh kumar termux bot
# youtube.com/termux2

# envcheck.py (Updated with Type Checking)

import os
import sys
import json
import click
from typing import List, Dict, Any, Tuple
from ruamel.yaml import YAML # Assuming ruamel.yaml is installed from previous step

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
            int(value)
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


def load_required_variables(file_path: str) -> Dict[str, str]:
    """Loads required variable names and their types from the specification file."""
    required_vars_with_types = {}
    try:
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Check for KEY: type format
                    if ':' in line:
                        key, type_str = line.split(':', 1)
                        key = key.strip()
                        type_str = type_str.strip().lower()
                    else:
                        # Default to string if no type specified
                        key = line
                        type_str = "string"
                    
                    if type_str not in VALID_TYPES:
                        click.echo(f"❌ ERROR: Invalid type '{type_str}' specified for variable '{key}'. Must be one of: {', '.join(VALID_TYPES.keys())}", err=True)
                        sys.exit(1)

                    required_vars_with_types[key] = type_str
        return required_vars_with_types
    except FileNotFoundError:
        click.echo(f"❌ ERROR: Specification file '{file_path}' not found. Did you create it?", err=True)
        sys.exit(1)

def load_dotenv_vars(file_path: str) -> dict:
    # (Function logic remains the same)
    dotenv_vars = {}
    try:
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        dotenv_vars[key.strip()] = value.strip().strip('"').strip("'")
        return dotenv_vars
    except FileNotFoundError:
        return {}


def format_output(data: dict, format_type: str):
    # (Function logic remains the same, but now includes 'type_errors')
    if format_type == 'json':
        click.echo(json.dumps(data, indent=2))
    elif format_type == 'yaml':
        yaml = YAML()
        yaml.default_flow_style = False
        yaml.indent(mapping=2, sequence=4, offset=2)
        yaml.dump(data, sys.stdout)
    else: # 'text' format (Standard CLI output)
        # Use simple text reporting logic from before, adapted for type_errors
        missing_vars = data['missing']
        empty_vars = data['empty']
        type_errors = data['type_errors']
        found_count = data['found_count']

        click.echo("\n--- 🛡️ EnvSanityCheck: Starting Sanity Check ---")

        if missing_vars:
            click.echo("\n❌ MISSING VARIABLES:")
            for var in missing_vars:
                click.echo(f"  - {var}")
            click.echo("  -> Please add these to your .env file or system environment.")

        if empty_vars:
            click.echo("\n⚠️ EMPTY VARIABLES:")
            for var in empty_vars:
                click.echo(f"  - {var}")
            click.echo("  -> These are present but have an empty value.")

        if type_errors:
            click.echo("\n🚨 TYPE MISMATCH ERRORS:")
            for error in type_errors:
                click.echo(f"  - {error['key']}: {error['message']}")
            click.echo("  -> Please ensure values match the expected type (integer, boolean, etc.).")
        
        is_failing = bool(missing_vars or empty_vars or type_errors)

        if not is_failing:
            click.echo(f"\n✅ SUCCESS! All {found_count} required variables are set correctly.")
            click.echo("--- EnvSanityCheck: Finished ---")
        else:
            total_errors = len(missing_vars) + len(empty_vars) + len(type_errors)
            click.echo(f"\n--- EnvSanityCheck: {len(missing_vars)} Missing, {len(empty_vars)} Empty, {len(type_errors)} Type Errors (Total Errors: {total_errors}) ---")
            click.echo("Please fix the errors listed above.")


@click.command()
@click.option('--spec', default=SPEC_FILE_NAME, help=f"Name of the specification file listing required variables. Default: {SPEC_FILE_NAME}")
@click.option('--format', 'output_format', default='text', type=click.Choice(VALID_FORMATS), help="Output format: 'text' (default), 'json', or 'yaml'.")
def envsanitycheck(spec: str, output_format: str):
    """
    EnvSanityCheck: Checks if all required environment variables for the project are set.
    """
    
    required_vars_with_types = load_required_variables(spec)
    if not required_vars_with_types:
        return
        
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
                found_count += 1
                # New: Type Check
                is_valid, message = check_value_type(var, value, expected_type)
                if not is_valid:
                    type_errors.append({"key": var, "expected": expected_type, "actual_value": value, "message": message})
    
    is_failing = bool(missing_vars or empty_vars or type_errors)

    # 1. Prepare Structured Data (Updated)
    report_data = {
        "status": "FAILURE" if is_failing else "SUCCESS",
        "required_count": len(required_vars_with_types),
        "found_count": found_count,
        "missing": missing_vars,
        "empty": empty_vars,
        "type_errors": type_errors, # New field
        "all_checks_passed": not is_failing
    }

    # 2. Output the Data
    format_output(report_data, output_format)

    # 3. Determine Exit Code
    if is_failing:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    envsanitycheck()
