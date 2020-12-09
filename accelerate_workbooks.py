import requests  # Contains methods used to make HTTP requests
import requests
from urllib3.exceptions import InsecureRequestWarning
import xml.etree.ElementTree as ET  # Contains methods used to build and parse XML
import sys

import argparse
import getpass
import logging
import os
from tabulate import tabulate

from dateutil import tz

import tableauserverclient as TSC
from collections import defaultdict
from datetime import time, timedelta

from tableauserverclient import ServerResponseError

# The following packages are used to build a multi-part/mixed request.
# They are contained in the 'requests' library
from requests.packages.urllib3.fields import RequestField
from requests.packages.urllib3.filepost import encode_multipart_formdata

# page size for outputting
PAGE_SIZE = 30

# The namespace for the REST API is 'http://tableausoftware.com/api' for Tableau Server 9.0
# or 'http://tableau.com/api' for Tableau Server 9.1 or later
xmlns = {'t': 'http://tableau.com/api'}

VERSION = 3.6
tokenFile = ".token_profile"

# The maximum size of a file that can be published in a single request is 64MB
FILESIZE_LIMIT = 1024 * 1024 * 64  # 64MB

# For when a workbook is over 64MB, break it into 5MB(standard chunk size) chunks
CHUNK_SIZE = 1024 * 1024 * 5  # 5MB

# If using python version 3.x, 'raw_input()' is changed to 'input()'
if sys.version[0] == '3':
    raw_input = input


class ApiCallError(Exception):
    pass


class UserDefinedFieldError(Exception):
    pass


def _encode_for_display(text):
    """
    Encodes strings so they can display as ASCII in a Windows terminal window.
    This function also encodes strings for processing by xml.etree.ElementTree functions.

    Returns an ASCII-encoded version of the text.
    Unicode characters are converted to ASCII placeholders (for example, "?").
    """
    return text.encode('ascii', errors="backslashreplace").decode('utf-8')


def sign_out_existing_connection(server):
    """
    Destroys the active session and invalidates authentication token.
    'server'        server
    """
    removeTokenFile()
    try:
        if server is not None:
            server.auth.sign_out()
            print("Signed out from current connection to {} successfully".format(server.server_address))
    except Exception as ex:
        print("Unable to sign out {} due to {}.".format(server.server_address, ex))
    return


def sign_in_to_server(server, username, password, site="", ssl_cert_pem=None):
    """
    Signs in to the server specified with the given credentials
    'server'   specified server address
    'username' is the name (not ID) of the user to sign in as.
               Note that most of the functions in this example require that the user
               have server administrator permissions.
    'password' is the password for the user.
    'site'     is the ID (as a string) of the site on the server to sign in to. The
               default is "", which signs in to the default site.
    'ssl_cert_pem' is the file path to the ssl certificate in pem format
    Returns the authentication token and the site ID.
    """
    url = None
    if "http:" in server.lower() or "https:" in server.lower():
        url = "{}/api/{}/auth/signin".format(server, VERSION)
    else:
        url = "http://{}/api/{}/auth/signin".format(server, VERSION)

    ssl_cert_pem = ssl_cert_pem if ssl_cert_pem is not None else False

    # Builds the request
    xml_request = ET.Element('tsRequest')
    credentials_element = ET.SubElement(xml_request, 'credentials', name=username, password=password)
    ET.SubElement(credentials_element, 'site', contentUrl=site)
    xml_request = ET.tostring(xml_request)

    # Make the request to server
    server_response = requests.post(url, data=xml_request, verify=ssl_cert_pem)
    _check_status(server_response, 200)

    # ASCII encode server response to enable displaying to console
    server_response = _encode_for_display(server_response.text)

    # Reads and parses the response
    parsed_response = ET.fromstring(server_response)

    # Gets the auth token and site ID
    token = parsed_response.find('t:credentials', namespaces=xmlns).get('token')
    site_id = parsed_response.find('.//t:site', namespaces=xmlns).get('id')
    user_id = parsed_response.find('.//t:user', namespaces=xmlns).get('id')
    writeTokenToFile(token, site_id, user_id, server, ssl_cert_pem)
    putTokenInEnv(token, site_id, user_id, server, ssl_cert_pem)
    return token, site_id, user_id


