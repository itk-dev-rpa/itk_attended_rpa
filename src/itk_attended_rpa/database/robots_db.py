from dataclasses import dataclass

from itk_attended_rpa.database import db_util

@dataclass
class Robot:
    name: str
    location_url: str
    readme_url: str


def get_robots() -> tuple[Robot]:
    """Get all robots in the database."""
    connection = db_util.get_connection()
    robots = connection.execute("SELECT name, location_url, readme_url FROM ROBOTS").fetchall()

    return tuple(Robot(*row) for row in robots)


if __name__ == '__main__':
    robots = get_robots()
    print(robots)