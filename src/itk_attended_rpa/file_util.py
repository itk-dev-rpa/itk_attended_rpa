"""This module is responsible for handling downloaded robots on the file system."""

from pathlib import Path
import hashlib
from io import BytesIO
import zipfile
import shutil

import requests

from itk_attended_rpa.database.robots_db import Robot


def download_robot(robot: Robot):
    """Download the given robot.
    If a robot with the same name already exists on the system
    the hash file is checked to see if the remote robot is different.
    """
    # Download robot data
    response = requests.get(robot.location_url, timeout=30)
    response.raise_for_status()
    robot_data = response.content

    # Check if the new data matches existing data
    existing_hash = get_robot_hash(robot)
    new_hash = calculate_hash(robot_data)

    if existing_hash == new_hash:
        return

    # Delete old data
    robot_folder = get_robot_folder(robot)
    if robot_folder.is_dir():
        shutil.rmtree(robot_folder)

    # Save new data
    save_robot(robot, robot_data)
    save_hash_file(robot, new_hash)


def save_robot(robot: Robot, data: bytes):
    """Save robot's bytedata to the robot's folder.
    If the given data is a zipfile it's unpacked.
    If not it's assumed to be a single python file.
    """
    folder_path = get_robot_folder(robot)
    byte_io = BytesIO(data)

    if zipfile.is_zipfile(byte_io):
        with zipfile.ZipFile(byte_io) as zip_file:
            zip_file.extractall(folder_path)
    else:
        file_path = folder_path / "main.py"
        file_path.write_bytes(data)


def get_main_folder() -> Path:
    """Get the path to the robots folder.
    Also ensures the folder exists.
    """
    path = Path("~/itk_attended_rpa").expanduser()
    if not path.is_dir():
        path.mkdir(parents=True)
    return path


def get_robot_folder(robot: Robot) -> Path:
    """Get the folder of the given robot.
    Also ensure the folder exists.
    """
    path = get_main_folder() / robot.name
    if not path.is_dir():
        path.mkdir()
    return path


def get_hash_path(robot: Robot) -> Path:
    """Get the path of the hash-file for the given robot."""
    folder_dir = get_robot_folder(robot)
    return folder_dir / ".hash"


def get_robot_hash(robot: Robot) -> str | None:
    """Get the hash of an existing robor in the file system."""
    hash_file = get_hash_path(robot)
    if not hash_file.is_file():
        return None
    return hash_file.read_text()


def save_hash_file(robot: Robot, hash_str: str):
    """Save the given hash to the robot's folder."""
    hash_file = get_hash_path(robot)
    hash_file.write_text(hash_str)


def calculate_hash(data: bytes) -> str:
    """Calculate the hash of the given data."""
    return hashlib.sha1(data).hexdigest()


def find_main_file(robot: Robot) -> Path:
    """Find the main.py file of the given robot."""
    folder_path = get_robot_folder(robot)
    return next(folder_path.glob("**/main.py"))
