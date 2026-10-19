"""
fastbi - Scaffold Power BI projects instantly from templates.

A universal CLI tool to initialize Power BI projects from any .pbip template.
It handles intelligent renaming of files, folders, and updates JSON content to maintain path integrity.
"""

import sys
import os
import subprocess
import typer
import shutil
import json
import re
from pathlib import Path
from datetime import datetime
from rich.console import Console
from typing import List, Any, Optional

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# --- Setup ---
app = typer.Typer(
    add_completion=False,
    help="fastbi - Scaffold Power BI projects instantly from templates.",
)
console = Console()
CONFIG_DIR = Path.home() / ".fastbi"
CONFIG_FILE = CONFIG_DIR / "config.json"

IGNORE_PATTERNS = shutil.ignore_patterns(
    ".git", ".gitignore", ".vs", ".vscode", "*.tmp", "*cache*", "*.log"
)


# --- Helper Functions ---
def load_config() -> dict | None:
    try:
        with open(CONFIG_FILE, "r", encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def save_config(config: dict):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding='utf-8') as f:
        json.dump(config, f, indent=4)
    console.print(f"[green]✓ Configuration saved to {CONFIG_FILE}[/green]")


def is_valid_foldername(name: str) -> bool:
    if not name or Path(name).is_absolute():
        return False
    return not bool(re.search(r'[<>:"/\\|?*]', name))


def open_project_file(file_path: Path):
    try:
        console.print(f"[cyan]Launching {file_path.name} in Power BI Desktop...[/cyan]")
        if sys.platform == "win32":
            os.startfile(str(file_path))
        elif sys.platform == "darwin":
            subprocess.run(["open", str(file_path)])
        else:
            subprocess.run(["xdg-open", str(file_path)])
    except Exception as e:
        console.print(f"[yellow]Note: Could not open project automatically: {e}[/yellow]")


def run_setup_wizard() -> dict:
    console.print("[bold yellow]🚀 Welcome! Let's configure your .pbip project template.[/bold yellow]")
    while True:
        template_path_str = console.input("[bold]Drag your template folder here and press Enter: [/bold]")
        cleaned_path_str = template_path_str.strip().strip('"')
        template_path = Path(cleaned_path_str).resolve()
        if template_path.is_dir():
            try:
                discover_template_base_name(template_path)
                config = {"template_path": str(template_path)}
                save_config(config)
                return config
            except ValueError as e:
                console.print(f"[bold red]Error: {e}[/bold red]")
        else:
            console.print(f"[bold red]Error: Path is not a valid directory. Try again.[/bold red]")


def update_json_file(file_path: Path, key_path: List[Any], new_value: Any):
    if not file_path.exists():
        console.print(f"[yellow]  - Warning: Could not update '{file_path.name}', file not found.[/yellow]")
        return
    try:
        with open(file_path, "r+", encoding='utf-8') as f:
            data = json.load(f)
            temp_data = data
            for key in key_path[:-1]:
                temp_data = temp_data[key]
            temp_data[key_path[-1]] = new_value
            f.seek(0)
            json.dump(data, f, indent=2)
            f.truncate()
        console.print(f"[green]  ✓ Updated '{file_path.name}'[/green]")
    except (KeyError, IndexError):
        console.print(f"[red]  - Error: Key path {key_path} not found in '{file_path.name}'.[/red]")
    except Exception as e:
        console.print(f"[red]  - Error: Failed to update '{file_path.name}'. Details: {e}[/red]")


def discover_template_base_name(template_path: Path) -> str:
    pbip_files = list(template_path.glob("*.pbip"))
    if not pbip_files:
        raise ValueError("Invalid template: No *.pbip file found in directory.")
    if len(pbip_files) > 1:
        raise ValueError("Invalid template: Multiple *.pbip files found, which is ambiguous.")
    base_name = pbip_files[0].stem
    console.print(f"Discovered template base name: [bold cyan]'{base_name}'[/bold cyan]")
    return base_name


