import socket

client=socket.socket()
client.connect(("localhost",12345))
print("Connected to the server on port 12345...")

while True:
    message=input("You: ")
    client.send(message.encode())
    if message.lower == "exit":
        print("Client has left the chat")
        break

    response = client.recv(1024).decode()
    if response.lower() == "exit0":
        print("Server has left the chat.")
        break
    print(f"Server: {response}")

client.close()