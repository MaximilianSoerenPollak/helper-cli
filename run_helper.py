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
        "bazel run //process-docs:ide_support",
        "bazel run //process-docs:incremental",
        "bazel build //process-docs:incremental && bazel-bin/process-docs/incremental",
        "bazel build //process-docs:docs",

        # Currently can not test 'live_preview'
        # "bazel run //process-docs:live_preview",
        # "bazel build //process-docs:live_preview && bazel-bin/process-docs/live_preview",
]

def run_command(cmdinput: str):
    len_left = len_max - len(cmdinput)
    print(f"[cyan]{'='*len_max}[/cyan]")
    print(f"[cornflower_blue]{'='*int(len_left/2)}{cmdinput}{'='*int(len_left/2)}[/cornflower_blue]")
    print(f"[cyan]{'='*len_max}[/cyan]")
    if "&&" in cmdinput:
        split_commands = cmdinput.split("&&")
        cmd = split_commands[0].strip().split()
        # Build the executeable
        proc_build = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )
        # Run the executeable
        proc_run = subprocess.run(
            split_commands[-1].strip(),
            capture_output=True,
            text=True
        )
        output = proc_build.stderr + proc_run.stderr + proc_build.stdout  + proc_run.stdout
        return_code = proc_build.returncode if proc_build.returncode != 0 else proc_run.returncode
    else:
        cmd = cmdinput.split()
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )
        output = proc.stderr + proc.stdout
        return_code = proc.returncode
    infos, warnings, errors = parse_output(output)
    return return_code,infos, warnings, errors 



def parse_output(output: str):
    infos = []
    warnings = []
    errors = []
    debug = []
    # print("THIS IS THE RAW OUTPUT")
    # print("\n\n\n")
    # print(output)
    outputlines = output.split("\n")
    for line in outputlines: 
        if "info:" in line.lower():
            infos.append(line)
        if "warning:" in line.lower():
            warnings.append(line)
        if "error:" in line.lower():
            errors.append(line)
        if "debug:" in line.lower():
            debug.append(line)

    print_info = "\n".join(infos)
    print_warnings = "\n".join(warnings)
    print_errors = "\n".join(errors)
    print_debug = "\n".join(debug)
    if debug:
        len_left = len_max - len("DEBUG") 
        print(f"[white]{'='*int(len_left/2)}[/white][aquamarine3]DEBUG[/aquamarine3][white]{'='*int(len_left/2)}[/white]")
        print(f"[aquamarine3]{print_debug}[/aquamarine3]\n")
    if infos:
        len_left = len_max - len("INFOS") 
        print(f"[white]{'='*int(len_left/2)}[/white][blue]INFOS[/blue][white]{'='*int(len_left/2)}[/white]")
        print(f"[blue]{print_info}[/blue]\n")
    if warnings:
        len_left = len_max - len("WARNINGS") 
        print(f"[white]{'='*int(len_left/2)}[dark_orange]WARNINGS[/dark_orange][white]{'='*int(len_left/2)}[/white]")
        print(f"[dark_orange]{print_warnings}[/dark_orange]\n")
    if errors:
        len_left = len_max - len("ERRORS") 
        print(f"[white]{'='*int(len_left/2)}[/white][red1]ERRORS[/red1][white]{'='*int(len_left/2)}[/white]")
        print(f"[red1]{print_errors}[/red1]\n")

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

def clear_cache_and_build_folder():
    subprocess.run(
        ["bazel", "clean", "&&", "rm", "-r", "_build"],
        capture_output=True,
        text=True
    )


def get_commands(cmds: list[str] = all_commands, clear_cache: bool = False):
    # cmds = ["bazel run //docs:incremental"]
    results = []
    if clear_cache:
        len_left = len_max - len("CLEARING CACHE FOR EACH BUILD")
        print(f"[magenta]{'='*int(len_left/2)}CLEARING CACHE FOR EACH BUILD{'='*int(len_left/2)}[/magenta]")
        print("\n\n")
    for cmd in cmds:
        if clear_cache:
            clear_cache_and_build_folder()
            
        exit_code, infos, warnings, errors = run_command(cmd)
        results.append(result(
                       cmd=cmd,
                       exit_code=exit_code,
                       infos=infos,
                       warnings=warnings,
                       errors=errors
        ))
        # print(f"[yellow1]{'x'*len_max}[/yellow1]\n\n")
    create_results_table(results)


if __name__ ==  "__main__":
    typer.run(get_commands)


