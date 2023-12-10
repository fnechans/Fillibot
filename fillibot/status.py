import json
from typing import Any
import datetime
import os
from typing import Dict


class StatusVariable:
    _status = {}


def Status() -> Dict[str, Any]:
    return Status._status


def save(file_name: str = 'status.json'):
    current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M_%S")
    file_name_time = f"{file_name}.{current_time}"  # only if not quiet
    with open(file_name_time, 'w') as f:
        json.dump(Status(), f)
    if os.path.exists(file_name):
        os.remove(file_name)
    os.symlink(file_name_time, file_name)


def load(file_name: str = 'status.json'):
    with open(file_name, 'r') as f:
        StatusVariable._status = json.load(f)
