# Ex 4.4 - HTTP Server Shell
# Author: Orit Shiff
# Purpose: Provide a basis for Ex. 4.4
# Note: The code is written in a simple way, without classes, log files or other utilities, for educational purpose
# Usage: Fill the missing functions and constants

# TO DO: import modules
import os
import socket

# TO DO: set constants
IP = "0.0.0.0"
PORT = 80
SOCKET_TIMEOUT = 0.5
REDIRECTION_DICTIONARY = {"old_page": "abstract.jpg"} # Programmer should pick the old and new resources
FIXED_RESPONSE = "HTTP/1.1 200 OK\r\nContent-Length: 5\r\nContent-Type: text/html; charset=ISO-8859-1\r\n\r\nhello"


def get_file_data(filename):
    # try:
    #   if "webroot" not in filename:
    #     filename = f'webroot/{filename}'
    #   with open(filename, "rb") as f:
    #       return f.read()
    # except FileNotFoundError:
    #     print(f"Error: File not found: {filename}")
    #     return None
  if "webroot" not in filename:
    # Search recursively from the start_dir
    filename = find_file(filename, start_dir=os.getcwd())
  
  try:
    with open(filename, "rb") as f:
      return f.read()
  except FileNotFoundError:
    print(f"Error: File not found: {filename}")
    return None

# Function to search for file recursively
def find_file(filename, start_dir):
  name = filename.split("/")[-1]
  for root, dirs, files in os.walk(start_dir):
    for file in files:
      if file == name:
        return os.path.join(root, file)
  return filename


def handle_client_request(resource, socket):
    # Check for redirection in REDIRECTION_DICTIONARY
  path, query_string = resource.split("?") if "?" in resource else (resource, "")
    
  if path.split("/webroot")[-1] in ["/calculate-next", "/calculate-area"]:
    if "/calculate-next" in path:
        try:
            params = dict(item.split("=") for item in query_string.split("&"))
            num = int(params.get("num", 0))
            result = num + 1
            response_body = f"The next number is: {result}"
        except ValueError:
            response_body = "Error: Invalid input."
    else:  # "/calculate-area":
        try:
            params = dict(item.split("=") for item in query_string.split("&"))
            height = int(params["height"])
            width = int(params["width"])
            result = height * width * 0.5
            response_body = f"The area is: {result}"
        except ValueError:
            response_body = "Error: Invalid input ."

    header = f"HTTP/1.1 200 OK\r\nContent-Length: {len(response_body)}\r\nContent-Type: text/plain\r\n\r\n"
    socket.sendall(header.encode() + response_body.encode())

  else:  # asks a file
      if "?" in resource:
        filename = resource.split("?")[1].split("=")[1]
      else:
        filename = path.strip("/") or "webroot/index.html"
      
      if filename in REDIRECTION_DICTIONARY:
        new_url = REDIRECTION_DICTIONARY[filename]
        response = f"HTTP/1.1 302 Found\r\nLocation: {new_url}\r\n\r\n"
        socket.sendall(response.encode())
        return
  
      data = get_file_data(filename)

      if not data:
          response = "HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\n\r\n"
          socket.sendall(response.encode())
          return

      if filename.endswith(".html"):
          content_type = "text/html"
      elif filename.endswith(".css"):
          content_type = "text/css"
      elif filename.endswith(".js"):
          content_type = "text/javascript"
      elif filename.endswith(".jpg"):
          content_type = "image/jpeg"
      else:
          content_type = "application/octet-stream"

      header = f"HTTP/1.1 200 OK\r\nContent-Length: {len(data)}\r\nContent-Type: {content_type}\r\n\r\n"
      socket.sendall(header.encode() + data)


def validate_HTTP_request(request):
    """
    Check if request is a valid HTTP request and returns TRUE / FALSE and the requested URL
    """
    try:
        # Check if request line is present and has the correct format (e.g., GET /index.html HTTP/1.1)
        method, resource, protocol = request.split(" ")[:3]
        if method.upper() != "GET" or "HTTP/1.1" not in protocol.upper():
            return False, None
        return True, resource
    except ValueError:
        return False, None


def handle_client(socket):
    """Handles client requests: verifies client's requests are legal HTTP, calls function to handle the requests"""
    print("Client connected")
    while True:
        # TO DO: insert code that receives client request
        try:
            client_request = socket.recv(1024).decode()
        except TimeoutError:
            continue

        valid_http, resource = validate_HTTP_request(client_request)
        if valid_http:
            print("Got HTTP request")
            handle_client_request(resource, socket)
            break
        else:
            print("Error: invalid HTTP request")
            break

    print("Closing connection")
    socket.close()


def main():
    # Open a socket and loop forever while waiting for clients
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((IP, PORT))
    server_socket.listen()
    print("Listening for connections on port {}".format(PORT))

    while True:
        client_socket, client_address = server_socket.accept()
        print("New connection received")
        client_socket.settimeout(SOCKET_TIMEOUT)
        handle_client(client_socket)

    server_socket.close()


if __name__ == "__main__":
    # Call the main handler function
    main()