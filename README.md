<h1 align="center">
   Yanagi Workbench
</h1>
<p align="center">
<strong><em>Python Automation made easy.</em></strong>
</p>

## What is this project?
Yanagi Workbench is a Python project designed as a Swiss Army knife for automating different kinds of tasks. It can be used for both administrative workflows and IT-related activities, offering a simple interface to perform actions with just a few clicks.

## Project structure
The project is organized to separate interface components from application logic and configuration. The main directories and files are:

| Path | Type | Purpose |
| --- | --- | --- |
| `main.py` | Entry point | Starts the application and loads the UI from `app/ui/main_window.py`. |
| `requirements.txt` | Configuration | Lists Python dependencies required to run the project. |
| `README.md` | Documentation | Explains how the project works and how to run it. |
| `assets/icons/` | Assets | Stores icon files used by buttons and UI elements. |
| `app/ui/` | UI layer | Contains frame and window interface definitions for the application. |
| `app/tools/` | Logic layer | Contains logic classes and helper modules used by the UI frames. |
| `app/config/` | Configuration | Stores application settings such as title and window size constants. |
| `app/shared/` | Shared utilities | Contains shared helpers used across the app. |

### Directory roles
- `app/ui/`: interface code only. Each file defines a visible frame or window behavior.
- `app/tools/`: application logic only. Each module implements the functions used by the UI frames.
- `app/config/`: configuration values for the application, such as constants and settings.
- `app/shared/`: utility functions and shared constants used by multiple modules.
- `assets/icons/`: icons used by buttons and UI widgets.

## How to run the application
To run the project, you will need:

- Python installed on your computer
- The dependencies listed in the requirements.txt file

### Step by step
1. Open the terminal in the project folder.
2. Create a virtual environment (optional, but recommended):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   python main.py
   ```

### Important notes
- If the python command does not work, try python3 instead.
- On some Linux distributions, you may need to install the tkinter package for the graphical interface to work correctly. Example on Ubuntu/Debian:
  ```bash
  sudo apt update && sudo apt install python3-tk
  ```

With that, the application should open normally and be ready to use.