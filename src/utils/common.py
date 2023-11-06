# Copyright (C) 2023 Wibo Kuipers
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
from src.utils.config import config_get
from rich.console import Console
console = Console()

"Prints out the programs title"
def print_title(title:str):
    console.print(f"[cyan]----- {title.upper()} -----[/cyan]\n")

"Clear the terminal"
def clear():

    #### Clear terminal
    if os.name == "posix":
        os.system("clear")
    else:
        os.system("cls")

    db_session_data = config_get("DB_SESSION", fallback=True)
    if not db_session_data == None:
        
        if db_session_data["engine"] == "mysql":
            console.print(f'[cyan]Connected to [blue]MySQL[/blue] database[/cyan] {db_session_data["database"]} [cyan]on[/cyan] {db_session_data["host"]}\n')

        if db_session_data["engine"] == "sqlite":
            console.print(f"[cyan]Connected to [blue]SQLite[/blue] database at [white]{db_session_data['path']}[/white][/cyan]\n")
