import socket


HEADER = 64
PORT = 7071
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!dc"
SERVER = "172.17.0.1"
ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR) #Connecting to server



def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length)) #Filling message until HEADER many bytes is in the message
    client.send(send_length)
    client.send(message)
    print(client.recv(2048).decode(FORMAT)) #Receiving message from server



while True:
    data = input("Put your message here:")
    send(data)
    if data == DISCONNECT_MESSAGE:
        break

