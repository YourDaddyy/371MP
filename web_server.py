import socket
import threading
import os
from datetime import datetime

# Function to handle client requests
def handle_client(client_socket):
    try:
        request = client_socket.recv(1024).decode('utf-8')
        print(f"Received Request:\n{request}")

        if not request:
            return

        # Parse the request line (first line)
        request_line = request.splitlines()[0]
        method, path, version = request_line.split()

        # Remove leading / from the path
        if path == "/":
            path = "/test.html"
        path = path.lstrip("/")

        # Check if file exists and send appropriate status code
        if method == "GET":
            if os.path.isfile(path):
                # Handle 304 Not Modified (using a fixed If-Modified-Since date for demo)
                if "If-Modified-Since" in request:
                    # This is a fixed date for testing; normally, you'd get the file's last modification time
                    last_modified = datetime(2023, 10, 1, 12, 0, 0)
                    if_modified_since = request.split("If-Modified-Since:")[1].strip()
                    client_modified_date = datetime.strptime(if_modified_since, '%a, %d %b %Y %H:%M:%S GMT')
                    
                    if client_modified_date >= last_modified:
                        response = "HTTP/1.1 304 Not Modified\r\n\r\n"
                        client_socket.sendall(response.encode())
                        client_socket.close()
                        return

                # Handle 200 OK
                with open(path, 'r') as file:
                    body = file.read()

                response = "HTTP/1.1 200 OK\r\n"
                response += "Content-Type: text/html\r\n"
                response += "Content-Length: {}\r\n\r\n".format(len(body))
                response += body
                client_socket.sendall(response.encode())

            else:
                # Handle 404 Not Found
                response = "HTTP/1.1 404 Not Found\r\n\r\n"
                client_socket.sendall(response.encode())
        
        else:
            # Handle 501 Not Implemented for methods other than GET
            response = "HTTP/1.1 501 Not Implemented\r\n\r\n"
            client_socket.sendall(response.encode())

    except Exception as e:
        # Handle 400 Bad Request in case of any exception or malformed request
        response = "HTTP/1.1 400 Bad Request\r\n\r\n"
        client_socket.sendall(response.encode())

    client_socket.close()


def start_server(host='localhost', port=8080):
    # Create a TCP socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind the socket to the address and port
    server.bind((host, port))

    # Start listening for incoming connections
    server.listen(5)
    print(f"[*] Listening on {host}:{port}")

    while True:
        # Accept an incoming connection
        client_socket, addr = server.accept()
        print(f"[*] Accepted connection from {addr}")

        # Handle the client in a separate thread
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()


if __name__ == "__main__":
    start_server()