def post_process_project(destination_dir: Path, project_name: str, template_base_name: str) -> Path:
    console.print("[cyan]Starting Power BI structure post-processing...[/cyan]")
    old_pbip_path = destination_dir / f"{template_base_name}.pbip"
    old_report_dir = destination_dir / f"{template_base_name}.Report"

    # Support both modern .SemanticModel and legacy .Dataset
    old_model_sm = destination_dir / f"{template_base_name}.SemanticModel"
    old_model_ds = destination_dir / f"{template_base_name}.Dataset"
    if old_model_sm.exists():
        old_model_dir = old_model_sm
    elif old_model_ds.exists():
        old_model_dir = old_model_ds
    else:
        old_model_dir = old_model_sm

    new_pbip_path = destination_dir / f"{project_name}.pbip"
    new_report_dir = destination_dir / f"{project_name}.Report"
    new_model_dir = destination_dir / f"{project_name}.SemanticModel"
    pbir_file_path = new_report_dir / "definition.pbir"
    report_platform_file = new_report_dir / ".platform"
    model_platform_file = new_model_dir / ".platform"

    console.print("Renaming files and folders...")
    if old_pbip_path.exists():
        old_pbip_path.rename(new_pbip_path)
    if old_report_dir.exists():
        old_report_dir.rename(new_report_dir)
    if old_model_dir.exists():
        old_model_dir.rename(new_model_dir)

    console.print("Updating internal project references...")
    if new_pbip_path.exists():
        update_json_file(new_pbip_path, ['artifacts', 0, 'report', 'path'], new_report_dir.name)
    if pbir_file_path.exists():
        update_json_file(pbir_file_path, ['datasetReference', 'byPath', 'path'], f"../{new_model_dir.name}")
    if report_platform_file.exists():
        update_json_file(report_platform_file, ['metadata', 'displayName'], project_name)
    if model_platform_file.exists():
        update_json_file(model_platform_file, ['metadata', 'displayName'], project_name)

    return new_pbip_path


# --- The Engine ---
def run_project_creation_logic(
    project_name: str,
    output_dir: Optional[Path] = None,
    no_date: bool = False,
    open_project: bool = False,
):
    """The core engine for creating a project. Called by CLI commands."""
    if not project_name:
        console.print("[bold red]Error:[/bold red] Project name is required.")
        console.print("Usage: [cyan]fastbi create \"My Report\"[/cyan]")
        console.print("Or shortcut: [cyan]fastbi \"My Report\"[/cyan]")
        raise typer.Exit(code=1)

    config = load_config()
    if not config:
        config = run_setup_wizard()

    template_path = Path(config.get("template_path", ""))
    if not template_path.exists() or not template_path.is_dir():
        console.print(f"[bold red]Error: Configured template directory does not exist:[/bold red] {template_path}")
        answer = console.input("[yellow]Would you like to reconfigure your template path now? (y/n): [/yellow]")
        if answer.strip().lower().startswith("y"):
            config = run_setup_wizard()
            template_path = Path(config["template_path"])
        else:
            raise typer.Exit(code=1)

    try:
        template_base_name = discover_template_base_name(template_path)
    except ValueError as e:
        console.print(f"[bold red]Template Error: {e}[/bold red]")
        raise typer.Exit(code=1)

    if not is_valid_foldername(project_name):
        console.print(f"[bold red]Error: Invalid project name '{project_name}'. Avoid characters like /\\:*?\"<>|[/bold red]")
        raise typer.Exit(code=1)

    if no_date:
        new_project_folder_name = project_name
    else:
        current_date = datetime.now().strftime("%Y%m")
        new_project_folder_name = f"{current_date} - {project_name}"

    base_dir = output_dir.resolve() if output_dir else Path.cwd()
    destination_dir = base_dir / new_project_folder_name

    if destination_dir.exists():
        console.print(f"[bold red]Error: Directory '{destination_dir.name}' already exists in '{base_dir}'.[/bold red]")
        raise typer.Exit(code=1)

    created_pbip_file = None

    try:
        with console.status("[bold cyan]Copying template files...[/bold cyan]", spinner="dots") as status:
            shutil.copytree(template_path, destination_dir, ignore=IGNORE_PATTERNS)
            status.update("[bold cyan]Post-processing PBI project...[/bold cyan]")
            created_pbip_file = post_process_project(destination_dir, project_name, template_base_name)

        console.print(f"[bold green]✓ Success! Project created and configured at:[/bold green] \n[underline]{destination_dir}[/underline]")
        console.print("\n[bold]Next steps:[/bold]")
        console.print(f'  [cyan]1. cd "{destination_dir}"[/cyan]')
        console.print("  [cyan]2. Open the .pbip file to start working.[/cyan]")

        if open_project and created_pbip_file and created_pbip_file.exists():
            open_project_file(created_pbip_file)

    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred: {e}[/bold red]")
        if destination_dir.exists():
            console.print("[yellow]Rolling back: Cleaning up partially created directory...[/yellow]")
            shutil.rmtree(destination_dir, ignore_errors=True)
            console.print("[yellow]Rollback complete.[/yellow]")
        raise typer.Exit(code=1)


