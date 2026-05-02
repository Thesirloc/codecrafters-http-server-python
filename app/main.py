import socket  # noqa: F401


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # TODO: Uncomment the code below to pass the first stage
    #
    reuse_port = hasattr(socket, "SO_REUSEPORT")
    with socket.create_server(("localhost", 4221), reuse_port=reuse_port) as server_socket:
        connection, address = server_socket.accept() # wait for client
        print(f"Client connected at {address}")
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
        match path.split("/"):
            case ["",""]:
                response = "HTTP/1.1 200 OK\r\n\r\n"
            case ["", "echo", value]:
                response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(value)}\r\n\r\n{value}"
            case ["", "user-agent"]:
                response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(headers_dict['User-Agent'])}\r\n\r\n{headers_dict['User-Agent']}"
            case _:
                response = "HTTP/1.1 404 Not Found\r\n\r\n"
        connection.sendall(response.encode("utf-8"))


if __name__ == "__main__":
    main()
