# ----- License -------------------------------------------------- # 

#  MacroKey - MacroKey modifies VBA project protection records inside 
#  supported Office archives, producing rewritten documents for 
#  authorized macro inspection and security research.
#  Copyright (c) 2026 - CursedSec (Operated by Cursed271). All rights reserved.

#  This software is an proprietary intellectual property developed for
#  penetration testing, threat modeling, and security research. It   
#  is licensed under the CURSEDSEC OWNERSHIP EDICT:
#
#  🚫 PROHIBITION WARNING 🚫
#  Redistribution, re-uploading, and unauthorized modification are strictly forbidden 
#  under the COE. Use is granted ONLY under the limited terms defined in the official 
#  LICENSE file (COE), which must be included in all copies.

#  DISCLAIMER:
#  This tool is intended for **educational or ethical testing** purposes only.
#  Unauthorized or malicious use of this software against systems without 
#  proper authorization is strictly prohibited and may violate laws and regulations.
#  The author assumes no liability for misuse or damage caused by this tool.

#  🔗 LICENSE: CURSEDSEC OWNERSHIP EDICT (COE)
#  🔗 Repository: https://github.com/Cursed271
#  🔗 Author: Steven Pereira (@Cursed271)

# ----- Libraries ------------------------------------------------ #

import os
import re
import sys
import typer
import shutil
import zipfile
import tempfile
from pathlib import Path
from rich.rule import Rule
from rich.text import Text
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from rich.console import Console
from typing import Optional, Tuple
import typer.rich_utils as typer_rich

# ----- Global Declaration --------------------------------------- #

console = Console()
app = typer.Typer(rich_markup_mode="rich")
DPB_REGEX = re.compile(rb'DPB\=\"(.*?)\"', flags=re.DOTALL)
DPB_VALUE = b'282A84CBA1CBA1345FCCA12306A08F55352852B2A8681BCC935ECE2CC44972582045A51D'
MASTER_KEY = "MacroKey@3690"

VBA_PROJECT_PATHS = [
    "xl/vbaProject.bin",     # Excel (.xlsm, .xlsb)
    "word/vbaProject.bin",   # Word (.docm)
    "ppt/vbaProject.bin",    # PowerPoint (.pptm)
]

# ----- DPB Modification ----------------------------------------- #

def modify_dpb(vba_data: bytes) -> Tuple[bytes, bool]:
    match = DPB_REGEX.search(vba_data)
    if not match:
        return vba_data, False
    original_dpb = match.group(1)
    dpb_adjusted = DPB_VALUE.ljust(len(original_dpb), b'0')[:len(original_dpb)]
    modified_vba = DPB_REGEX.sub(b'DPB="' + dpb_adjusted + b'"', vba_data, count=1)
    return modified_vba, True

# ----- Document Processor --------------------------------------- #

def process_document(input_path: Path, output_path: Path) -> Tuple[bool, str]:
    if not input_path.exists():
        return False, "The provided input file does not exist on disk."
    if not zipfile.is_zipfile(input_path):
        return False, "The file is not a valid OpenXML macro archive (.xlsm, .docm, .pptm)."
    with zipfile.ZipFile(input_path, 'r') as zin:
        vba_file_entry = None
        for candidate in VBA_PROJECT_PATHS:
            if candidate in zin.namelist():
                vba_file_entry = candidate
                break
        if not vba_file_entry:
            for item in zin.namelist():
                if "vbaProject.bin" in item:
                    vba_file_entry = item
                    break
        if not vba_file_entry:
            return False, "Target file does not contain an embedded vbaProject.bin."
        raw_vba = zin.read(vba_file_entry)
        modified_vba, success = modify_dpb(raw_vba)
        if not success:
            return False, "No active DPB protection signature was detected in the project."
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_zip = Path(temp_dir) / "rebuilt.zip"
            with zipfile.ZipFile(temp_zip, 'w', compression=zipfile.ZIP_DEFLATED) as zout:
                for item in zin.infolist():
                    if item.filename == vba_file_entry:
                        zout.writestr(item.filename, modified_vba)
                    else:
                        zout.writestr(item.filename, zin.read(item.filename))
            output_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(temp_zip, output_path)
    return True, f"Successfully modified DPB hash in {vba_file_entry}"

# ----- Summary Table ------------------------------------------- #

