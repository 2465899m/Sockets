                                                                     #Comments
import socket
import os
import sys

port = int(sys.argv[2])                                                     #Taking the port number as argument from command line
ipaddr = sys.argv[1]                                                        #Taking the ip address as argument from command line
command = sys.argv[3]                                                       #Taking the type of request as argument from command line
cli_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)                #Defining cli_sock
try:                                                                        #Runs if no error found
    cli_sock.connect((ipaddr, port))                                        #Establishing a connection to the server
except:                                                                     #Runs if error found
    print ("Error: Host not active")                                               #Printing appropriate error message
successful = False                                                          #Initialising a boolean variable to check if the processes were carried out successfully
print("Server IP Address = "+ipaddr+", Server port number = " + str(port))  #Printing the server details on command line

def uploadFile():                                                           #Function to upload a file
    global successful                                                       #Changing variable scope to highlight the changes outside of the function
    fileName = sys.argv[4]                                                  #Taking the file name as argument from command line
    fileNameEncoded = str.encode(fileName)                                  #Encoding the file name
    if(sys.getsizeof(fileNameEncoded)>100):                                 #If file name is too long
        longFileSize = "Filename too long"                                  #Appropriate error message
        print(longFileSize)                                                 #Printing the message
    else:
        longFileSize = "Filename is valid"                                  #Message if no error occured
    longFileSizeEncoded = str.encode(longFileSize)                          #Encoding the message
    cli_sock.sendall(longFileSizeEncoded)                                   #Sending the message to the server
    if (longFileSize == "Filename is valid"):                               #If server thinks the filename is valid
        cli_sock.recv(50)                                                   #Receiving confirmation taht data can be sent
        cli_sock.sendall(fileNameEncoded)                                   #Sending the encoded file name
        serverErrorEncoded = cli_sock.recv(50)                              #Receiving server error status as bytes type object
        serverErrorStatus = serverErrorEncoded.decode()                     #Decoding the message
        print(serverErrorStatus)                                            #Printing the message
        if(serverErrorStatus == "No errors detected, writing file"):        #If no errors were detected on the server side
            #most error checking done server side for this command
            if(not os.path.exists(fileName)):                               #If no such file of the given name exists on the client side
                #checks if the file to be transferred actually exists
                clientErrorStatus = "No such file exists."                  #Appropriate error message
            else:
                clientErrorStatus = "No client errors detected, initiating file transfer" #Appropriate progress message
            print(clientErrorStatus)                                        #Printing the message
            clientErrorEncoded = str.encode(clientErrorStatus)              #Encoding client error status
            cli_sock.sendall(clientErrorEncoded)                            #Sending the client error status
            if(clientErrorStatus == "No client errors detected, initiating file transfer"):    #If no errors detected on client side
                file = open(fileName, "r")                                  #Opening the file for reading
                for line in file:                                           #Reading the file line by line
                    cli_sock.recv(50)                                       #Receiving confirmation that data can be sent
                    lineToSendEncoded = str.encode(line)                    #Encoding the line
                    lineSize = sys.getsizeof(lineToSendEncoded)             #Checking the size of the line
                    lineSizeEncoded = str.encode(str(lineSize))             #Encoding the line size
                    cli_sock.sendall(lineSizeEncoded)                       #Sending the line size to let the server know what to expect
                    cli_sock.recv(50)                                       #Receiving confirmation that data can be sent
                    cli_sock.sendall(lineToSendEncoded)                     #Sending the encoded line
                file.close()                                                #Closing the file after reaching the end
                successful = True                                           #Changing the value of variable successful to indicate the the process was carried out successfully
    cli_sock.close()                                                        #Closing the connection

