import socket
import threading
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
max_length = 1024
HEADER = 128
PORT = 8080
SERVER="127.0.0.1"
def send(message):
    client.send(message.encode())
def receive():
    message = ""
    try:
        temp = client.recv(max_length)
        message=temp.decode()
    except:
        pass
    return message

connected = False
flag=False
while True:
    ADDR = (SERVER, PORT)
    try:
        client.connect(ADDR)
        if flag==False:
            break
    except:
        print("Unable to connect to given server's address\n")

print("Successfully connected to the server.\n")

while True:
    username = input("Enter you Username in alphanumeric format: ")
    try:
        if (username != "ALL" and username.isalnum()):
            print("\nRegistering Username...\n")
            send("REGISTER TOSEND {}\n\n".format(username))
            message = receive()
            if (len(message)==0):
                continue
            if (message[0:5] == 'ERROR'):
                print("ERROR 100 occured Failed to register: Malformed Username")
            else:
                send("REGISTER TORECV " + username + "\n\n")
                message = receive()
                if (len(message)==0):
                    continue
                if (message[0:5] == 'ERROR'):
                    print("ERROR 100 occured Failed to register: Malformed Username")
                else:
                    print("Registration successful\n")
                    connected = True
                    break
    except:
        print("\nInvalid Username\n")

def outgoing_message():
    while connected==True:
        s = input()
        if (len(s) == 0):
            continue
        if (s[0] != '@'):
            print(" invalid message format: should start with \'@\' followed by receiver's username and message")
        else:
            n=len(s)  
            aux=s.split()
            for i in range(n):
                if s[i]==" ":
                    break
            receiver=s[1:i+1]
            message=s[i+1:]
            send("SEND " + receiver + "\n" +"Content-length: " + str(len(message)) + "\n\n" + message)
    
def find_sender(s):
    for i in range(8,len(s)):
        if s[i]=="\n":
            break
    return s[8:i] 

def incoming_message():
    while connected==True:
        s = receive()
        if (len(s)==0):
            continue
        error=dict()
        error["ERROR 102"]={"ERROR 102 Unable to send"}
        error["ERROR 100"]={"ERROR 100 No user registered"}
        if (s[0] == 'S'):
            receiver = s[5:]
            print("MESSAGE SENT to " + receiver + '\n')
        elif (s[0:8] in error.keys()):
            aux=error[s[0:8]]
            print(aux)
        elif(s[0:7] == "FORWARD"):
            sender=find_sender(s)
            aux=(s.split())
            if (aux[2]!= "Content-length:"):
                send("ERROR 103: Header Incomplete\n")
                break
            else:
                message = " ".join(aux[4:])
                if (int(aux[3]) != len(message)):
                    send("ERROR 103: Header Incomplete\n\n")
                    if flag==False:
                        break
                else:
                    print("[" + sender + "] " + message)
                    send("RECEIVED " + sender + "\n\\n")
        else:
            print("ERROR 103: Header incomplete\n")
            if flag==False:
                break
    print("Connection lost!!!")

thread1 = threading.Thread(target=outgoing_message)
thread1.start()
thread2 = threading.Thread(target=incoming_message)
thread2.start()
