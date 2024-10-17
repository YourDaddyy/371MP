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

        request_line = request.splitlines()[0]
        method, path, _ = request_line.split()

        if path == "/":
            path = "test.html"
        else:
            path = path.lstrip("/")

        if method == "GET":
            if os.path.isfile(path):
                # Get the last modified time of the file dynamically
                last_modified_timestamp = os.path.getmtime(path)
                last_modified = datetime.utcfromtimestamp(last_modified_timestamp)
                last_modified_str = last_modified.strftime('%a, %d %b %Y %H:%M:%S GMT')

                # Check for If-Modified-Since header
                if "If-Modified-Since" in request:
                    if_modified_since = request.split("If-Modified-Since:")[1].strip()
                    client_modified_date = datetime.strptime(if_modified_since, '%a, %d %b %Y %H:%M:%S GMT')

                    # Compare the last modified time with the client's modified date
                    if client_modified_date >= last_modified:
                        response = "HTTP/1.1 304 Not Modified\r\n\r\n"
                        client_socket.sendall(response.encode())
                        client_socket.close()
                        return

                with open(path, 'r') as file:
                    body = file.read()

                response = f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nLast-Modified: {last_modified_str}\r\nContent-Length: {len(body)}\r\n\r\n{body}"
                client_socket.sendall(response.encode())
            else:
                response = "HTTP/1.1 404 Not Found\r\n\r\n"
                client_socket.sendall(response.encode())
        else:
            response = "HTTP/1.1 501 Not Implemented\r\n\r\n"
            client_socket.sendall(response.encode())

    except Exception:
        response = "HTTP/1.1 400 Bad Request\r\n\r\n"
        client_socket.sendall(response.encode())

    client_socket.close()

def start_server(host='localhost', port=8080):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(5)
    print(f"[*] Listening on {host}:{port}")

    while True:
        client_socket, addr = server.accept()
        print(f"[*] Accepted connection from {addr}")
        threading.Thread(target=handle_client, args=(client_socket,)).start()

if __name__ == "__main__":
    start_server()
