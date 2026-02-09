#!/usr/bin/env python3
"""
Klaviyo Skill Pack Setup Wizard

Interactive setup tool for configuring the Klaviyo Skill Pack.
Guides non-technical users through API key setup, environment
configuration, dependency installation, and health checks.

Usage:
    python scripts/setup.py
    python scripts/setup.py --skip-install
    python scripts/setup.py --skills klaviyo,shopify
    python scripts/setup.py --non-interactive
"""

import os
import sys
import stat
import subprocess
import argparse
import getpass
from pathlib import Path


# ANSI color codes
class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    END = "\033[0m"


SKILLS = {
    "klaviyo-analyst": {
        "label": "Klaviyo (Analyst)",
        "env_vars": {
            "KLAVIYO_API_KEY": {
                "prompt": "Klaviyo Private API Key (starts with pk_)",
                "instructions": (
                    "Get your key: Klaviyo > Settings > API Keys > "
                    "Create Private API Key (read-only scopes)"
                ),
                "validation": lambda v: v.startswith("pk_") and len(v) > 10,
                "error": "Key should start with 'pk_' and be 36+ characters",
            },
        },
        "requirements": "requirements.txt",
        "health_check": None,  # Needs MCP server, not a script
    },
    "klaviyo-developer": {
        "label": "Klaviyo (Developer)",
        "env_vars": {
            "KLAVIYO_API_KEY": {
                "prompt": "Klaviyo Private API Key (same key as Analyst)",
                "instructions": "Uses the same key as klaviyo-analyst",
                "validation": lambda v: v.startswith("pk_") and len(v) > 10,
                "error": "Key should start with 'pk_' and be 36+ characters",
            },
        },
        "requirements": "requirements.txt",
        "health_check": None,
    },
    "google-analytics": {
        "label": "Google Analytics (GA4)",
        "env_vars": {
            "GOOGLE_ANALYTICS_PROPERTY_ID": {
                "prompt": "GA4 Property ID (numeric, found in Admin > Property Settings)",
                "instructions": (
                    "In GA4: Admin > Property Settings > Property ID (number only)"
                ),
                "validation": lambda v: v.isdigit(),
                "error": "Property ID should be a number (e.g., 123456789)",
            },
            "GOOGLE_APPLICATION_CREDENTIALS": {
                "prompt": "Path to Google service account JSON file",
                "instructions": (
                    "Google Cloud Console > IAM & Admin > Service Accounts > "
                    "Create > Download JSON key"
                ),
                "validation": lambda v: os.path.exists(v),
                "error": "File not found at that path",
            },
        },
        "requirements": "requirements.txt",
        "health_check": "scripts/ga_client.py --days 7 --metrics sessions",
    },
    "shopify": {
        "label": "Shopify",
        "env_vars": {
            "SHOPIFY_STORE_URL": {
                "prompt": "Shopify store URL (e.g., https://my-store.myshopify.com)",
                "instructions": (
                    "Your .myshopify.com URL (not your custom domain)"
                ),
                "validation": lambda v: "myshopify.com" in v or v.startswith("https://"),
                "error": "Should be your .myshopify.com URL",
            },
            "SHOPIFY_ACCESS_TOKEN": {
                "prompt": "Shopify Admin API access token (starts with shpat_)",
                "instructions": (
                    "Shopify Admin > Settings > Apps > Develop apps > "
                    "Create app > Install > Copy Admin API access token"
                ),
                "validation": lambda v: v.startswith("shpat_") and len(v) > 10,
                "error": "Token should start with 'shpat_'",
            },
        },
        "requirements": "requirements.txt",
        "health_check": "scripts/shopify_client.py --resource shop",
    },
    "looker-studio": {
        "label": "Looker Studio",
        "env_vars": {
            "GOOGLE_SHEETS_CREDENTIALS_PATH": {
                "prompt": "Path to Google service account JSON file (for Sheets API)",
                "instructions": (
                    "Google Cloud Console > Enable Sheets API + Drive API > "
                    "Service Accounts > Create > Download JSON key"
                ),
                "validation": lambda v: os.path.exists(v),
                "error": "File not found at that path",
            },
        },
        "requirements": "requirements.txt",
        "health_check": "scripts/data_pipeline.py --action list-templates",
    },
}