# --- Typer CLI Commands ---

@app.command(name="setup", help="Run the wizard to (re)configure your template path.")
def setup_command():
    """Configure or reconfigure the template path."""
    run_setup_wizard()


@app.command(name="info", help="Display current configuration and template details.")
def info_command():
    """Show configuration and template status."""
    config = load_config()
    console.print(f"[bold]Configuration file:[/bold] {CONFIG_FILE}")
    if not config or "template_path" not in config:
        console.print("[yellow]No template configured yet. Run [cyan]fastbi setup[/cyan] to get started.[/yellow]")
        return
    tpath = Path(config["template_path"])
    exists = tpath.is_dir()
    status_str = "[green]Valid directory[/green]" if exists else "[bold red]Not found (missing path!)[/bold red]"
    console.print(f"[bold]Template path:[/bold] {tpath} ({status_str})")
    if exists:
        try:
            base_name = discover_template_base_name(tpath)
            console.print(f"[bold]Template base name:[/bold] [cyan]{base_name}[/cyan]")
        except Exception as e:
            console.print(f"[bold red]Template check:[/bold red] {e}")


@app.command(name="create", help="Create a new Power BI project from your template.")
def create_command(
    project_name: str = typer.Argument(..., help="The name for the new project."),
    output_dir: Optional[Path] = typer.Option(None, "--output", "-o", help="Custom destination directory (defaults to current directory)."),
    no_date: bool = typer.Option(False, "--no-date", help="Do not prefix the folder name with the current YYYYMM date."),
    open_project: bool = typer.Option(False, "--open", "-O", help="Open the .pbip project in Power BI Desktop immediately after creation."),
):
    """Create a new project (main command)."""
    run_project_creation_logic(
        project_name=project_name,
        output_dir=output_dir,
        no_date=no_date,
        open_project=open_project,
    )


@app.command(name="new", help="Create a new Power BI project (alias for 'create').")
def new_command(
    project_name: str = typer.Argument(..., help="The name for the new project."),
    output_dir: Optional[Path] = typer.Option(None, "--output", "-o", help="Custom destination directory (defaults to current directory)."),
    no_date: bool = typer.Option(False, "--no-date", help="Do not prefix the folder name with the current YYYYMM date."),
    open_project: bool = typer.Option(False, "--open", "-O", help="Open the .pbip project in Power BI Desktop immediately after creation."),
):
    """Create a new project (alias for create)."""
    run_project_creation_logic(
        project_name=project_name,
        output_dir=output_dir,
        no_date=no_date,
        open_project=open_project,
    )


# --- Default behavior (shortcut) ---
@app.callback(invoke_without_command=True)
def main_callback(ctx: typer.Context):
    """
    fastbi - Scaffold Power BI projects instantly.
    """
    if ctx.invoked_subcommand is None:
        console.print("[bold]fastbi[/bold] - Scaffold Power BI projects instantly")
        console.print("\nUsage:")
        console.print("  [cyan]fastbi \"My Project\"[/cyan]                - Create a project (shortcut)")
        console.print("  [cyan]fastbi create \"My Project\"[/cyan]         - Create a project (explicit)")
        console.print("  [cyan]fastbi \"My Project\" --open[/cyan]         - Create and launch in Power BI Desktop")
        console.print("  [cyan]fastbi \"My Project\" --no-date[/cyan]      - Create without date prefix")
        console.print("  [cyan]fastbi \"My Project\" -o D:\\Reports[/cyan]  - Create in specific folder")
        console.print("  [cyan]fastbi setup[/cyan]                        - Configure template path")
        console.print("  [cyan]fastbi info[/cyan]                         - View current configuration")
        console.print("\nFor full help: [cyan]fastbi --help[/cyan]")
        raise typer.Exit()


def main():
    known_commands = {"setup", "create", "new", "info"}
    # If the user passed arguments and the first argument is not a flag and not a known command,
    # assume it is a project name shortcut for 'create':
    if len(sys.argv) > 1 and not sys.argv[1].startswith("-") and sys.argv[1] not in known_commands:
        sys.argv.insert(1, "create")
    app()


if __name__ == "__main__":
    main()