def downloadFile():                                                         #Function to dowload a file
    b = False                                                               #Initializing a variable which is used to trigger a if-else ladder below
    global successful                                                       #Changing variable scope to highlight the changes outside of the function
    disallowedCharacters = ['\\','/',':','*','"','<','>','|']               #List containing disallowed characters
    fileName = sys.argv[4]                                                  #Taking the file name as argument from command line
    fileNameEncoded = str.encode(fileName)                                  #Encoding the file name
    for c in disallowedCharacters:                                          #Iterating through the list of disallowed characters
        if c in fileName:                                                   #If the file name contains a character in the list
            clientErrorStatus = "File name contains disallowed character"   #Appropriate error message
            b = True                                                        #Changing the value of the initialized variable to stop the process
    if not b:                                                               #If file does not contain disallowed character
        if(os.path.exists(fileName)):                                       #If file of given name already exists
            clientErrorStatus = "File already exists, overwriting is forbidden" #Appropriate error message
        elif(sys.getsizeof(fileNameEncoded)>100):                           #If filename is too long
            clientErrorStatus = "Filename too long"                         #Appropriate error message
        else:        
            clientErrorStatus = "No client errors detected"                 #Appropriate progress message
    print(clientErrorStatus)                                                #Printing the message
    clientErrorEncoded = str.encode(clientErrorStatus)                      #Encoding client error status
    cli_sock.sendall(clientErrorEncoded)                                    #Sending encoded client error status
    if(clientErrorStatus == "No client errors detected"):                   #If no errors detected on client side
        cli_sock.recv(50)                                                   #Receiving confirmation that process can continue
        cli_sock.sendall(fileNameEncoded)                                   #Sending the encoded file name
        serverErrorEncoded = cli_sock.recv(50)                              #Receiving a bytes type object containing server error status
        serverErrorStatus = serverErrorEncoded.decode()                     #Decoding the bytes type object containing server error status
        print(serverErrorStatus)                                            #Printing the message containing server error status
        if(not serverErrorStatus == "No such file exists."):                #If a file of the given name does not exist
            file = open(fileName, "w")                                      #Opening the file for writing
            exitcommand = True                                              #Initializing a variable to be used in the while loop below
            while(exitcommand):                                             #while the value of variable remains unchanged
                try:                                                        #try block to carry out the process
                    dataReceivedConfirmation = str.encode("NEXT")           #Encoding the message to tell the server to go to the next stage of the process
                    cli_sock.sendall(dataReceivedConfirmation)              #Letting the server know that data is being received by sending encoded message
                    lineSizeEncoded = cli_sock.recv(50)                     #Receiving the line size as bytes type object
                    lineSize = lineSizeEncoded.decode()                     #Decoding the line size
                    lineSize = int(lineSize)                                #String to int
                    cli_sock.sendall(dataReceivedConfirmation)              #Letting the server know that data is still being received
                    lineToWriteEncoded = cli_sock.recv(lineSize+20)         #Receiving the bytes type object with given size and some margin of error,
                                                                            #so no line is ever too big
                    lineToWrite = lineToWriteEncoded.decode()               #Decoding the received data
                    file.write(lineToWrite)                                 #Writing the received data to the file
                except:                                                     #If any unknown error detected or end of file reached
                    exitcommand = False                                     #Changing the value of variable to stop the loop
            file.close()                                                    #Closing the file
            successful = True                                               #Changing the value of variable successful to indicate the the process was carried out successfully

def displayFiles():                                                         #Function to display the contents of the directory of the server
    global successful                                                       #Changing variable scope to highlight the changes outside of the function                    
    fileListEncoded = cli_sock.recv(100)                                    #Receiving the file list as a bytes type object
    fileList = fileListEncoded.decode()                                     #Decoding the file list which was received as a bytes type object
    print (fileList)                                                        #Printing the file list
    successful = True                                                       #Changing the value of variable successful to indicate the the process was carried out successfully

try:
    commandEncoded = str.encode(command)                                    #Encoding the request received from the command line
    cli_sock.sendall(commandEncoded)                                        #Sending the encoded request to the server
    reply = cli_sock.recv(50)                                               #Receiving the request that has been received by the server as a bytes type object
    print(reply.decode())                                                   #Printing the request received by the server after decoding it
    if command == "put":                                                    #If the client wants to upload a file
        uploadFile()                                                        #Calling the corresponding function
    elif command == "get":                                                  #If the client wants to download a file
        downloadFile()                                                      #Calling the corresponding function
    elif command == "list":                                                 #If the client wants to knwo the contents of the directory
        displayFiles()                                                      #Calling the corresponding function
    if successful:                                                          #If the variable successful gets changed to true
        print(command+" successful")                                        #Printing that the request was processed successfully
    else:
        print(command+" unsuccessful")                                      #Printing that the request could not be processed unsuccessfully
    cli_sock.close()                                                        #Closing the connection after processing the request
        
except:                                                                     #If any unknown errors were detected
    print("An unexpected error occurred")                                   #Printing appropriate error message                                      