class SkillPackSetup:
    """Interactive setup wizard for the Klaviyo Skill Pack."""

    def __init__(self, pack_dir: Path, skills_filter: list = None, non_interactive: bool = False):
        self.pack_dir = pack_dir
        self.skills_filter = skills_filter
        self.non_interactive = non_interactive
        self.collected_keys = {}
        self.configured_skills = []
        self.skipped_skills = []
        self.errors = []

    def run(self, skip_install: bool = False):
        """Main wizard flow."""
        self._print_banner()

        # Step 1: Prerequisites
        self._print_step(1, 5, "Checking prerequisites")
        if not self.check_prerequisites():
            return

        # Step 2: Collect API keys
        self._print_step(2, 5, "Configuring API keys")
        self.collect_api_keys()

        if not self.configured_skills:
            self._print_warning("No skills were configured. Run again when you have API keys ready.")
            return

        # Step 3: Create .env files
        self._print_step(3, 5, "Creating configuration files")
        self.create_env_files()

        # Step 4: Install dependencies
        if not skip_install:
            self._print_step(4, 5, "Installing Python packages")
            self.install_dependencies()
        else:
            self._print_warning("Skipping package installation (--skip-install)")

        # Step 5: Health checks
        self._print_step(5, 5, "Running health checks")
        self.run_health_checks()

        # Summary
        self.print_summary()

    def check_prerequisites(self) -> bool:
        """Check Python version and required tools."""
        # Python version
        major, minor = sys.version_info[:2]
        if major < 3 or (major == 3 and minor < 9):
            self._print_error(
                f"Python 3.9+ required (you have {major}.{minor}). "
                "Please upgrade Python."
            )
            return False
        self._print_success(f"Python {major}.{minor} detected")

        # pip
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "--version"],
                capture_output=True, check=True,
            )
            self._print_success("pip is available")
        except (subprocess.CalledProcessError, FileNotFoundError):
            self._print_error(
                "pip not found. Install it: python -m ensurepip --upgrade"
            )
            return False

        # Pack directory
        if not self.pack_dir.exists():
            self._print_error(f"Pack directory not found: {self.pack_dir}")
            return False
        self._print_success(f"Pack directory found: {self.pack_dir}")

        return True

    def collect_api_keys(self):
        """Interactively collect API keys for each skill."""
        # Reuse Klaviyo key across analyst + developer
        klaviyo_key = None

        for skill_name, skill_config in SKILLS.items():
            # Skip if not in filter
            if self.skills_filter and skill_name not in self.skills_filter:
                continue

            skill_dir = self.pack_dir / skill_name
            if not skill_dir.exists():
                continue

            print(f"\n{Colors.BOLD}--- {skill_config['label']} ---{Colors.END}")

            if self.non_interactive:
                # In non-interactive mode, skip skills that need keys
                self.skipped_skills.append(skill_name)
                print("  Skipped (non-interactive mode)")
                continue

            if not self._confirm(f"  Set up {skill_config['label']}?"):
                self.skipped_skills.append(skill_name)
                continue

            # Collect each env var
            skill_keys = {}
            skip_skill = False

            for var_name, var_config in skill_config["env_vars"].items():
                # Reuse Klaviyo key
                if var_name == "KLAVIYO_API_KEY" and klaviyo_key:
                    if self._confirm(f"  Reuse Klaviyo key from earlier?"):
                        skill_keys[var_name] = klaviyo_key
                        continue

                print(f"\n  {Colors.BLUE}{var_config['instructions']}{Colors.END}")
                # Use masked input for secrets (API keys, tokens)
                is_secret = any(kw in var_name.upper() for kw in ["KEY", "TOKEN", "SECRET"])
                value = self._prompt(f"  {var_config['prompt']}", secret=is_secret)

                if not value:
                    self._print_warning(f"  Skipping {skill_config['label']} (no key provided)")
                    skip_skill = True
                    break

                if var_config["validation"] and not var_config["validation"](value):
                    self._print_warning(f"  {var_config['error']}")
                    if not self._confirm("  Use this value anyway?"):
                        skip_skill = True
                        break

                skill_keys[var_name] = value

                if var_name == "KLAVIYO_API_KEY":
                    klaviyo_key = value

            if skip_skill:
                self.skipped_skills.append(skill_name)
            else:
                self.collected_keys[skill_name] = skill_keys
                self.configured_skills.append(skill_name)
                self._print_success(f"  {skill_config['label']} configured")

    def create_env_files(self):
        """Write .env files from collected keys."""
        for skill_name, keys in self.collected_keys.items():
            env_path = self.pack_dir / skill_name / ".env"
            lines = [f"# Auto-generated by setup.py\n"]
            for var_name, value in keys.items():
                lines.append(f"{var_name}={value}\n")

            env_path.write_text("".join(lines))
            # Restrict .env file to owner-only read/write (0600)
            env_path.chmod(stat.S_IRUSR | stat.S_IWUSR)
            self._print_success(f"  Created {skill_name}/.env (permissions: 0600)")

    def install_dependencies(self):
        """Install Python packages for configured skills."""
        installed = set()
        for skill_name in self.configured_skills:
            req_file = self.pack_dir / skill_name / SKILLS[skill_name]["requirements"]
            if req_file.exists() and str(req_file) not in installed:
                print(f"  Installing packages for {SKILLS[skill_name]['label']}...")
                try:
                    subprocess.run(
                        [sys.executable, "-m", "pip", "install", "-r", str(req_file), "-q"],
                        check=True,
                        capture_output=True,
                    )
                    self._print_success(f"  Packages installed for {SKILLS[skill_name]['label']}")
                    installed.add(str(req_file))
                except subprocess.CalledProcessError as e:
                    self._print_error(
                        f"  Failed to install packages for {SKILLS[skill_name]['label']}: "
                        f"{e.stderr.decode() if e.stderr else str(e)}"
                    )
                    self.errors.append(f"pip install failed for {skill_name}")

    def run_health_checks(self):
        """Test API connectivity for each configured skill."""
        for skill_name in self.configured_skills:
            health_cmd = SKILLS[skill_name]["health_check"]
            if not health_cmd:
                print(f"  {SKILLS[skill_name]['label']}: No CLI health check (uses MCP server)")
                continue

            skill_dir = self.pack_dir / skill_name
            cmd_parts = health_cmd.split()
            full_cmd = [sys.executable] + [str(skill_dir / cmd_parts[0])] + cmd_parts[1:]

            print(f"  Testing {SKILLS[skill_name]['label']}...")
            try:
                result = subprocess.run(
                    full_cmd,
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=str(skill_dir),
                    env={**os.environ, **self.collected_keys.get(skill_name, {})},
                )
                if result.returncode == 0:
                    self._print_success(f"  {SKILLS[skill_name]['label']}: API connection OK")
                else:
                    self._print_warning(
                        f"  {SKILLS[skill_name]['label']}: {result.stderr.strip()[:100]}"
                    )
                    self.errors.append(f"Health check failed for {skill_name}")
            except subprocess.TimeoutExpired:
                self._print_warning(f"  {SKILLS[skill_name]['label']}: Timed out (API may be slow)")
            except Exception as e:
                self._print_error(f"  {SKILLS[skill_name]['label']}: {e}")
                self.errors.append(f"Health check error for {skill_name}")

    def print_summary(self):
        """Print setup summary and next steps."""
        print(f"\n{'='*50}")
        print(f"{Colors.BOLD}Setup Complete{Colors.END}")
        print(f"{'='*50}\n")

        if self.configured_skills:
            print(f"{Colors.GREEN}Configured:{Colors.END}")
            for skill in self.configured_skills:
                print(f"  + {SKILLS[skill]['label']}")

        if self.skipped_skills:
            print(f"\n{Colors.YELLOW}Skipped:{Colors.END}")
            for skill in self.skipped_skills:
                if skill in SKILLS:
                    print(f"  - {SKILLS[skill]['label']}")

        if self.errors:
            print(f"\n{Colors.RED}Issues:{Colors.END}")
            for error in self.errors:
                print(f"  ! {error}")

        print(f"\n{Colors.BOLD}Next Steps:{Colors.END}")
        print("  1. Copy skills to Claude Code:")
        print(f"     cp -r {self.pack_dir}/klaviyo-analyst ~/.claude/skills/")
        print(f"     cp -r {self.pack_dir}/shopify ~/.claude/skills/")
        print("     (repeat for each skill you want to use)")
        print()
        print("  2. Try your first audit:")
        if "shopify" in self.configured_skills:
            print(f"     python {self.pack_dir}/shopify/scripts/analyze.py --analysis-type full-audit")
        elif "google-analytics" in self.configured_skills:
            print(f"     python {self.pack_dir}/google-analytics/scripts/analyze.py --days 30 --compare")
        print()
        print("  3. Or just ask Claude:")
        print('     "Audit my Shopify store and tell me what needs fixing"')
        print('     "Review our email marketing performance in Klaviyo"')
        print()

    def _print_banner(self):
        """Print welcome banner."""
        print()
        print(f"{Colors.BOLD}{'='*50}")
        print("  Klaviyo Skill Pack Setup Wizard")
        print(f"{'='*50}{Colors.END}")
        print()
        print("This wizard will help you configure the skill pack.")
        print("You'll need API keys for the platforms you use.")
        print("Press Enter to skip any step you're not ready for.")
        print()

    def _print_step(self, n: int, total: int, message: str):
        """Print progress step."""
        print(f"\n{Colors.BOLD}[{n}/{total}] {message}{Colors.END}")

    def _print_success(self, message: str):
        print(f"  {Colors.GREEN}OK{Colors.END} {message}")

    def _print_warning(self, message: str):
        print(f"  {Colors.YELLOW}WARN{Colors.END} {message}")

    def _print_error(self, message: str):
        print(f"  {Colors.RED}ERROR{Colors.END} {message}")

    def _prompt(self, message: str, default: str = "", secret: bool = False) -> str:
        """Input with optional default. Uses masked input for secrets."""
        suffix = f" [{default}]" if default else ""
        try:
            if secret:
                value = getpass.getpass(f"{message}{suffix}: ").strip()
            else:
                value = input(f"{message}{suffix}: ").strip()
            return value or default
        except (EOFError, KeyboardInterrupt):
            print()
            return default

    def _confirm(self, message: str) -> bool:
        """Y/n confirmation."""
        if self.non_interactive:
            return False
        try:
            response = input(f"{message} (y/n) [y]: ").strip().lower()
            return response in ("", "y", "yes")
        except (EOFError, KeyboardInterrupt):
            print()
            return False


