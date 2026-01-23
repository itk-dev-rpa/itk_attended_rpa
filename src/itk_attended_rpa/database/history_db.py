
import getpass
import platform

from itk_attended_rpa.database import db_util


def add_robot_log(robot_name: str):
    """Add a log in the history table."""
    connection = db_util.get_connection()
    username = getpass.getuser()
    machine = platform.node()

    connection.execute("INSERT INTO [history] (robot_name, username, machine) VALUES (?, ?, ?)", robot_name, username, machine)
    connection.commit()
