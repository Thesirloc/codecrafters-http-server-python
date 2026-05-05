from genericpath import exists
import socket  # noqa: F401
import threading
import os
import sys

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
            response = get_request(path, headers_dict)
        case "POST":
            response = post_request(path, headers_dict, body_dict)
        case _:
            response = "HTTP/1.1 405 Method Not Allowed\r\n\r\n"
    connection.sendall(response.encode("utf-8"))
    connection.close()

def get_request(path, headers_dict):
    match path.split("/"):
        case ["",""]:
            response = "HTTP/1.1 200 OK\r\n\r\n"
        case ["", "echo", value]:
            response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(value)}\r\n\r\n{value}"
        case ["", "user-agent"]:
            response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(headers_dict['User-Agent'])}\r\n\r\n{headers_dict['User-Agent']}"
        case ["", "files", value]:
            file_path = os.path.join(root_directory, value)
            if os.path.exists(file_path):
                content = serve_file(file_path)
                response = f"HTTP/1.1 200 OK\r\nContent-Type: application/octet-stream\r\nContent-Length: {len(content)}\r\n\r\n{content}"
            else:
                response = "HTTP/1.1 404 Not Found\r\n\r\n"
        case _:
            response = "HTTP/1.1 404 Not Found\r\n\r\n"
    return response

def post_request(path, headers_dict, body_list):
    match path.split("/"):
        case ["", "files", value]:
            file_path = os.path.join(root_directory, value)
            with open(file_path, "w") as f:
                f.write("\r\n".join(body_list))
            response = "HTTP/1.1 201 Created\r\nContent-Length: 0\r\n\r\n"
        case _:
            response = "HTTP/1.1 404 Not Found\r\n\r\n"
    return response



def serve_file(path):
    with open(path, "r") as f:
        return f.read()

if __name__ == "__main__":
    main()