def main():
    parser = argparse.ArgumentParser(
        description="Klaviyo Skill Pack Setup Wizard",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive setup (recommended)
  python scripts/setup.py

  # Skip package installation
  python scripts/setup.py --skip-install

  # Set up only specific skills
  python scripts/setup.py --skills klaviyo-analyst,shopify

  # Non-interactive mode (for CI/testing)
  python scripts/setup.py --non-interactive
        """,
    )

    parser.add_argument(
        "--skip-install",
        action="store_true",
        help="Skip pip install of dependencies",
    )
    parser.add_argument(
        "--skills",
        help="Comma-separated list of skills to configure (default: all)",
    )
    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Run without prompts (for testing -- skips API key collection)",
    )

    args = parser.parse_args()

    # Determine pack directory (script is in scripts/ subdirectory)
    script_dir = Path(__file__).resolve().parent
    pack_dir = script_dir.parent

    # Parse skills filter
    skills_filter = None
    if args.skills:
        skills_filter = [s.strip() for s in args.skills.split(",")]
        invalid = [s for s in skills_filter if s not in SKILLS]
        if invalid:
            print(f"Unknown skills: {', '.join(invalid)}")
            print(f"Available: {', '.join(SKILLS.keys())}")
            sys.exit(1)

    wizard = SkillPackSetup(
        pack_dir=pack_dir,
        skills_filter=skills_filter,
        non_interactive=args.non_interactive,
    )
    wizard.run(skip_install=args.skip_install)


if __name__ == "__main__":
    main()
