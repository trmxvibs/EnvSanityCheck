# envcheck.py

import os
import click
from typing import List

# --- Configuration ---
SPEC_FILE_NAME = "env.spec"
DOTENV_FILE_NAME = ".env"

def load_required_variables(file_path: str) -> List[str]:
    """Loads required variable names from the specification file."""
    required_vars = []
    try:
        with open(file_path, 'r') as f:
            for line in f:
                # Ignore empty lines and comments
                line = line.strip()
                if line and not line.startswith('#'):
                    required_vars.append(line)
        return required_vars
    except FileNotFoundError:
        click.echo(f"❌ ERROR: Specification file '{file_path}' not found. Did you create it?", err=True)
        return []

def load_dotenv_vars(file_path: str) -> dict:
    """Loads variables from a simple .env file."""
    dotenv_vars = {}
    try:
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Parse KEY=VALUE format
                    if '=' in line:
                        key, value = line.split('=', 1)
                        # Remove leading/trailing quotes and spaces from value
                        dotenv_vars[key.strip()] = value.strip().strip('"').strip("'")
        return dotenv_vars
    except FileNotFoundError:
        return {}

@click.command()
@click.option('--spec', default=SPEC_FILE_NAME, help=f"Name of the specification file listing required variables. Default: {SPEC_FILE_NAME}")
def envsanitycheck(spec: str):
    """
    EnvSanityCheck: Checks if all required environment variables for the project are set.
    """
    click.echo("\n--- 🛡️ EnvSanityCheck: Starting Sanity Check ---")
    
    # 1. Load required variables list
    required_vars = load_required_variables(spec)
    if not required_vars:
        return
        
    # 2. Load available variables from .env and system environment
    dotenv_vars = load_dotenv_vars(DOTENV_FILE_NAME)
    
    # System variables take precedence over .env file variables
    all_available_vars = {**dotenv_vars, **os.environ}
    
    missing_vars = []
    empty_vars = []
    found_count = 0
    
    # 3. Start validation
    for var in required_vars:
        if var not in all_available_vars:
            missing_vars.append(var)
        else:
            value = all_available_vars[var]
            if not value:
                empty_vars.append(var)
            else:
                found_count += 1
    
    # 4. Report the output
    
    # A. Missing Variables
    if missing_vars:
        click.echo("\n❌ MISSING VARIABLES:")
        for var in missing_vars:
            click.echo(f"  - {var}")
        click.echo("  -> Please add these to your .env file or system environment.")

    # B. Empty Variables
    if empty_vars:
        click.echo("\n⚠️ EMPTY VARIABLES:")
        for var in empty_vars:
            click.echo(f"  - {var}")
        click.echo("  -> These are present but have an empty value.")

    # C. Success / Summary
    if not missing_vars and not empty_vars:
        click.echo(f"\n✅ SUCCESS! All {found_count} required variables are set correctly.")
        click.echo("--- EnvSanityCheck: Finished ---")
    else:
        click.echo(f"\n--- EnvSanityCheck: {len(missing_vars)} Missing, {len(empty_vars)} Empty ---")
        click.echo("Please fix the errors listed above.")

if __name__ == '__main__':
    envsanitycheck()