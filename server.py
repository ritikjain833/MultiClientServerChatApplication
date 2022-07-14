import socket
import threading
map = dict()
max_length = 1024
PORT = 8080
SERVER = "localhost"                
ADDR = (SERVER, PORT)
HEADER = 128
def send(msg, client):
    client.send(msg.encode())
def print_Error():
    err=[]
    err.append("ERROR 100 Malformed username\n\n")    
    err.append("ERROR 101 No user registered\n\n")
    err.append("ERROR 102 Unable to send\n\n")
    err.append("ERROR 103 Header Incomplete\n\n")
    err.append("ERROR: Invalid message\n")
    return err
def receive(client):
    message = ""
    try:
        temp = client.recv(max_length)
        message=temp.decode()
    except:
        pass
    return message
def outgoing_message(conn, noOfConf, boolRecv):
    toSend = False
    toRecv = False
    username = ""
    connected = True
    while connected==True:
        s = receive(conn)
        aux=s.split(" ")
        if (connected == False):
            if (len(username)==0):
                del map[username]
                boolRecv.pop()
                print("Total active connections are:", len(map))
            break
        if (len(s) == 0):
            continue
        if (aux[0] == "REGISTER"):
            if (aux[1] == "TOSEND"):
                if (toSend == False):
                    temp=s[16:].split("\n")
                    if temp[1]!="" or temp[2]!="":    
                        send(print_Error()[0], conn)
                    else:
                        username = temp[0]
                        if (username.isalnum() == False or username in map):
                            send(print_Error()[0], conn)
                        else:
                            toSend = True
                            send("REGISTERED TOSEND " + username + "\n\n", conn)
                else:
                    send(print_Error()[4], conn)
            elif (aux[1] == "TORECV"):
                if (toRecv == False):
                    temp=s[16:].split("\n")
                    if temp[1]!="" or temp[2]!="":    
                        send(print_Error()[0], conn)
                    else:
                        username = temp[0]
                        if (username.isalnum() == False or username in map):
                            send(print_Error()[0], conn)
                        else:
                            toRecv = True
                            map[username] = [conn, None]
                            send("REGISTERED TORECV " + username + "\n\n", conn)
                            print(" Total active connections are:", len(map.keys()))

                else:
                    send(print_Error()[4], conn)
            else:
                send(print_Error()[4], conn)
        elif (aux[0] == "SEND"):
            if (toSend==True):
                i = 5
                while(s[i] != '\n'):
                    i += 1
                k=i
                remain=(s[k:])  
                aux=s.split()
                receiver = aux[1]
                c=aux[2]
                if (c != "Content-length:"):
                    send(print_Error()[3], conn)
                    connected = False
                    if (len(username)==0):
                        del map[username]
                        boolRecv.pop()
                        print("Total active connections are:", len(map))
                    break
                else:
                    contentLength=int(aux[3])
                    msg = " ".join(aux[4:])
                    if (contentLength != len(msg)):
                        send(print_Error()[3], conn)
                        connected = False
                        if (len(username)==0):
                            del map[username]
                            boolRecv.pop()
                            print(" Total active connections are:", len(map))
                        break
                    else:
                        if receiver in map:
                            send("FORWARD " + username +remain, map.get(receiver)[0])
                            map.get(receiver)[1] = map.get(username)[0]
                        elif receiver == "ALL":
                            noOfConf= 1
                            for aux in boolRecv:
                                aux=False
                            boolRecv[0]=True    
                            for r in map:
                                if (r == username):
                                    continue
                                send("FORWARD " + username +remain, map.get(r)[0])
                                map.get(r)[1] = map.get(username)[0]
                        else:
                            send(print_Error()[2], conn)
            else:
                send(print_Error()[1], conn)
        elif (aux[0] == "RECEIVED"):
            if (toSend==True):
                if (noOfConf < len(boolRecv)):
                    boolRecv[noOfConf] = True
                    noOfConf+= 1
                    if (noOfConf == len(boolRecv)):
                        noOfConf = 1000
                        z = True
                        for x in boolRecv:
                            if x==False:
                                z=False
                                break
                        if (z==True):
                            send("SENT ALL\n", map.get(username)[1])
                        else:
                            send(print_Error()[2],map.get(username)[1])

                else:
                    send("SENT " + username + "\n", map.get(username)[1])
            else:
                send(print_Error()[1], conn)
        elif (aux[0] == "ERROR 103"):
            if (noOfConf< len(boolRecv)):
                boolRecv[noOfConf] = False
                noOfConf += 1
                if (noOfConf == len(boolRecv)):
                    noOfConf = 1000
                    if (z):
                        send(print_Error()[2], map.get(username)[1])
            else:
                send(s, map.get(username)[1])

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.bind(ADDR)
    server.listen()
    print("server is Listening on port number: {}".format(PORT) )
    noOfConf = 1000
    boolRecv = []

    while True:
        boolRecv.append(False)
        conn, addr = server.accept()
        thread = threading.Thread(target=outgoing_message, args=(conn,noOfConf, boolRecv))
        thread.start()






