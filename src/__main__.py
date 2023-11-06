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

from src import __app_name__, cli
from src.utils.decorators import config_check
from src.utils.common import console, clear

#### Initialize some stuff
DEV = False

def raise_error(e):
    if DEV: raise e
    else: 
        if hasattr(e, "msg"):
            console.print(e.msg, style="white on red")
        else:
            console.print(f"[white]{e}[/white]", style="white on red")

@config_check
def main():
    clear()
    try:
        cli.app(prog_name=__app_name__)
    except Exception as e:
        raise_error(e)

if __name__ == "__main__":
    main()
