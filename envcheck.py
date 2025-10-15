# envcheck.py
# made by Lokesh kumar termux bot
# youtube.com/termux2

import os
import sys
import json # JSON module for output
import click
from typing import List
# Note: Requires 'ruamel.yaml' to be installed (pip install ruamel.yaml)
try:
    from ruamel.yaml import YAML
except ImportError:
    YAML = None

# --- Configuration ---
SPEC_FILE_NAME = "env.spec"
DOTENV_FILE_NAME = ".env"
VALID_FORMATS = ['text', 'json', 'yaml']

def load_required_variables(file_path: str) -> List[str]:
    # (Function logic remains the same)
    required_vars = []
    try:
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    required_vars.append(line)
        return required_vars
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
    """Formats the final report data into the specified format (JSON, YAML, or text)."""
    if format_type == 'json':
        click.echo(json.dumps(data, indent=2))
    elif format_type == 'yaml':
        if YAML is None:
             click.echo("❌ ERROR: ruamel.yaml not installed. Run 'pip install ruamel.yaml' for YAML output.", err=True)
             sys.exit(1)
        yaml = YAML()
        yaml.default_flow_style = False
        yaml.indent(mapping=2, sequence=4, offset=2)
        yaml.dump(data, sys.stdout)
    else: # 'text' format (Standard CLI output)
        missing_vars = data['missing']
        empty_vars = data['empty']
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
        
        is_failing = bool(missing_vars or empty_vars)

        if not is_failing:
            click.echo(f"\n✅ SUCCESS! All {found_count} required variables are set correctly.")
            click.echo("--- EnvSanityCheck: Finished ---")
        else:
            click.echo(f"\n--- EnvSanityCheck: {len(missing_vars)} Missing, {len(empty_vars)} Empty ---")
            click.echo("Please fix the errors listed above.")


@click.command()
@click.option('--spec', default=SPEC_FILE_NAME, help=f"Name of the specification file listing required variables. Default: {SPEC_FILE_NAME}")
@click.option('--format', 'output_format', default='text', type=click.Choice(VALID_FORMATS), help="Output format: 'text' (default), 'json', or 'yaml'.")
def envsanitycheck(spec: str, output_format: str):
    """
    EnvSanityCheck: Checks if all required environment variables for the project are set.
    """
    
    required_vars = load_required_variables(spec)
    if not required_vars:
        return
        
    dotenv_vars = load_dotenv_vars(DOTENV_FILE_NAME)
    all_available_vars = {**dotenv_vars, **os.environ}
    
    missing_vars = []
    empty_vars = []
    found_count = 0
    
    for var in required_vars:
        if var not in all_available_vars:
            missing_vars.append(var)
        else:
            value = all_available_vars[var]
            if not value:
                empty_vars.append(var)
            else:
                found_count += 1
    
    is_failing = bool(missing_vars or empty_vars)

    # 1. Prepare Structured Data
    report_data = {
        "status": "FAILURE" if is_failing else "SUCCESS",
        "required_count": len(required_vars),
        "found_count": found_count,
        "missing": missing_vars,
        "empty": empty_vars,
        "all_checks_passed": not is_failing
    }

    # 2. Output the Data
    format_output(report_data, output_format)

    # 3. Determine Exit Code (for CI/CD compatibility)
    if is_failing:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    envsanitycheck()

