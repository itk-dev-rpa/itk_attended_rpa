import os
from tkinter.messagebox import showerror
import re

import pyodbc

def get_connection() -> pyodbc.Connection:
    """Get a connection to the database."""
    return pyodbc.connect(get_conn_string(), timeout=2)


def get_conn_string() -> str | None:
    """Get the connection string from environment variables."""
    return os.getenv("itk_attended_rpa_conn_String")

def try_connection():
    """Test the connection to the database and show any errors to the user."""
    try:
        get_connection()
    except (pyodbc.InterfaceError, pyodbc.OperationalError) as e:
        error = e.args[1]
        error = re.sub(r"\[.*?\]", "", error)
        error = error.split("(", maxsplit=1)[0]
        showerror("Fejl i forbindelse til database", error)
        raise
    except Exception as e:
        showerror("Ukendt fejl", f"Der er sketen uventet fejl. Kontakt udvikler med følgende fejlbesked:\n{str(e)}")
        raise
