#  EnvSanityCheck: Environment Variable Validator

A **minimal, multi-language compatible Python CLI tool** that validates whether all required environment variables are present and non-empty **before running your project**.

Stop wasting time debugging deployment failures caused by missing `.env` variables!  

---

##  Key Features & Benefits

 **Multi-Language Compatible**  
Works seamlessly with **Python, Node.js, PHP, Java, Go**, and more — since it only checks `.env` files and system environment variables.

 **Team Productivity**  
Ensures every new developer sets up their environment correctly using a single `env.spec` blueprint.

 **Clear Feedback**  
Output for:
```sql
-  **Missing** variables
-  **Empty** variables
-  **All good** when everything is set correctly.
```
 **Lightweight & Fast**  
No complex dependencies or deep code scanning. Just a quick, reliable sanity check.

---

##  Installation & Setup

### 1. Prerequisite
Ensure you have **Python 3.6+** installed on your system (Windows, macOS, or Linux).

### 2. Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/YourUsername/EnvSanityCheck.git
cd EnvSanityCheck
pip install -r requirements.txt
```
##  Configuration (The Blueprint)

The core of EnvSanityCheck is the env.spec file — a simple text file listing all required environment variables.

### 1. Create the env.spec File

Place it in your project’s root directory (where your .env file usually resides).

### 2. Define Required Variables

Each line should contain a single variable name. Comments starting with # are ignored.

Example env.spec

```nginx
# Environment variable blueprint
DATABASE_URL       # The database connection string
API_SECRET_KEY     # Key required for API authentication
SERVICE_PORT       # Port number for the application
```
### Tip:
You can document each variable using comments for better team readability.

## Usage

Run the tool from your project root
```sh
python envchek.py
```
## Optional Arguments
| Argument | Default    | Description                                                                          |
| -------- | ---------- | ------------------------------------------------------------------------------------ |
| `--spec` | `env.spec` | Specify a different blueprint file (e.g., `python envcheck.py --spec prod.env.spec`) |

## Output & Reporting
EnvSanityCheck provides three clear statuses:

###  1. Success

All required variables are present and non-empty.

```sql
---  EnvSanityCheck: Starting Sanity Check ---

 SUCCESS! All 3 required variables are set correctly.

--- EnvSanityCheck: Finished ---
```

### 2. Missing Variables

A variable listed in env.spec was not found in .env or your system environment.
```shell
 MISSING VARIABLES:
  - LOG_LEVEL
  -> Action: Add 'LOG_LEVEL=...' to your .env file.
```

### Empty Variables

A variable was found, but its value is blank.

```csharp
 EMPTY VARIABLES:
  - DATABASE_URL
  -> Action: This variable is present but needs a valid value (e.g., DATABASE_URL="connection_string").
```


##  How It Works (For Contributors)

Read Blueprint: Loads all variable names from the env.spec file.

Gather Configuration: Reads both .env and os.environ (system variables), giving system variables higher priority.

Validate: Compares the required variables against the loaded configuration.

Report: Prints a clean summary with color-coded results.

This approach keeps the tool small, portable, and language-agnostic — ideal for all types of projects.

## Contribution

We welcome all contributions!

 Report Bugs: Open an issue describing the problem.

 Suggest Features: We might add JSON/YAML output, automatic checks, or CI/CD integration in future versions.

 Submit PRs: Fork the repo, implement your changes, and open a pull request.

 

## Support

If you like EnvSanityCheck, give it a ⭐ on GitHub and share it with your team!
Let’s make environment setup simple and foolproof for everyone.











