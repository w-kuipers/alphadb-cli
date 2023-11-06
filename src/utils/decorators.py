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

from configparser import ConfigParser
import os
from src.utils import globals
from src.utils.common import console
from typing import Callable
from alphadb import AlphaDBSQLite, AlphaDBMySQL
from simpleUID import urlsafe
from cryptography.fernet import Fernet
from src.utils.config import config_get, config_remove

#### Decorator function to init config when its not initialized yet
def config_check(func: Callable) -> Callable:
    def _(*args, **kwargs):
        config = ConfigParser()
        if os.path.isfile(globals.CONFIG_PATH):
            config.read(globals.CONFIG_PATH)

        if not "CONFIG" in config:
            config["CONFIG"] = {}
        if not "secret" in config["CONFIG"]:
            config["CONFIG"]["secret"] = urlsafe("padding")

        with open(globals.CONFIG_PATH, "w+") as configfile:
            config.write(configfile)

        return func(*args, **kwargs)

    return _


#### Check for database connecten, used for local db connection
def connection_check() -> Callable:
    def _(func: Callable) -> Callable:
        def _wrapper(*args, **kwargs):
            if globals.db.connection == None:

                #### Check if a connection is saved
                conn = config_get("DB_SESSION", fallback=True)
                main_config = config_get("CONFIG")
                secret = main_config["secret"] if "secret" in main_config else None
                    
                if conn and secret:

                    #### If engine is not saved, remove session
                    if not "engine" in conn:
                        console.print("[red]Unable to authorize using saved credentials. Please reconnect to the database.[/red]")
                        config_remove("DB_SESSION")
                        return

                    engine = conn["engine"]
                    
                    if engine == "mysql":
                        globals.db = AlphaDBMySQL()

                        try:
                            globals.db.connect(
                                host=conn["host"],
                                user=conn["user"],
                                password=Fernet(secret).decrypt(conn["password"][1:-1]).decode(),  ## Decrypt
                                database=conn["database"],
                                port=conn["port"],
                            )

                            globals.db.connection.autocommit = True
                        except:
                            console.print("[red]Unable to authorize using saved credentials. Please reconnect to the database.[/red]")
                            return

                    if engine == "sqlite":
                        globals.db = AlphaDBSQLite()

                        try:
                            globals.db.connect(conn["path"])
                        except:
                            console.print(f"[red]Unable to connect to database at [white]{conn['path']}[/white][/red]")

                    return func(*args, **kwargs)

                console.print("\n[yellow]No database connection found.[/yellow]\n")
        return _wrapper
    return _