def _check_status(server_response, success_code):
    """
    Checks the server response for possible errors.
    'server_response'       the response received from the server
    'success_code'          the expected success code for the response
    Throws an ApiCallError exception if the API call fails.
    """
    if server_response.status_code != success_code:
        parsed_response = ET.fromstring(server_response.text)

        # Obtain the 3 xml tags from the response: error, summary, and detail tags
        error_element = parsed_response.find('t:error', namespaces=xmlns)
        summary_element = parsed_response.find('.//t:summary', namespaces=xmlns)
        detail_element = parsed_response.find('.//t:detail', namespaces=xmlns)

        # Retrieve the error code, summary, and detail if the response contains them
        code = error_element.get('code', 'unknown') if error_element is not None else 'unknown code'
        summary = summary_element.text if summary_element is not None else 'unknown summary'
        detail = detail_element.text if detail_element is not None else 'unknown detail'
        error_message = '{0}: {1} - {2}'.format(code, summary, detail)
        raise ApiCallError(error_message)
    return


def removeTokenFile():
    if os.path.exists(tokenFile):
        try:
            os.remove(tokenFile)
        except OSError as e:
            pass


def writeTokenToFile(token="", site_id="", user_id="", server_url="", ssl_cert_pem=""):
    f = open(tokenFile, "w+")
    f.write(token + " " + site_id + " " + user_id + " " + server_url + " " + ssl_cert_pem)
    f.close()


def promptUsernamePass(args, current_server_address=None):
    if args.server is not None:
        server_url = args.server
    elif current_server_address is not None:
        server_url = current_server_address
    else:
        server_url = raw_input("server: ")

    site = raw_input("site (hit enter for the Default site): ") if args.site is None else args.site
    username = raw_input("username: ") if args.username is None else args.username
    password = getpass.getpass("password: ") if args.password is None else args.password

    if not ("http://" in server_url.lower() or "https://" in server_url.lower()):
        server_url = "http://" + server_url

    ssl_cert_pem = ""
    if "https:" in server_url.lower():
        ssl_cert_pem = raw_input("path to ssl certificate (hit enter to ignore): ") \
            if args.ssl_cert_pem is None else args.ssl_cert_pem

    return server_url, site, username, password, ssl_cert_pem


def readTokenFromFile():
    token = None
    if os.path.exists(tokenFile):
        f = open(tokenFile, "r")
        if f.mode == 'r':
            token = f.read()

        f.close()

    if token:
        return token.split(' ')

    return None, None, None, None, None


def readTokenFromEnv():
    return os.getenv('auth_token'), os.getenv('site_id'), os.getenv('user_id'), \
           os.getenv('server_url'), os.getenv('ssl_cert_pem')


def putTokenInEnv(auth_token, site_id, user_id, serverurl, ssl_cert_pem):
    os.environ['auth_token'] = auth_token
    os.environ['site_id'] = site_id
    os.environ['user_id'] = user_id
    os.environ['server_url'] = serverurl
    os.environ['ssl_cert_pem'] = ssl_cert_pem


def sign_in(args, current_server_address=None):
    serverurl, site, username, password, ssl_cert_pem = promptUsernamePass(args, current_server_address)

    try:
        auth_token, site_id, user_id = sign_in_to_server(serverurl, username, password, site, ssl_cert_pem)
        server = set_up_tsc_server(serverurl, site_id, user_id, auth_token, ssl_cert_pem)
        if server is not None:
            print("Signed in to {} successfully".format(serverurl))
        return server
    except ApiCallError as error:
        print("\n{}, please verify your username, password, and site.".format(error))
        return None
    except Exception:
        print("Unable to connect to {}".format(serverurl))
        return None


def set_up_tsc_server(serverurl, site_id, user_id,
                      auth_token, ssl_cert_pem):
    server = TSC.Server(serverurl)

    if "https:" in serverurl.lower():
        server.add_http_options({'verify': ssl_cert_pem if len(ssl_cert_pem) > 0 else False})

    server._set_auth(site_id, user_id, auth_token)

    server.use_server_version()

    return server if connection_alive(server) else None


def connection_alive(server):
    try:
        server.sites.get()
        return True
    except Exception:
        return False


def cleanStrings(auth_token, site_id, user_id, serverurl, ssl_cert_pem):
    return auth_token.strip(), site_id.strip(), user_id.strip(), serverurl.strip(), ssl_cert_pem.strip()


def get_session_connection_to_server():
    try:
        auth_token, site_id, user_id, serverurl, ssl_cert_pem = readTokenFromEnv()
        if not auth_token:
            auth_token, site_id, user_id, serverurl, ssl_cert_pem = readTokenFromFile()
            if auth_token:
                try:
                    auth_token, site_id, user_id, serverurl, ssl_cert_pem = cleanStrings(auth_token, site_id,
                                                                                         user_id, serverurl,
                                                                                         ssl_cert_pem)
                except Exception:
                    pass

        if auth_token is not None:
            if not ("http://" in serverurl.lower() or "https:" in serverurl.lower()):
                serverurl = "http:" + serverurl

            return set_up_tsc_server(serverurl, site_id,
                                     user_id, auth_token, ssl_cert_pem)
    except Exception:
        pass
    return None


