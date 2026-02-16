# ----- License -------------------------------------------------- # 

#  MacroKey - MacroKey is an open-source tool for ethical testing, VBA analysis, and controlled macro manipulation in authorized environments.
#  Copyright (c) 2025 - CursedSec (Operated by Cursed271). All rights reserved.

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
import shutil
import zipfile
import tempfile
from rich.console import Console

# ----- Global Declaration --------------------------------------- #

console = Console()
DPB_regex = re.compile(rb'DPB\="(.*?)"', flags=re.DOTALL)
DPB_value = b'282A84CBA1CBA1345FCCA12306A08F55352852B2A8681BCC935ECE2CC44972582045A51D'

# ----- Replace DPB Value ---------------------------------------- #

def modify_dpb(input_file):
	if not input_file:
		console.print(f"[bold red][!] No filename provided.")
		return
	if not os.path.isfile(input_file):
		console.print(f"[bold red][!] The provided file does not exist.")
		return
	output_file = input_file.rsplit(".", 1)[0] + "_new.xlsm"
	with zipfile.ZipFile(input_file, 'r') as zipinput:
		try:
			vba_file = zipinput.read("xl/vbaProject.bin")
		except KeyError:
			console.print(f"[bold red][!] The file - vbaProject.bin not found.")
			sys.exit()
		original_DPB = DPB_regex.search(vba_file).group(1)
		DPB_adjusted = DPB_value.ljust(len(original_DPB), b'0')[:len(original_DPB)]
		modified_vba = DPB_regex.sub(b'DPB="' + DPB_adjusted + b'"', vba_file, 1)
		with tempfile.TemporaryDirectory() as temp_dir:
			tempd = os.path.join(temp_dir, "out.zip")
			with zipfile.ZipFile(tempd, 'w', compression=zipfile.ZIP_DEFLATED) as zipoutput:
				for zi in zipinput.infolist():
					zipoutput.writestr(
                        zi.filename,
                        modified_vba if zi.filename == 'xl/vbaProject.bin' else zipinput.read(zi.filename)
                    )
			shutil.move(tempd, output_file)
	return output_file

# ----- Banner --------------------------------------------------- #

def ascii():
	console.print(rf"""[#C6ECE3]
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                                  │
│    ooo        ooooo                                        oooo    oooo                          │ 
│    `88.       .888'                                        `888   .8P'                           │ 
│     888b     d'888   .oooo.    .ooooo.  oooo d8b  .ooooo.   888  d8'     .ooooo.  oooo    ooo    │ 
│     8 Y88. .P  888  `P  )88b  d88' `"Y8 `888""8P d88' `88b  88888[      d88' `88b  `88.  .8'     │
│     8  `888'   888   .oP"888  888        888     888   888  888`88b.    888ooo888   `88..8'      │
│     8    Y     888  d8(  888  888   .o8  888     888   888  888  `88b.  888    .o    `888'       │
│    o8o        o888o `Y888""8o `Y8bod8P' d888b    `Y8bod8P' o888o  o888o `Y8bod8P'     .8'        │
│                                                                                   .o..P'         │
│                                                                                   `Y8P'          │
│                                                                                                  │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
	""")
	console.print(rf"[#C6ECE3]+--------------------------------------------------------------+")
	console.print(rf"[#C6ECE3]  MacroKey - Crack the Code. Own the Macro.")
	console.print(rf"[#C6ECE3]  Created by [bold black]Cursed271")
	console.print(rf"[#C6ECE3]+--------------------------------------------------------------+")

# ----- Main Function -------------------------------------------- #

if __name__ == "__main__":
	os.system("cls" if os.name == "nt" else "clear")
	ascii()
	input_file = console.input(f"[#C6ECE3][?] Enter the name of the .XLSM File: ")
	output_file = modify_dpb(input_file)
	console.print(rf"[#C6ECE3][+] MacroKey has successfully modified the DPB value.")
	console.print(rf"[#C6ECE3][+] Use the password - 'MacroKey@3690' to access the VBA Scripts in {output_file}.")
	console.print("[#C6ECE3]+--------------------------------------------------------------+")

# ----- End ------------------------------------------------------ #
