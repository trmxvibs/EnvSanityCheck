# EnvSanityCheck: The Advanced Environment Validator

[![CI Status](https://github.com/trmxvibs/EnvSanityCheck/actions/workflows/ci.yml/badge.svg)](https://github.com/trmxvibs/EnvSanityCheck/actions/workflows/ci.yml)

### Don't let a missing or malformed configuration ruin your deployment. 
### EnvSanityCheck is a robust, lightweight Python CLI tool that guarantees all your project's essential environment variables are correctly defined and typed. 
### It's the ultimate gatekeeper for your project's configuration integrity.

---

## Key Features
| Feature | Description | Benefit |
| :--- | :--- | :--- |
| **Type Validation** | Checks for integer, boolean, and float types, preventing errors like setting `PORT="eighty"`. | Ensures data integrity at setup. |
| **CI/CD Ready** | Uses standard Exit Codes (0/1) to automatically fail deployment pipelines if configuration is wrong. | Essential for automated deployments. |
| **Structured Output** | Provides reports in plain text, JSON, or YAML format. | Allows easy integration with other scripts and tools. |
| **Cross-Platform** | Works with Python, Node.js, Go, PHP, Java, and any project using `.env` files. | Universal utility for any developer team. |
| **Smart Parsing** | Correctly handles inline comments (`# comments`) in your `.env` file values. | More flexible and developer-friendly. |

---

## Quick Start: Installation
### 1. Prerequisites

You need **Python 3.6+** installed.

### 2. Installation (Recommended)

EnvSanityCheck is installed directly from PyPI. This is the simplest way to use the tool in any environment (including CI/CD, Linux, or Windows).

```bash
pip install envsanitycheck
```

### 3. Development Setup (Optional)
If you wish to contribute or run tests:
```sh
git clone [https://github.com/trmxvibs/EnvSanityCheck.git](https://github.com/trmxvibs/EnvSanityCheck.git)
cd EnvSanityCheck
```

### Install the package and its dependencies in editable mode
```sql
pip install -e .
```

## A to Z Configuration & Usage

The tool operates based on a single blueprint file: `env.spec`

### Step 1: Define the Specification (env.spec)

Create a file named `env.spec` in your project root.
Specify both the variable name and its expected type using the format:
```bash
KEY: type
```
## Supported Types

| Type             | Example                                          |
| ---------------- | ------------------------------------------------ |
| string (default) | `DATABASE_URL: string`                           |
| integer          | `SERVICE_PORT: integer`                          |
| float            | `APP_TIMEOUT_SECONDS: float`                     |
| boolean          | `DEBUG_MODE: boolean` (accepts `true/false/1/0`) |

## Example env.spec:
```bash
# env.spec

DATABASE_URL: string
SERVICE_PORT: integer
DEBUG_MODE: boolean
MAX_REQUESTS: integer
```
## Step 2: Run the Validation

Execute the script from your terminal:
```sh
envcheck
```

## Reporting: Understanding the Output

The tool checks for three distinct failure modes:

### A. Core Failure Modes (Text Output)
| Status            | Symbol | Description                                                                                                          |
| ----------------- | ------ | -------------------------------------------------------------------------------------------------------------------- |
| **MISSING**       | ❌      | The variable is required in `env.spec` but not found anywhere.                                                       |
| **EMPTY**         | ⚠️     | The variable is present but has an empty value (e.g., `KEY=`).                                                       |
| **TYPE MISMATCH** | 🚨     | The variable is found, but the value cannot be converted to the expected type (e.g., setting an integer to `"ten"`). |

## Example Output (Failure):


```sql
--- 🛡️ EnvSanityCheck: Starting Sanity Check ---

🚨 TYPE MISMATCH ERRORS:
  - SERVICE_PORT: Value 'eighty' cannot be converted to type 'integer'.
  -> Please ensure values match the expected type (integer, boolean, etc.).

--- EnvSanityCheck: 0 Missing, 0 Empty, 1 Type Errors (Total Errors: 1) ---
Please fix the errors listed above.
```
## B. Structured Output (For Integration)

Use the --format flag to get machine-readable output.
This is vital for integrating the tool into shell scripts or other programs.

| Format | Command                            | Example Use Case                                                   |
| ------ | ---------------------------------- | ------------------------------------------------------------------ |
| JSON   | `python envcheck.py --format json` | Easily read configuration errors into a Node.js or Python program. |
| YAML   | `python envcheck.py --format yaml` | Ideal for use in advanced CI/CD pipelines or Ansible scripts.      |

### Example JSON Output (Failure):
```json
{
  "status": "FAILURE",
  "required_count": 4,
  "found_count": 4,
  "missing": [],
  "empty": [],
  "type_errors": [
    {
      "key": "SERVICE_PORT",
      "expected": "integer",
      "actual_value": "eighty",
      "message": "Value 'eighty' cannot be converted to type 'integer'."
    }
  ],
  "all_checks_passed": false
}
```
## CI/CD Integration

EnvSanityCheck makes integration simple by using standard UNIX exit codes:

Exit Code 0: All checks passed (✓)

Exit Code 1: One or more errors found (Missing, Empty, or Type Mismatch)


### Example in a CI/CD pipeline:

```bash
# Example CI/CD stage
echo "Checking Environment Configuration..."
python envcheck.py

# The pipeline will automatically stop here if the exit code is 1 (failure)
echo "Configuration validated successfully. Starting deployment."
```

# ❓ FAQ: Clarifying the Scope

Here are common questions regarding the scope and purpose of EnvSanityCheck:

### 1. How is EnvSanityCheck different from Pydantic Settings?

Pydantic Settings is the **gold standard for configuration validation at the application runtime** (inside the Python application). EnvSanityCheck is a **CLI utility for pre-runtime, CI/CD validation**.

| Feature | EnvSanityCheck | Pydantic Settings |
| :--- | :--- | :--- |
| **Validation Point** | CI/CD Pre-Check (Fails the build fast) | Application Runtime (Fails on app start) |
| **Scope** | **Language-Agnostic** (Validates config for Node/Go/PHP/Python) | Python-only |
| **Data Types** | Basic types (string, integer, boolean) | Advanced structures (complex types, models, etc.) |

### 2. Should I use this to validate Production Secrets?

**No, absolutely not.** Production secrets (API keys, credentials) should never be stored in plaintext files in the repository or validated directly within the CI pipeline.

* **Best Practice:** Secrets should be loaded at runtime from a secure **Secrets Vault** (e.g., HashiCorp Vault, AWS Secrets Manager) and validated by the application's runtime logic (e.g., Pydantic).
* **EnvSanityCheck Use:** The tool is designed to validate **non-sensitive infrastructure configuration** (e.g., `SERVICE_PORT`, `LOG_LEVEL`, `DEBUG_MODE`) and catch configuration drift errors in **development** and **staging** environments *before* a deployment starts.




## Contribution & License

We welcome contributions!
Please check the CONTRIBUTING.md file for guidelines on reporting bugs and submitting features.

This project is licensed under the MIT License.























