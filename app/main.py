import socket  # noqa: F401


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # TODO: Uncomment the code below to pass the first stage
    #
    with socket.create_server(("localhost", 4221), reuse_port=True) as server_socket:
        connection, address = server_socket.accept() # wait for client
        print(f"Connected to {address}")
        response = "HTTP/1.1 200 OK\r\n\r\n"
        connection.sendall(response.encode("utf-8"))

if __name__ == "__main__":
    main()
