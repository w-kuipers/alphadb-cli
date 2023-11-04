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
import json
from src.utils.config import config_get, config_write
from requests import get
from requests.exceptions import JSONDecodeError, ConnectionError
from inquirer import Text, prompt
from inquirer.errors import ValidationError
from src.utils.common import console

"Adding a new version source to config"
def add_version_source() -> str | None:
    ## ! Do not allow spaces
    print("Version sources can either be local JSON files or URL's returning JSON data.\n")
    
    try: ## To catch ConnectionError
        #### Function to validate path/url
        def pathval(path: str):
            if path[0:4] == "http":
                r = get(path)
                if not r.status_code == 200:
                    raise ValidationError("", reason=f"URL responded with {r.status_code}")
                return True

            if not os.path.isfile(path):
                raise ValidationError("", reason="This path does not point towards a JSON file.")
            return True
    
        #### Promt user to input path
        questions = [Text("path", message="Please provide either an absolute local file path or a local/remote URL", validate=lambda _, x: pathval(x))]
        answers = prompt(questions)
        
        #### If answers is None, user probably aborted
        if answers == None: return

        path = answers["path"]
        
        if path[0:4] == "http":
            template_name = get(path).json()["name"]
        else:
            with open(path) as version_json:
                template_name = json.load(version_json)["name"]

    #### TODO This connection error catch does not seem to work  
    except ConnectionError:
        console.print("\n[red]Unable to establish connection[/red]\n")
        return

    except JSONDecodeError:
        console.print("\n[red]The supplied URL did not respond with compatible data[/red]\n")
        return

    ##### TODO maybe add a check if the data has no errors
    
    questions = [Text("name", message="Name the template", default=template_name)]
    answers = prompt(questions)

    #### If answers is NOne, user probably aborted
    if answers == None: return

    name = answers["name"]

    ##http://localhost:8000/fmm/v1/database/db-version-config-information/

    #### Write to config file
    vs = config_get("VERSION_SOURCES", fallback=True)
    if vs == None: vs = {}
    vs[name] = path
    config_write({"VERSION_SOURCES": vs})

    return path
