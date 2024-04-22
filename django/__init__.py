import os
import sys
import venv

# The following code checks if the script is being run from a virtual environment or not.
# If it is, it prints a message indicating that a virtual environment is active.
# If it's not, it checks the operating system.
# If the operating system is Windows (os.name == "nt"), it sets the virtual environment name to "venv_django_win" and tries to activate it.
# If the virtual environment doesn't exist (throws a NameError), it creates a new one with the specified name.
# If the operating system is not Windows, it assumes it's Linux and does the same as above but with the virtual environment name set to "venv_django_linux".
if os.name == "nt":
    venvname = "venv_django_win"    
    print(f"Checking for {venvname}")
    try:
        import venv_django_win as venv
        venv.activate(venvname)
        os.system(f"pip install -r {os.path.join(os.path.dirname(__file__), 'requirements.txt')}")
    except NameError:
        venv.create(venvname, with_pip=True)
        venv.activate(venvname)
        os.system(f"pip install -r {os.path.join(os.path.dirname(__file__), 'requirements.txt')}")
else:
    venvname = "venv_django_linux"
    print(f"Checking for {venvname}")
    try:
        venv.activate(venvname)
        os.system(f"pip install -r {os.path.join(os.path.dirname(__file__), 'requirements.txt')}")
    except NameError:
        venv.create(venvname, with_pip=True)
        venv.activate(venvname)
        os.system(f"pip install -r {os.path.join(os.path.dirname(__file__), 'requirements.txt')}")

# After setting up the virtual environment, it imports the manage module from the myproject package in Django.
from django.myproject import manage

# If this script is the main module, it sets the command line arguments to ["runserver"].
# This is equivalent to running "python manage.py runserver" from the command line, which starts the Django development server.
if '__main__' == __name__:
    sys.argv = ["runserver"]
    manage.main()