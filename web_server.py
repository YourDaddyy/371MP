import socket
import threading
import os
from datetime import datetime
import multiprocessing


# Function to handle client requests
def handle_client(client_socket,is_chunk=False):
    try:
        request = client_socket.recv(1024).decode('utf-8')
        print(f"Received Request:\n{request}")

        if not request:
            return

        request_line = request.splitlines()[0]
        method, path, _ = request_line.split()
        
        if request_line.startswith("GET"):
            if path.startswith("http://"):
                path = path[len("http://"):]
            elif path.startswith("https://"):
                path = path[len("https://"):]
            if "/" in path:
                path = path[path.index("/"):]
            else:
                path = "/"

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
                if is_chunk == True:
                    response_headers = (
                    f"HTTP/1.1 200 OK\r\n"
                    f"Content-Type: text/html\r\n"
                    f"Last-Modified: {last_modified_str}\r\n"
                    f"Content-Length: {len(body)}\r\n"
                    f"Transfer-Encoding: chunked\r\n\r\n"
                    )
                    client_socket.sendall(response_headers.encode())

                    with open(path, 'rb') as file:
                        while chunk := file.read(512):  
                            client_socket.sendall(f"{len(chunk):X}\r\n".encode())
                            print(f"Message is sent chunk size is {len(chunk)}")
                            client_socket.sendall(chunk)
                            client_socket.sendall(b"\r\n")

                    client_socket.sendall(b"0\r\n\r\n")
                    print("\n\n\n")
                else:
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


def handle_proxy_client(client_socket):
    try:
        request = client_socket.recv(1024).decode('utf-8')
        print(f"Received Request from Client:\n{request}")

        lines = request.splitlines()
        if not lines:
            return

        if lines[0].startswith("CONNECT"):
            host_line = [line for line in lines if line.startswith("Host:")][0]
            host = host_line.split(" ")[1]
            target_host, target_port = host.split(":")
            target_port = int(target_port)
            # print(f"Host is {target_host}, Port is {target_port}")

            response = "HTTP/1.1 200 Connection Established\r\n\r\n"
            try:
                client_socket.sendall(response.encode())
            except Exception as e:
                print(f"Error sending response: {e}")

            target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            target_socket.connect((target_host, target_port))

            client_socket.setblocking(False)
            target_socket.setblocking(False)

            while True:
                try:
                    data_from_client = client_socket.recv(4096)
                    if len(data_from_client) == 0:
                        break
                    target_socket.sendall(data_from_client)
                except BlockingIOError:
                    pass
                except ConnectionResetError:
                    print("Client closed the connection")
                    break

                try:
                    data_from_target = target_socket.recv(4096)
                    if len(data_from_target) == 0:
                        break
                    client_socket.sendall(data_from_target)
                except BlockingIOError:
                    pass
                except ConnectionResetError:
                    print("Target server closed the connection")
                    break

            target_socket.close()

        else:
            request_line = lines[0]
            if request_line.startswith("GET"):
                method, full_url, version = request_line.split()

                if full_url.startswith("http://"):
                    full_url = full_url[len("http://"):]
                elif full_url.startswith("https://"):
                    full_url = full_url[len("https://"):]

                if "/" in full_url:
                    path = full_url[full_url.index("/"):]
                else:
                    path = "/"

                new_request_line = f"{method} {path} {version}"
                lines[0] = new_request_line

                request = "\r\n".join(lines) + "\r\n\r\n"
            
            host = None
            for line in lines:
                if line.startswith("Host:"):
                    host = line.split(": ")[1]
                    break

            if not host:
                response = "HTTP/1.1 400 Bad Request\r\n\r\nMissing Host header"
                client_socket.sendall(response.encode())
                client_socket.close()
                return

            target_host, target_port = host.split(":")
            target_port = int(target_port)
            print(f"Host is {target_host}, Port is {target_port}")
            target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            target_socket.connect((target_host, target_port))
            target_socket.sendall(request.encode())

            while True:
                response = target_socket.recv(4096)
                if len(response) == 0:
                    break
                client_socket.sendall(response)

            target_socket.close()

    except Exception as e:
        print(f"Error: {e}")
    finally:
        try:
            client_socket.close()
        except Exception as e:
            print(f"Error closing client socket: {e}")


def start_server(host='localhost', port=8080, is_chunck = False):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(50)
    print(f"[*] Listening on {host}:{port}")

    while True:
        client_socket, addr = server.accept()
        print(f"[*] Accepted connection from {addr}")
        threading.Thread(target=handle_client, args=(client_socket, is_chunck)).start()
        
def start_proxy_server(host='localhost', port=8080):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(50)
    print(f"[*] Listening on {host}:{port}")

    while True:
        client_socket, addr = server.accept()
        print(f"[*] Accepted connection from {addr}")
        threading.Thread(target=handle_proxy_client, args=(client_socket,)).start()

if __name__ == "__main__":
    is_chunck = False
    server_process = multiprocessing.Process(target=start_server, args=('localhost', 8080, is_chunck))
    proxy_process = multiprocessing.Process(target=start_proxy_server, args=('localhost', 8081))
    
    server_process.start()
    proxy_process.start()
    
    server_process.join()
    proxy_process.join()
