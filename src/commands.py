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

from src.utils.common import print_title
from src.utils.connect.mysql import get_mysql_creds
from src.utils.connect.sqlite import get_sqlite_file
from alphadb import AlphaDBMySQL, AlphaDBSQLite, VersionSourceVerification
from alphadb.utils.exceptions import DBTemplateNoMatch, IncompleteVersionData, MissingVersionData, DBConfigIncomplete
from mysql.connector import DatabaseError, InterfaceError
from cryptography.fernet import Fernet
from src.utils.config import config_get, config_write 
from src.utils.common import console, clear
from src.utils.decorators import connection_check
from src.utils.version_source import select_version_source, vs_path_to_json
from inquirer import List, prompt, Confirm
from src.utils import globals

"Connect to a database"
def connect():

    print_title("connect")
    
    #### Prompt user for database engine
    questions = [List("engine", choices=["MySQL", "SQLite"])]
    answers = prompt(questions)
    
    #### If answers is None, user likely aborted
    if answers == None: return

    #### clear terminal and rerender title
    clear()
    print_title("connect")

    engine = answers["engine"]

    if engine == "MySQL":
        
        globals.db = AlphaDBMySQL()
        creds = get_mysql_creds()

        try:
            globals.db.connect(
                host=creds["host"],
                user=creds["user"],
                password=creds["password"],
                database=creds["database"],
                port=creds["port"],
            )

        #### Print mysql error if raised
        except (DatabaseError, InterfaceError) as e:
            if hasattr(e, "msg"): console.print(f"\n[red]{e.msg}[/red]\n")
            else: console.print(f"\n[red]{e}[/red]\n")
            return

        ### If connection was successful, add the credentials to config
        pass_bytes = creds["password"].encode()
        f = Fernet(config_get("CONFIG", "secret"))
        pass_encrypted = f.encrypt(pass_bytes)

        #### Save credentials to config
        config_write({
            "DB_SESSION": {
                "engine": "mysql",
                "host": creds["host"],
                "user": creds["user"],
                "password": pass_encrypted,
                "database": creds["database"],
                "port": creds["port"],
            }
        })

        console.print(f'\n[green]Successfully connected to database:[/green] [cyan]"{creds["database"]}"[/cyan]\n')

    elif engine == "SQLite":
        
        globals.db = AlphaDBSQLite()

        db_file = get_sqlite_file()

        #### If db_file is None, user likely aborted
        if db_file == None: return
        
        #### Make db connection
        globals.db.connect(db_file)

        #### Save connection to config
        config_write({
            "DB_SESSION": {
                "engine": "sqlite",
                "path": db_file,
            }
        })

        console.print(f'\n[green]Successfully connected to database at:[/green] [cyan]{db_file}[/cyan]\n')

    return

"Initialize database"
@connection_check()
def init():
    
    #### Initialize loader
    with console.status("[cyan]Getting the database ready[/cyan]", spinner="bouncingBall") as _:
        init = globals.db.init()

    if init == "already-initialized":
        console.print("[yellow]The database is already initialized[/yellow]\n")
        return

    if init == True:
        console.print("[green]Database successfully initialized[/green]\n")
        return

"Get database status"
@connection_check()
def status():

    print_title("database status")

    check = globals.db.status()

    print(f'Database: {check["name"]}')
    print(f'Template: {check["template"]}')
    if check["init"] == True:
        console.print("Status: ", "[cyan]Initialized[/cyan]")
    else:
        console.print("Status: ", "[yellow]Uninitialized[/yellow]")
    print(f'Version: {check["version"]}\n')

    return

"Update database"
@connection_check()
def update(nodata=False):

    print_title("update")

    #### Initialize loader
    with console.status("[cyan]Checking database[/cyan]", spinner="bouncingBall") as loader:

        #### Check database status
        status = globals.db.status()
        if status["init"] == False:
            console.print(f"[yellow]Database [cyan]{status['name']}[/cyan] has not yet been initialized[/yellow]\n")
            return

    try:

        version_source_path = select_version_source()
    
        #### If source path is None, user probably aborted
        if version_source_path == None: return
        
        with console.status("[cyan]Reading version source[/cyan]", spinner="bouncingBall") as loader:
           
            version_information = vs_path_to_json(version_source_path)

            #### If version information is None, an error has likely occured and we should not proceed
            if version_information == None: return

            loader.update("[cyan]Running updates on the database[/cyan]")

            update = globals.db.update(version_source=version_information, no_data=nodata)

            if update:
                if update == "up-to-date":
                    console.print(f"[blue]Database is already the latest version [cyan]({status['version']})[/cyan][/blue]\n")
                    return

                console.print("[green]Database successfully updated to the latest version[/green]\n")
            else:
                console.print("[red]An error occured[/red]\n")

    except (DBTemplateNoMatch, IncompleteVersionData, MissingVersionData, DBConfigIncomplete) as e:
        console.print(f"[red]{e}[/red]\n")

"Empty database"
@connection_check()
def vacate(confirm=False):
    print_title("vacate")
    
    #### Only works when confirm==True is specified
    if not confirm == True:
        console.print(f"[yellow]The vacate function requires the[/yellow] [red]--confirm[/red] [yellow]option.[/yellow]")
        print("This is a safety feature that hopefully prevents unintended data loss.\n\nDon't worry, you'll still be prompted for confirmation!\n")
        return

    console.print(f"[yellow]The vacate function[/yellow] [red]deletes all data in the database[/red].")
    console.print("[yellow]This action can [red]NOT[/red] be undone.[/yellow]\n")
    
    #### Prompt user for confirmation
    questions = [Confirm("confirm", message="Are you absolutely sure you want to completely delete all data?")]
    answers = prompt(questions)

    #### If answers is None, user likely aborted
    if answers == None: return

    if answers["confirm"]:
        with console.status("[cyan]Removing all data from database[/cyan]", spinner="bouncingBall") as _:

            #### Empty db
            if globals.db.vacate(confirm=confirm):
                console.print("[green]The database had successfully been emptied.[/green]\n")
    else:
        console.print("[cyan]Not empying[/cyan]\n")
    return

def verify_version_source():
    print_title("verify version source")
    
    version_source_path = select_version_source()

    #### If version source path is None, user likely aborted
    
    version_source = vs_path_to_json(version_source_path)

    #### If version source is None, an error likely occured and we should not proceed
    if version_source == None: return

    verification = VersionSourceVerification(version_source)

    print(verification.verify())

