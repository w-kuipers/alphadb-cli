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
from src.utils.constants import CONFIG_PATH
from src.utils.common import console
from typing import Callable
from simpleUID import urlsafe
from cryptography.fernet import Fernet
from src.utils.config import config_get

#### Decorator function to init config when its not initialized yet
def config_check(func: Callable) -> Callable:
    def _(*args, **kwargs):
        config = ConfigParser()
        if os.path.isfile(CONFIG_PATH):
            config.read(CONFIG_PATH)

        if not "CONFIG" in config:
            config["CONFIG"] = {}
        if not "secret" in config["CONFIG"]:
            config["CONFIG"]["secret"] = urlsafe("padding")

        with open(CONFIG_PATH, "w+") as configfile:
            config.write(configfile)

        return func(*args, **kwargs)

    return _


#### Check for database connecten, used for local db connection
def connection_check(db) -> Callable:
    def _(func: Callable) -> Callable:
        def _wrapper(*args, **kwargs):
            if db.connection == None:

                #### Check if a connection is saved
                conn = config_get("DB_SESSION", fallback=True)
                main_config = config_get("CONFIG")
                secret = main_config["secret"] if "secret" in main_config else None

                if conn and secret:
                    try:
                        db.connect(
                            host=conn["host"],
                            user=conn["user"],
                            password=Fernet(secret).decrypt(conn["password"][1:-1]).decode(),  ## Decrypt
                            database=conn["database"],
                            port=conn["port"],
                        )
                        db.connection.autocommit = True
                    except:
                        console.print("[red]Unable to authorize using saved credentials. Please reconnect to the database.[/red]")
                        return

                    return func(*args, **kwargs)

                console.print("\n[yellow]No database connection found.[/yellow]\n")

        return _wrapper

    return _
