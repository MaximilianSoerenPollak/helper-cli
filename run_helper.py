import typer
import subprocess
from rich import print
from rich.table import Table
from rich.console import Console
from dataclasses import dataclass

@dataclass
class result():
    cmd: str
    exit_code: int
    infos: list[str]
    warnings: list[str]
    errors: list[str]



"""
Want to be able to run specific or all commands
Parse outputs of the command and make it nicely viewable
    - Parse warnings, info, errors, debug
    - Color them and count them each
Give a nice overview table at the end of which command worked and what didn't 
"""

len_max = 80

all_commands = [
        "bazel run //docs:incremental",
        "bazel build //docs:docs",
        "bazel run //docs:ide_support"
]

def run_command(cmdinput: str):
    cmd = cmdinput.split()
    len_left = len_max - len(cmdinput)
    print(f"[cyan]{'='*len_max}[/cyan]")
    print(f"[cornflower_blue]{'='*int(len_left/2)}{cmdinput}{'='*int(len_left/2)}[/cornflower_blue]")
    print(f"[cyan]{'='*len_max}[/cyan]")
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )
    output = proc.stderr + proc.stdout
    infos, warnings, errors = parse_output(output)
    return proc.returncode,infos, warnings, errors 
    # print(output)



def parse_output(output: str):
    infos = []
    warnings = []
    errors = []
    outputlines = output.split("\n")
    for line in outputlines: 
        if "info:" in line.lower():
            infos.append(line)
        if "warning:" in line.lower():
            warnings.append(line)
        if "error:" in line.lower():
            errors.append(line)

    print_info = "\n".join(infos)
    print_warnings = "\n".join(warnings)
    print_errors = "\n".join(errors)
    if infos:
        print("=========INFOS===============")
        print(f"[blue]{print_info}[/blue]\n")
    if warnings:
        print("===========WARNINGS===============")
        print(f"[red]{print_warnings}[/red]\n")
    if errors:
        print("===========ERRORS===============")
        print(f"[red]{print_errors}[/red]\n")
    print("\n")
    return infos, warnings, errors  
        # elif "debug" in line.lower(
  



def create_results_table(results: list[result]) -> None:
    """
    Create a rich table to display results with color-coded status
    """
    console = Console()
    
    table = Table(title="Command Execution Results")
    
    # Define columns
    table.add_column("Command", style="cyan")
    table.add_column("Exit Code", style="magenta")
    table.add_column("Warnings", style="yellow")
    table.add_column("Errors", style="red")
    table.add_column("Pass", style="green")
    
    # Populate table
    for result in results:
        # Determine pass status
        pass_status = "✅" if len(result.warnings) == 0 and len(result.errors) == 0 else "❌"
        
        # Add row
        table.add_row(
            result.cmd, 
            str(result.exit_code), 
            str(len(result.warnings)), 
            str(len(result.errors)), 
            pass_status
        )
    
    # Print the table
    console.print(table)



def get_commands(cmds: list[str] = all_commands):
    # cmds = ["bazel run //docs:incremental"]
    results = []
    for cmd in cmds:
        exit_code, infos, warnings, errors = run_command(cmd)
        results.append(result(
                       cmd=cmd,
                       exit_code=exit_code,
                       infos=infos,
                       warnings=warnings,
                       errors=errors
        ))
    create_results_table(results)


if __name__ ==  "__main__":
    typer.run(get_commands)


