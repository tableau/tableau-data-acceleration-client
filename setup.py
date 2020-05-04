import zipfile
import os
import subprocess
import sys
import shutil

tsc_download_file = 'tsc_development.zip'

# Tabelau Server Client version supporting accelerate_workbooks.py
tsc_version = '5812dc9043348f7b80ad0c4dd363652a2351756d'

server_client_download_url = 'https://github.com/tableau/server-client-python/archive/{}.zip'.format(tsc_version)
tsc_lib_directory = 'server-client-python-{}'.format(tsc_version)
script_directory = os.path.dirname(os.path.realpath(__file__))


def download(download_url, download_directory, download_file_name):
    import urllib.request
    urllib.request.urlretrieve(download_url, os.path.join(download_directory, download_file_name))


def download_file_and_unzip(download_url, download_directory, download_file_name):
    download(download_url, download_directory, download_file_name)

    with zipfile.ZipFile(os.path.join(download_directory, download_file_name), "r") as zip_ref:
        zip_ref.extractall(download_directory)


def install(package):
    subprocess.check_call([sys.executable, "-m", 'pip', "install", "--upgrade", package])


def assert_python_version():
    version = sys.version_info
    if not (version.major == 3 and version >= (3, 5, 0)):
        print("Tableau Server Client only supports Python 3.5 and later. "
              "Your Python version is {}.{}.{}".format(version.major, version.minor, version.micro))
        return False
    return True


def download_tableu_server_client():
    try:
        download_file_and_unzip(server_client_download_url, script_directory, tsc_download_file)
        return True
    except Exception as exception:
        print("Unable to download Tableau Server Client. Error: {}".format(exception))
        return False


def clean_up():
    try:
        os.remove(os.path.join(script_directory, tsc_download_file))
        shutil.rmtree(os.path.join(script_directory, tsc_lib_directory))
        return True
    except Exception as exception:
        print("Unable to delete installation files")
        return False


def install_dependencies():
    try:
        install('tabulate')
        install('python-dateutil')
        install(os.path.join(script_directory, tsc_lib_directory))
    except:
        print("Unable to install the dependencies")


def main():
    if not assert_python_version():
        return

    try:
        if download_tableu_server_client():
            install_dependencies()
    finally:
        clean_up()


if __name__ == "__main__":
    main()
