from genericpath import exists
import socket  # noqa: F401
import threading
import os
import sys
import gzip

if "--directory" in sys.argv:
    root_directory = sys.argv[sys.argv.index("--directory") + 1]
else:
    root_directory = "."
print(f"global variable root_directory set to - {root_directory}")

def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # TODO: Uncomment the code below to pass the first stage
    start_server()
    
def start_server():
    with socket.create_server(("localhost", 4221)) as server_socket:
        print("Server started at localhost:4221")
        while True:
            connection, address = server_socket.accept() # wait for client
            print(f"Client connected at {address}")
            threading.Thread(target=handle_client, args=(connection, address)).start()

def handle_client(connection, address):
    data = connection.recv(1024)
    print(f"Received data: {data.decode('utf-8')}")
    #Extract the path from the request line
    all_request_lines = data.decode('utf-8').split('\r\n')
    request_line = all_request_lines[0]
    method, path, version = request_line.split()
    headers_list = all_request_lines[1:all_request_lines.index("")]
    headers_dict = {h.split(":", 1)[0].strip(): h.split(":", 1)[1].strip() for h in headers_list if ":" in h}
    body_list = all_request_lines[all_request_lines.index("")+1:]
    body_dict = {b.split(":", 1)[0].strip(): b.split(":", 1)[1].strip() for b in body_list if ":" in b}
    match method:
        case "GET":
            response = create_response(*get_request(path, headers_dict))
        case "POST":
            response = create_response(*post_request(path, headers_dict, body_list))
        case _:
            response = create_response("405 Method Not Allowed", {}, "")
    connection.sendall(response)
    connection.close()

def get_request(path, headers_dict):
    match path.split("/"):
        case ["",""]:
            status_code = "200 OK"
            headers = {}
            content = ""
            response = status_code, headers, content
            # response = "HTTP/1.1 200 OK\r\n\r\n"
        case ["", "echo", value]:
            if "Accept-Encoding" in headers_dict and "gzip" in headers_dict.get("Accept-Encoding").split(", "): 
                status_code = "200 OK"
                headers = {
                    "Content-Type": "text/plain",
                    "Content-Length": len(value),
                    "Content-Encoding": "gzip"
                }
                content = value
                compressed_content = gzip.compress(content)
                response = status_code, headers, compressed_content
                # response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(value)}\r\nContent-Encoding: gzip\r\n\r\n{value}"
            else:
                status_code = "200 OK"
                headers = {
                    "Content-Type": "text/plain",
                    "Content-Length": len(value)
                }
                content = value
                response = status_code, headers, content
                # response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(value)}\r\n\r\n{value}"
        case ["", "files", value]:
            file_path = os.path.join(root_directory, value)
            if os.path.exists(file_path):
                status_code = "200 OK"
                headers = {
                    "Content-Type": "application/octet-stream",
                    "Content-Length": len(serve_file(file_path))
                }
                content = serve_file(file_path)
                response = status_code, headers, content
            else:
                status_code = "404 Not Found"
                headers = {}
                content = ""
                response = status_code, headers, content
        case ["", "user-agent"]:
            status_code = "200 OK"
            headers = {
                "Content-Type": "text/plain",
                "Content-Length": len(headers_dict.get("User-Agent"))
            }
            content = headers_dict.get("User-Agent")
            response = status_code, headers, content
        case _:
            status_code = "404 Not Found"
            headers = {}
            content = ""
            response = status_code, headers, content
    return response

def post_request(path, headers_dict, body_list):
    match path.split("/"):
        case ["",""]:
            status_code = "200 OK"
            headers = {}
            content = ""
            response = status_code, headers, content
        case ["", "files", value]:
            file_path = os.path.join(root_directory, value)
            with open(file_path, "w", encoding="utf-8") as f:
                content = "".join(body_list)
                f.write(content)
            status_code = "201 Created"
            headers = {}
            content = ""
            response = status_code, headers, content
        case _:
            status_code = "404 Not Found"
            headers = {}
            content = ""
            response = status_code, headers, content
    return response



def serve_file(path):
    with open(path, "r") as f:
        return f.read()

def create_response(status_code, headers, content):
    response = f"HTTP/1.1 {status_code}\r\n"
    for header, value in headers.items():
        response += f"{header}: {value}\r\n"
    response += f"\r\n{content}"
    return response.encode("utf-8")

if __name__ == "__main__":
    main()
