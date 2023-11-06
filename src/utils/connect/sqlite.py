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

from inquirer import Text, prompt
from inquirer.errors import ValidationError
import os
from sqlite3 import connect

def validate_db_path(_, path):
    
    #### Check if path is absolute
    if not os.path.isabs(path):
        raise ValidationError("", reason="Supplies path is not absolute!")

    #### Check if path exists
    if not os.path.exists(path):
        raise ValidationError("", reason="Supplied path does not exist!")
    
    #### Check if path is file
    if not os.path.isfile(path):
        raise ValidationError("", reason="Supplied path is not a file!")
    
    #### Check if file is an SQLite db file
    try:
        conn = connect(path)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='table';")

        _ = cursor.fetchall()

    except:
        raise ValidationError("", reason="Unable to establish a connection to this database file!")
    
    return True
def get_sqlite_file() -> str | None:
    
    questions = [Text("path", message="Please supply an absolute file path to the SQLite db file", validate=validate_db_path)]
    answers = prompt(questions)
    
    #### If answers is None, user likely aborted
    if answers == None: return

    return answers["path"]

