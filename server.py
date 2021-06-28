import socket
import os
import sys
                                                               
port = int(sys.argv[1])                                                          #Taking port number as an argument through command line
srv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)                     #Server startup
print("IP Address = 0.0.0.0, port number = " + str(port))                        #Printing the IP and Port 
print("Route to current directory: " + os.getcwd())                              #Printing directory path
srv_sock.bind(("0.0.0.0", port))                                                 #Binding the port with the hostname
print("Successfully bound to port. Awaiting client connection")                  #Appropriate message to indicate the progress
successful = False                                                               #Initialising a boolean variable to check if the processes were carried out successfully


def uploadFile():                                                                #Function for when client needs to upload a file
    global successful                                                            #Changing variable scope to highlight the changes outside of the function
    b = False                                                                    #Initializing a variable to be used later to trigger a if-else ladder
    disallowedCharacters = ['\\','/',':','*','"','<','>','|']                    #List containing disallowed characters
    fileNameValidityEncoded = cli_sock.recv(50)                                  #Receiving file name validity status of type bytes
    fileNameValidity = fileNameValidityEncoded.decode()                          #Decoding the bytes type object to string
    if(fileNameValidity == "Filename too long"):                                 #If file name was too long
        print(fileNameValidity)                                                  #Appropriate message to indicate error
    else:                                                                    
        dataReceivedConfirmation = str.encode("NEXT")                            #Encoding a message to be sent to the client
        cli_sock.sendall(dataReceivedConfirmation)                               #Sending the bytes object to client to let the client know the progress
        fileNameEncoded = cli_sock.recv(100)                                     #Receiving a valid file name as a bytes object
        fileName = fileNameEncoded.decode()                                      #Decoding the bytes type object to string
        for c in disallowedCharacters:                                           #Checking if the file name contains disallowed characters by iterating through list
            if c in fileName:                                                    #If the filename contains a disallowed characters
                serverErrorStatus = "File name contains disallowed character"    #Appropriate message to indicate error
                b = True                                                         #Changing the value of the initialized boolean variable to stop the process
        if not b:                                                                #If the boolean value is unchanged
            if(os.path.exists(fileName)):                                        #If the file of the given name already exists
                serverErrorStatus = "File already exists, overwriting is forbidden"  #Appropriate message to indicate error
            else:                                                                
                serverErrorStatus = "No errors detected, writing file"           #Appropriate message to indicate the progress
        print(serverErrorStatus)                                                 #Printing the message
        serverErrorEncoded = str.encode(serverErrorStatus)                       #Encoding the message
        cli_sock.sendall(serverErrorEncoded)                                     #Letting the client know the error/progress by sending the encoded message
        if(serverErrorStatus == "No errors detected, writing file"):             #If no errors were detected
            clientErrorEncoded = cli_sock.recv(100)                              #Recieving client's error/progress as bytes type object
            clientErrorStatus = clientErrorEncoded.decode()                      #Decoding the received message
            print(clientErrorStatus)                                             #Printing the message
            if(clientErrorStatus == "No client errors detected, initiating file transfer"): #If no errors on client side
                file = open(fileName, "w")                                       #Creating a file in server directory with received file name
                exitcommand = False                                              #Initializing a variable to start a while loop
                while(not exitcommand):                                          #While the initialized variable remains unchanged                                   
                    try:                                                         #try block to carry out the process
                        cli_sock.sendall(dataReceivedConfirmation)               #Letting the client know that data is being received by sending encoded message
                        lineSizeEncoded = cli_sock.recv(50)                      #Receiving the line size as bytes type object
                        lineSize = lineSizeEncoded.decode()                      #Decoding the line size
                        lineSize = int(lineSize)                                 #String to int
                        cli_sock.sendall(dataReceivedConfirmation)               #Letting the client know that data is still being received
                        lineToWriteEncoded = cli_sock.recv(lineSize+20)          #Receiving the bytes type object with given size and some margin of error,
                                                                                 #so no line is ever too big
                        lineToWrite = lineToWriteEncoded.decode()                #Decoding the received data
                        file.write(lineToWrite)                                  #Writing the received data to the file
                    except:                                                      #If any unknown error detected or end of file reached
                        exitcommand = True                                       #Changing the value of variable to stop the loop
                file.close()                                                     #Closing the file opened for writing
                successful = True                                                #Changing the value of variable successful to indicate the the process was carried out successfully

