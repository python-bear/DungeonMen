import os
import shutil
import pathlib


# Function to create a desktop shortcut
def create_desktop_shortcut(shortcut_name, target_path):
    desktop_path = pathlib.Path.home() / 'Desktop'
    shortcut_path = desktop_path / f'{shortcut_name}.lnk'

    with open(shortcut_path, 'w') as shortcut:
        double_backslash = "\\"
        shortcut.write(
            f'[InternetShortcut]\nURL=file://{target_path.replace(double_backslash, "/")}\nIconIndex=0\nIconFile='
            f'{target_path.replace(double_backslash, "/")}\n'
        )


# Function to perform the installation
def install_app():
    # Get the path to the Saved Games folder
    saved_games_path = pathlib.Path.home() / 'Saved Games'

    # Prompt the user for installation directory or use Saved Games folder as default
    install_path = input(f'Enter the installation directory (default: {saved_games_path}): ') or str(saved_games_path)

    # Create the installation directory if it doesn't exist
    os.makedirs(install_path, exist_ok=True)

    # Unzip your app files to the installation directory (assuming your app files are in a ZIP file)
    app_zip_path = 'path/to/your/app.zip'
    shutil.unpack_archive(app_zip_path, install_path)

    # Remove the original ZIP file if needed
    os.remove(app_zip_path)

    # Create a desktop shortcut for the app
    app_executable_path = install_path / 'main.exe'  # Replace 'main.exe' with the actual executable name
    create_desktop_shortcut('My App', app_executable_path)

    print('Installation completed successfully.')


if __name__ == "__main__":
    # Run the installation
    install_app()
