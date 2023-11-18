import json
import socket
import biplane
from theme_park_api import get_theme_parks_from_json

server = biplane.Server()


def main_page(park_id):
    page = "<link rel=\"stylesheet\" href=\"style.css\">"
    page += "</head>"
    page += "<body style=\"background-color:white;\">"

    page += "<div class=\"navbar\">"
    page += "<a href=\"#home\">Theme Park Wait Times</a>"
    page += "</div>"

    f = open('theme-park-list.json')
    data = json.load(f)
    f.close()
    park_list = sorted(get_theme_parks_from_json(data))

    page += "<div>"
    page += "<form action=\"/action\">"
#    page += "<label for=\"park\">Choose a theme park:</label></br>"
    page += "<br>"
    page += "<select name=\"park-names\" id=\"park-id\">\n"
    for park in park_list:
        park_name = remove_non_ascii(park[0])
        if park[1] == park_id:
            page += f"<option value=\"{park[1]}\" selected>{park_name}</option>\n"
        else:
            page += f"<option value=\"{park[1]}\">{park_name}</option>\n"
    page += "</select>\n"

    page += "<input type=\"submit\">"
    page += "</form>"
    page += "</div>"
    return page


def remove_non_ascii(orig_str):
    new_str = ""
    for c in orig_str:
        if ord(c) < 128:
            new_str += c
    return new_str


@server.route("/", "GET")
def main(query_parameters, headers, body):
    page = main_page(-1)
    response = biplane.Response(page, content_type="text/html")
    return response


@server.route("/style.css", "GET")
def main(query_parameters, headers, body):
    f = open("style.css")
    data = f.read()
    f.close()
    return biplane.Response(data, content_type="text/html")


@server.route("/action", "GET")
def main(query_parameters, headers, body):
    park_id = query_parameters.split("=")
    page = main_page(int(park_id[1]))
    return biplane.Response(page, content_type="text/html")


server_socket = socket.socket()
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,
                         1)  # allow the server to reuse the address immediately after it's been closed
for _ in server.start(server_socket, listen_on=('127.0.0.1', 8000)):
    pass