def render_summary_table(input_path: Path, output_path: Path, detail_msg: str, success: bool) -> None:
    tbl = Table(
        title="[bold white]MacroKey - VBA Protection Bypass Summary[/bold white]",
        border_style="#C6ECE3",
        header_style="#C6ECE3",
        expand=False
    )
    tbl.add_column("Security Dimension", style="bold white", justify="left")
    tbl.add_column("Audit Findings", style="cyan", justify="left")
    tbl.add_column("Security Posture", style="yellow", justify="left")
    file_size_kb = f"{input_path.stat().st_size / 1024:.2f} KB" if input_path.exists() else "0 KB"
    tbl.add_row("Target Document", input_path.name, f"File Size: {file_size_kb}")
    tbl.add_row("Document Format", input_path.suffix.upper(), "OpenXML Macro Container")
    tbl.add_row("Cryptographic Target", "MS-OVBA DPB Hash Record", "Project Password Descriptor")
    status_str = "[bold green]PASSWORD RESET APPLIED[/bold green]" if success else "[bold red]FAILED[/bold red]"
    tbl.add_row("Operation Result", detail_msg, status_str)
    if success:
        tbl.add_row("Master Unlock Key", f"[bold white on #1F2937] {MASTER_KEY} [/bold white on #1F2937]", "[bold green]Known Access Key[/bold green]")
    console.print()
    console.print(tbl)
    console.print()

# ----- Orchestration -------------------------------------------- #

def orchestrate(input_file: str, output_file: Optional[str] = None) -> None:
    in_path = Path(input_file).resolve()
    if not output_file:
        out_path = in_path.with_name(f"{in_path.stem}_new{in_path.suffix}")
    else:
        out_path = Path(output_file).resolve()
    title_name = in_path.stem.title()
    console.print(f"[#C6ECE3][+] MacroKey initiated against [bold white]{title_name}[/bold white]\n")
    with console.status("[#C6ECE3][!] Unpacking archive & replacing DPB hash with Master Key...", spinner="dots"):
        success, msg = process_document(in_path, out_path)
    render_summary_table(in_path, out_path, msg, success)
    if success:
        console.print(f"  [green][+] Successfully modified DPB value. File saved to [#C6ECE3]{out_path}[/#C6ECE3]\n")
        console.print(Panel(
            f"[bold white]Next Steps to Access the VBA Source Code:[/bold white]\n"
            f"1. Open the file [bold cyan]{out_path.name}[/bold cyan] in Microsoft Excel / Office.\n"
            f"2. Press [bold cyan]ALT + F11[/bold cyan] (or [bold cyan]Option + F11[/bold cyan] on Mac) to open the VBA Editor.\n"
            f"3. Double-click the locked project name in the left panel.\n"
            f"4. When prompted for the password, enter: [bold yellow]{MASTER_KEY}[/bold yellow]\n"
            f"5. The project unlocks cleanly with zero error prompts.",
            title="[bold #C6ECE3]MacroKey Access Instructions[/bold #C6ECE3]",
            border_style="#C6ECE3",
            width=banner_width
        ))
    else:
        console.print(f"[bold red][!] Operation aborted: {msg}[/bold red]\n")

# ----- ASCII Banner --------------------------------------------- #

def ascii() -> int:
    art_content = rf"""
ooo        ooooo                                        oooo    oooo
`88.       .888'                                        `888   .8P'
 888b     d'888   .oooo.    .ooooo.  oooo d8b  .ooooo.   888  d8'     .ooooo.  oooo    ooo
 8 Y88. .P  888  `P  )88b  d88' `"Y8 `888""8P d88' `88b  88888[      d88' `88b  `88.  .8'
 8  `888'   888   .oP"888  888        888     888   888  888`88b.    888ooo888   `88..8'
 8    Y     888  d8(  888  888   .o8  888     888   888  888  `88b.  888    .o    `888'
o8o        o888o `Y888""8o `Y8bod8P' d888b    `Y8bod8P' o888o  o888o `Y8bod8P'     .8'
                                                                               .o..P'
                                                                               `Y8P'
"""
    art_color = Text(art_content, style = "#C6ECE3")
    art_panel = Panel(art_color, border_style = "#C6ECE3", expand = False)
    console.print(art_panel)
    banner_width = console.measure(art_panel).maximum
    console.print(Rule(style = "#C6ECE3 blink"), width = banner_width)
    console.print(f"  [~] Created by [bold red blink]Cursed271[/bold red blink]")
    console.print(f"  [~] DeadKey - Inspect the macro behind the lock.")
    console.print(Rule(style = "#C6ECE3 blink"), width = banner_width)
    console.print()
    return banner_width

# ----- Argument Parser ------------------------------------------ #

@app.command()
def argu(
    file: Optional[str] = typer.Option(None, "--file", "-f", help="Target macro file (.xlsm, .docm, .pptm)"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Custom output path for unlocked file"),
) -> None:
    if not file:
        file = Prompt.ask("[bold #C6ECE3][?][/bold #C6ECE3] Enter the name of the .XLSM / Macro File")
    clean_file = file.strip().strip('"').strip("'")
    clean_output = output.strip().strip('"').strip("'") if output else None
    orchestrate(input_file=clean_file, output_file=clean_output)

# ----- Main Function -------------------------------------------- #

if __name__ == "__main__":
    os.system("cls" if os.name == "nt" else "clear")
    banner_width = ascii()
    typer_rich.MAX_WIDTH = banner_width
    app()

# ----- End ------------------------------------------------------ #