def sign_out():
    server = get_session_connection_to_server()
    if server is not None:
        sign_out_existing_connection(server)
    else:
        removeTokenFile()  # in case the auth token expires
        print("No existing connection to any server.")


def need_to_relogin(args, server):
    if server is None:
        return True

    current_site = None
    try:
        current_site = server.sites.get_by_id(server.site_id)
    except Exception:
        pass

    current_site = current_site.content_url if current_site is not None else None
    current_server_address = server.server_address
    if "http://" not in current_server_address:
        current_server_address = "http://" + current_server_address

    new_site = args.site if args.site is not None else current_site
    new_server_address = args.server if args.server is not None else current_server_address
    if new_server_address is not None and "http://" not in new_server_address:
        new_server_address = "http://" + new_server_address

    return current_site != new_site or current_server_address != new_server_address


def get_authenticated_connection_to_server(args):
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    server = get_session_connection_to_server()
    current_server_address = server.server_address if server is not None else None
    if need_to_relogin(args, server):
        sign_out_existing_connection(server)
    elif server is not None:
        return server
    return sign_in(args, current_server_address)


class UserResponse:
    YES = "y"
    NO = "n"
    YES_FOR_ALL = "a"
    NO_FOR_ALL = "q"


def assert_options_valid(args):
    if args.logout is not None and (args.server is not None or args.site is not None):
        print("Do not use --logout and --server at the same time.")
        return False

    if args.logout is not None or args.server is not None or args.site is not None:
        return True

    num_enable_actions = sum(action is not None for action in
                             [args.enable])

    if num_enable_actions == 1:
        if args.enable is not None and len(args.enable) > 2:
            print('--enable can only be followed by one workbook path and optional a sheet name')
            return False
        else:
            return True

    return True


def get_workbook_from_paths(server, data_acceleration_config, workbook_path, sheet_name):
    # sheet_path may be in form of
    # 1. project/workbook for all sheets
    # 2. project/workbook/sheet for only one sheet
    workbook_id_to_workbook = get_workbook_from_path(server, workbook_path)

    if len(workbook_id_to_workbook) == 0:
        return None

    workbook = list(workbook_id_to_workbook.values())[0][0]
    workbook.data_acceleration_config = data_acceleration_config
    server.workbooks.populate_views(workbook)

    views = []
    for view in workbook.views:
        if view.name == sheet_name:
            view.data_acceleration_config['acceleration_enabled'] = data_acceleration_config['acceleration_enabled']
            views.append(view);
    workbook._views = views;
    return workbook


def update_sheets(server, args, data_acceleration_config, site_content_url):
    workbook_path, sheet_name = find_sheet_path(args)
    if workbook_path is None:
        print("Use '--enable workbook_path sheet-path to specify the path of sheets. No sheet means all sheets\n")
        print('\n')
        return False

    if not assert_site_enabled_for_materialized_views(server, site_content_url):
        return False

    workbook = get_workbook_from_paths(server, data_acceleration_config, workbook_path, sheet_name)

    if workbook is None:
        return False

    try:
        update_workbook_internal(server, workbook)
    except ServerResponseError as error:
        print("Unable to {} {}/{}. {}".format(
            "enable" if data_acceleration_config["acceleration_enabled"] else "disable",
            workbook_path, error.detail
        ))
        return False

    print("Workbook update succeeded.")

    return True


def handle_enable_disable_command(server, args, site_content_url):
    data_acceleration_config = create_data_acceleration_config(args)

    return update_sheets(server, args, data_acceleration_config, site_content_url)


def find_sheet_path(args):
    if args.enable is not None and len(args.enable) > 0:
        return args.enable[0], args.enable[1] if len(args.enable) > 1 else None
    else:
        return None


def parse_workbook_path(file_path):
    # parse the list of project path of workbooks
    workbook_paths = sanitize_workbook_list(file_path, "path")

    workbook_path_mapping = defaultdict(list)
    for workbook_path in workbook_paths:
        workbook_project = workbook_path.rstrip().split('/')
        workbook_path_mapping[workbook_project[-1]].append('/'.join(workbook_project[:-1]))
    return workbook_path_mapping


