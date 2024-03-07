import socket
import threading #creating multiple threads(splitting tasks) for message handling


HEADER = 64
PORT = 7071 #random port used by nothing
SERVER = "172.17.0.1" #(192.168.1.11) socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT) #Address 
FORMAT = 'utf-8' #For decoding to string
DISCONNECT_MESSAGE = "!dc"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #First variable is socket type, Second variable is streaming data over socket
server.bind(ADDR) #Binding socket to the address

saved_msg = []

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")

    connected = True
    while connected:
        msg = conn.recv(1024).decode(FORMAT) #How many bytes we are receiving and decoding
        print(f"[{addr}] {msg}")
        if msg == DISCONNECT_MESSAGE:
            print(f"[CONNECTION TERMINATED] {addr} disconnected.")
            connected = False
            print(saved_msg)
            
            #conn.sendall(saved_msg[-1].encode(FORMAT))
            #conn.sendto = (msg.encode(FORMAT), addr) #Sending message to client


    conn.close()

# If we want to send objects as messages not strings use pickles or send messages json serialized (import pickle)



def start(): #Starting socket server allowing server to listen then passing them to handle_client
    server.listen()
    print(f"[LISTENING] Server is listenin on {SERVER}")
    while True:
        conn, addr = server.accept() #Waiting for new connection to server
        thread = threading.Thread(target=handle_client, args=(conn, addr)) #Passing new connection to handle_client
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")


print("[STARTING] server is starting...")
start()