"""This module is responsible for interactions with the constants table in the database."""

from itk_attended_rpa.database import db_util


def get_constants() -> dict[str, str]:
    """Get all constants from the database as a key/value dict."""
    connection = db_util.get_connection()
    constants = connection.execute("SELECT name, value FROM constants").fetchall()
    return {c[0]: c[1] for c in constants}