def get_workbook_from_path(server, workbook_path):
    all_projects = {project.id: project for project in TSC.Pager(server.projects)}
    workbook_id_to_workbook = dict()
    workbook_path_list = workbook_path.rstrip().split('/')
    workbook_project = '/'.join(workbook_path_list[:-1])
    workbook_name = workbook_path_list[-1]

    req_option = TSC.RequestOptions()
    req_option.filter.add(TSC.Filter(TSC.RequestOptions.Field.Name,
                                     TSC.RequestOptions.Operator.Equals,
                                     workbook_name))
    workbooks = list(TSC.Pager(server.workbooks, req_option))
    for workbook in workbooks:
        path = find_project_path(all_projects[workbook.project_id], all_projects, "")
        if path == workbook_project:
            workbook_id_to_workbook[workbook.id] = workbook, workbook_project
            break

    if len(workbook_id_to_workbook) == 0:
        print("Unable to find {}".format(workbook_path))
    return workbook_id_to_workbook


def find_project_path(project, all_projects, path):
    # project stores the id of it's parent
    # this method is to run recursively to find the path from root project to given project
    path = project.name if len(path) == 0 else project.name + '/' + path

    if project.parent_id is None:
        return path
    else:
        return find_project_path(all_projects[project.parent_id], all_projects, path)


def update_workbook_internal(server, workbook):
    # without removing the workbook name, the rest api server code will
    # think the user would change the name of the workbook
    try:
        workbook_name = workbook.name
        workbook.name = None
        server.workbooks.update(workbook)
    finally:
        workbook.name = workbook_name


def create_data_acceleration_config(args):
    data_acceleration_config = dict()
    data_acceleration_config['acceleration_enabled'] = args.enable is not None
    data_acceleration_config['accelerate_now'] = True if args.accelerate_now else False
    data_acceleration_config['last_updated_at'] = None
    data_acceleration_config['acceleration_status'] = None
    return data_acceleration_config


def assert_site_options_valid(args):
    if args.accelerate_now:
        print('"--accelerate-now" only applies to workbook/project type')
        return False
    return True


def assert_site_enabled_for_materialized_views(server, site_content_url):
    parent_site = server.sites.get_by_content_url(site_content_url)
    if parent_site.data_acceleration_mode == "disable":
        print('Cannot update workbook/project because site is disabled for Workbook Acceleration')
        return False
    return True


def assert_project_valid(project_name, projects):
    if len(projects) == 0:
        print("Cannot find project: {}".format(project_name))
        return False
    return True


def sanitize_workbook_list(file_name, file_type):
    if not os.path.isfile(file_name):
        print("Invalid file name '{}'".format(file_name))
        return []
    file_list = open(file_name, "r")

    if file_type == "name":
        return [workbook.rstrip() for workbook in file_list if not workbook.isspace()]
    if file_type == "path":
        return [workbook.rstrip() for workbook in file_list if not workbook.isspace()]


def main():
    parser = argparse.ArgumentParser(description='Workbook Acceleration settings for sites/workbooks.')
    parser.add_argument('--server', '-s', required=False, help='Tableau server address')
    parser.add_argument('--username', '-u', required=False, help='username to sign into server')
    parser.add_argument('--password', '-p', required=False, help='password to sign into server')
    parser.add_argument('--ssl-cert-pem', '-ssl', required=False,
                        help='ssl certificate in Privacy Enhanced Mail (PEM) encoding')
    parser.add_argument('--enable', '-en', required=False, nargs='*', metavar="WORKBOOK_PATH SHEET_NAME",
                        help='enable Workbook Acceleration')
    parser.add_argument('--site', '-si', required=False,
                        help='the server Default site will be use unless the site name is specified')
    parser.add_argument('--logging-level', '-l', choices=['debug', 'info', 'error'], default='error',
                        help='desired logging level (set to error by default)')
    parser.add_argument('--logout', '-lo', required=False, help="logout the current active session",
                        action='store_const', const=True)
    parser.add_argument('--accelerate-now', '-an', required=False, action='store_true',
                        help='create Workbook Acceleration Views for workbooks immediately')

    args = parser.parse_args()

    if not assert_options_valid(args):
        parser.print_usage()
        return

    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    # ignore warnings for missing ssl cert for https connections
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    if args.logout is not None:
        sign_out()
        return

    server = get_authenticated_connection_to_server(args)

    if server is None:
        return

    # site content url is the TSC term for site id
    site = server.sites.get_by_id(server.site_id)
    site_content_url = site.content_url

    if args.enable is not None:
        if not handle_enable_disable_command(server, args, site_content_url):
            return


if __name__ == "__main__":
    main()
