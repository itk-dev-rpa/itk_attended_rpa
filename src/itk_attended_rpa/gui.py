"""This is the main module of the application which shows the gui."""

import json
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import webbrowser
import subprocess
import threading

from itk_attended_rpa.database import constants_db, db_util, history_db, robots_db
from itk_attended_rpa import file_util


class App(tk.Tk):
    """The main application."""
    def __init__(self):
        super().__init__()

        self.process = None
        self.popup = None

        self.title("ITK Attended RPA")

        tk.Label(self, text="Velkommen til ITK Attended RPA").pack()
        tk.Label(self, text="Her kan du vælge en robot, som du vil køre lokalt på din pc.").pack()
        tk.Label(self, text="Vælg en robot i listen og tryk 'Kør', og så bliver robotten").pack()
        tk.Label(self, text="automatisk downloadet og startet.").pack()

        self.selected = tk.StringVar(value="")
        self.dropdown = ttk.Combobox(self, textvariable=self.selected, values=[], state="readonly", width=40)
        self.dropdown.pack(pady=10)
        self.update_options()

        tk.Button(self, text="Åben vejledning", command=self.open_readme).pack()

        self.print_button = tk.Button(self, text="Kør", command=self.run_robot)
        self.print_button.pack(pady=10)

        self.mainloop()

    def update_options(self):
        """Update the robot dropdown with robots in the database."""
        robots_list = robots_db.get_robots()
        self.robot_dict = {robot.name: robot for robot in robots_list}

        new_options = [robot.name for robot in robots_list]
        self.dropdown["values"] = new_options
        self.selected.set(new_options[0])

    def open_readme(self):
        """Open the readme url of the selected robot."""
        robot = self.robot_dict[self.selected.get()]
        if robot.readme_url:
            webbrowser.open(robot.readme_url)
        else:
            messagebox.showinfo("Ingen readme", "Denne robot ser ikke ud til at have en vejledning.")

    def run_robot(self):
        """Run the selected robot."""
        robot = self.robot_dict[self.selected.get()]
        self.show_process_popup(robot.name)
        history_db.add_robot_log(robot.name)

        file_util.download_robot(robot)
        main_file = file_util.find_main_file(robot)

        constants_dict = constants_db.get_constants()
        constants_str = json.dumps(constants_dict, ensure_ascii=False)

        cmd = ["python", main_file, constants_str]
        self.process = subprocess.Popen(cmd)  # pylint: disable=consider-using-with
        threading.Thread(target=self.monitor_process, daemon=True).start()

    def show_process_popup(self, robot_name: str):
        """Show a popup which blocks the main window while the robot is running."""
        self.popup = tk.Toplevel(self)
        self.popup.title("Robot kører")
        self.popup.geometry("300x120")
        self.popup.resizable(False, False)

        # Make it modal (blocks main window)
        self.popup.transient(self)
        self.popup.grab_set()
        self.popup.protocol("WM_DELETE_WINDOW", lambda: None)

        tk.Label(self.popup, text=f"{robot_name} kører...").pack(pady=10)
        tk.Button(self.popup, text="Stop robot", command=self.kill_process).pack(pady=10)

        # Center popup on main window
        self.popup.update_idletasks()

        root_x = self.winfo_x()
        root_y = self.winfo_y()
        root_width = self.winfo_width()
        root_height = self.winfo_height()

        popup_width = self.popup.winfo_width()
        popup_height = self.popup.winfo_height()

        x = root_x + (root_width // 2) - (popup_width // 2)
        y = root_y + (root_height // 2) - (popup_height // 2)

        self.popup.geometry(f"+{x}+{y}")

    def monitor_process(self):
        """Monitor the robot process and close blocking
        popup when done.
        """
        return_code = self.process.wait()
        self.after(0, self.close_popup)

        if return_code == 0:
            messagebox.showinfo("Færdig", f"Robotten er færdig.")
        else:
            messagebox.showerror("Fejl", "Robotten stoppede uventet.")

    def close_popup(self):
        """Close the process popup."""
        if self.popup.winfo_exists():
            self.popup.grab_release()
            self.popup.destroy()

    def kill_process(self):
        """Terminate the running robot process."""
        if self.process and self.process.poll() is None:
            self.process.terminate()


def main():
    """The main entry point for the cli command 'itk-attended-rpa'"""
    if not db_util.get_conn_string():
        messagebox.showerror("Fejl", "'itk_attended_rpa_conn_String' er ikke sat i miljøvariabler.")
    else:
        db_util.try_connection()
        App()
