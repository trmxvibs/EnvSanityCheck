# tests/test_cli.py

import pytest
import os
from click.testing import CliRunner
from envsanitycheck.cli import envsanitycheck, check_value_type

# --- 1. Testing Core Logic: check_value_type ---

# Test cases for successful type validation
@pytest.mark.parametrize("value, expected_type", [
    ("hello", "string"),
    ("123", "integer"),
    ("3.14", "float"),
    ("True", "boolean"),
    ("false", "boolean"),
    ("1", "boolean"),
    ("0", "boolean"),
])
def test_check_value_type_success(value, expected_type):
    """Tests if valid values pass type checks."""
    is_valid, message = check_value_type("KEY", value, expected_type)
    assert is_valid is True
    assert message == ""

# Test cases for failing type validation
@pytest.mark.parametrize("value, expected_type", [
    ("abc", "integer"),  # String instead of Integer
    ("abc", "float"),    # String instead of Float
    ("yes", "boolean"),  # Invalid boolean
    ("1.0", "integer"),  # Float instead of Integer (should fail strict int check)
])
def test_check_value_type_failure(value, expected_type):
    """Tests if invalid values fail type checks and return a message."""
    is_valid, message = check_value_type("KEY", value, expected_type)
    assert is_valid is False
    assert message != ""

# --- 2. Testing CLI Command (Integration) ---

@pytest.fixture
def runner():
    """Provides the CliRunner for testing the command line interface."""
    return CliRunner()

# Test case for a successful run (No errors)
def test_cli_success(runner, tmp_path):
    """Mocks environment and spec file for a successful run."""
    # 1. Create temporary env.spec file
    spec_file = tmp_path / "env.spec"
    spec_file.write_text("API_KEY: string\nSERVICE_PORT: integer")

    # 2. Mock environment variables for the test
    os.environ['API_KEY'] = 'test-key'
    os.environ['SERVICE_PORT'] = '8000'

    # 3. Run the CLI command
    result = runner.invoke(envsanitycheck, ['--spec', str(spec_file)])

    # 4. Assertions
    assert result.exit_code == 0
    assert "SUCCESS" in result.output
    assert "All 2 required variables are set correctly." in result.output

    # Cleanup (important for os.environ)
    del os.environ['API_KEY']
    del os.environ['SERVICE_PORT']


# Test case for a failing run (Missing Variable)
def test_cli_failure_missing_var(runner, tmp_path):
    """Tests CLI failure when a required variable is missing."""
    spec_file = tmp_path / "env.spec"
    spec_file.write_text("REQUIRED_BUT_MISSING: string")

    # Run the CLI command
    result = runner.invoke(envsanitycheck, ['--spec', str(spec_file)])

    # Assertions
    assert result.exit_code == 1 # Command must exit with failure
    assert "❌ MISSING VARIABLES:" in result.output
    assert "REQUIRED_BUT_MISSING" in result.output
