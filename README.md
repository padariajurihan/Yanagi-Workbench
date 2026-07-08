<h1 align="center">
   Yanagi Workbench
</h1>
<p align="center">
<strong><em>Python Automation made easy.</em></strong>
</p>

## What is this project?
Yanagi Workbench is a Python project designed as a Swiss Army knife for automating different kinds of tasks. It can be used for both administrative workflows and IT-related activities, offering a simple interface to perform actions with just a few clicks.

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