def downloadFile():                                                              #Function for when the client wishes to download a file
    global successful                                                            #Changing variable scope to highlight the changes outside of the function
    clientErrorEncoded = cli_sock.recv(50)                                       #Receiving the client error status as bytes type object
    clientErrorStatus = clientErrorEncoded.decode()                              #Decoding the status message
    print(clientErrorStatus)                                                     #Printing the message
    if(clientErrorStatus == "No client errors detected"):                        #If client did not run into any errors
        defaultResponse = "NEXT"                                                 #Initializing a variable to carry out different stages of the processes
        defaultResponseEncoded = str.encode(defaultResponse)                     #Encoding the message to be sent to the client
        cli_sock.sendall(defaultResponseEncoded)                                 #Sending the encoded message to let the client know the progress
        fileNameEncoded = cli_sock.recv(100)                                     #Receiving the encoded file name to be downloaded by the client
        fileName = fileNameEncoded.decode()                                      #Decoding the file name 
        if(not os.path.exists(fileName)):                                        #If no such file exists
            serverErrorStatus = "No such file exists."                           #Appropriate error message
            print(serverErrorStatus)                                             #Printing the message
            serverErrorEncoded = str.encode(serverErrorStatus)                   #Encoding the message
            cli_sock.sendall(serverErrorEncoded)                                 #Sending the encoded message to let the client know the error
        else:
            serverErrorStatus = "File found, initiating transfer"                #Appropriate progress message
            print(serverErrorStatus)                                             #Printing the message
            serverErrorEncoded = str.encode(serverErrorStatus)                   #Encoding the message
            cli_sock.sendall(serverErrorEncoded)                                 #Sending the encoded message to let the client know the progress
            file = open(fileName, "r")                                           #Opening the required file to be read
            for line in file:                                                    #Reading file line by line
                cli_sock.recv(50)                                                #Receiving the confirmation that data can be sent                                              
                lineToSendEncoded = str.encode(line)                             #Encoding the line
                lineSize = sys.getsizeof(lineToSendEncoded)                      #Getting the size of the encoded line
                lineSizeEncoded = str.encode(str(lineSize))                      #Encoding the line size after converting int to string
                cli_sock.sendall(lineSizeEncoded)                                #Sending the encoded line size to let the client know what to expect
                cli_sock.recv(50)                                                #Receiving confirmation that data can be sent
                cli_sock.sendall(lineToSendEncoded)                              #Sending the encoded line
            file.close()                                                         #Closing the file after reaching the end
            successful = True                                                    #Changing the value of variable successful to indicate the the process was carried out successfully
    cli_sock.close()                                                             #Closing the connection

def displayFiles():                                                              #Function to display the contents of directory where server file is stored
    global successful                                                            #Changing variable scope to highlight the changes outside of the function
    fileList = os.listdir()                                                      #Storing the contents as a list (given by a function of os library)
    fileListString = ','.join(fileList)                                          #Converting the list to string
    fileListEncoded = str.encode(fileListString)                                 #Encoding the string containing information about directory contents
    cli_sock.send(fileListEncoded)                                               #Sending the encoded information
    successful = True                                                            #Changing the value of variable successful to indicate the the process was carried out successfully

try:
    while True:                                                                  #To keep the server running endlessly and keep processing client requests/connections
        srv_sock.listen(100)                                                     #Looking for connection requests
        cli_sock, cli_addr = srv_sock.accept()                                   #Accepting incoming connections
        print("Successfully bound to client with IP and port: "+str(cli_addr))   #Printing client information on command line
        request = cli_sock.recv(50)                                              #Receiving the desired process that user wants to carry out as a bytes object
        request = request.decode()                                               #Decoding the bytes type object
        print(request+" command received")                                       #Printing the type of process request received

        if request == "put":                                                     #If the client wants to upload a file
            toSend = str.encode("put command received.")                         #Encoding the type of process request received
            cli_sock.sendall(toSend)                                             #Sending that the encoded request that the server has received
            uploadFile()                                                         #Calling the corresponding function
        elif request == "get":                                                   #If the client wants to download a file
            toSend = str.encode("get command received.")                         #Encoding the type of process request received
            cli_sock.sendall(toSend)                                             #Sending that the encoded request that the server has received
            downloadFile()                                                       #Calling the corresponding function
        elif request == "list":                                                  #If the client wants to know the contents of the directory
            toSend = str.encode("list command received.")                        #Encoding the type of process request received
            cli_sock.sendall(toSend)                                             #Sending that the encoded request that the server has received
            displayFiles()                                                       #Calling the corresponding function
        if successful:                                                           #If the variable successful gets changed to true
            print(request+" successful")                                         #Printing that the request was processed successfully
            successful = False                                                   #Changing the variable back to its original value to prepare for the next request/connection
        else:
            print(request+" unsuccessful")                                       #Printing that the request could not be processed unsuccessfully
        cli_sock.close()                                                         #Closing the connection after processing the request

except:                                                                          #If any unknown errors were detected
    print("An error occured which forced the server to close")                   #Printing appropriate error message
            
