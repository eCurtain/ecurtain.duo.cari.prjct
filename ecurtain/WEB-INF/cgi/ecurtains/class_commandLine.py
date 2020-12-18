'''
Created on 20-Nov-2020

@author: carip
'''
session = open('release01 cmd/conf1.conf', 'r')
print("session : "+session.read())
logname = "logs.logs"
log = open(logname, 'w')
import os 
import datetime
current_time = datetime.datetime.today()

cd = os.getcwd()
log.write("==================================================\n")
log.write(cd + " NEW START OF SCRIPT\n")
log.write("THE SCRIPT IS RUNNING IN PATH " + cd + "\n")
log.write(cd + " add cd varibles as this directory\n")
log.write(cd  +" imported OS, DATETIME\n")
log.write(cd + " will import TIME, REQUESTS, CTYPES\n")
import time
time.time()
timestamp1 = time.time()
try:
    import requests
    import os
    import ctypes
    current_directory = os.getcwd()
    #Just ignore this error
    # it will work just fine
    ctypes.windll.kernel32.SetConsoleTitleW(current_directory + "\class_commandLine.py")
    log.write(cd + "ctypes.windll.kernel32.setConsoleTitleW(current_directory + '\class_commandLine.py') line set the console title \n")
except Exception as e:
    print("ERROR")
    print(e)
    try:
        err = str(e)
    except Exception as e:
        print(e)
timestamp2 = time.time()
print ("This took %.2f seconds" % (timestamp2 - timestamp1))
class commandLine ():
    print("COMMAND_LINE CLASS ENTERED TO _MAIN_")
    print(session.read())
    while True:
        line = input("ENTER COMMAND>>>")
        log.write(cd + " user write a invalid command wich is "+line+"\n")
        if line == "wget":
            log.write(cd + "request = wget\n")
            print("PLEASE ENTER A VALID URL TO DOWNLOAD")
            url_typeLine = input("valid url>>>")
            file_type = input("type_.not included>>>")
            log.write(cd + "user write the url\n")
            try:
                timestamp1 = time.time()
                requests.get(url_typeLine)
                wget = open("wget_download."+file_type, 'wb')
                #error
                timestamp2 = time.time()
                print ("This took %.2f seconds" % (timestamp2 - timestamp1))
            except Exception as e:
                print(e)
                log.write(cd + "User write a invalid url wich is "+url_typeLine + "\n")
            else:
                print("FINISH downlaoded the url:" + url_typeLine)
                log.write(cd + "User downloaded the file of the url wich is "+ url_typeLine + "\n")
        elif line == "ret":
            print("make sure the file is renamed as class_commandLine.py")
            log.write(cd + " MAKE SURE... MESSAGE PRINTED\n")
            print("RESTARTING... RELAODING SCRIPT...")
            log.write(cd + " the user want to restart the script\n")
            try:
                os.startfile("release01.py")
            except Exception as e:
                log.write(cd + "EXCEPTED ERROR : Make sure the file is renamed as class_commandLine.py\n")
            log.write(cd + " os.startfile('class_comandLine.py') is running if there is no error\n")
            log.close()
            exit(0)
        elif line == "read_entire script":
            f = open("class_commandLine.py", 'r')
            print(f.read())
            log.write(cd + " reading script...\n")
            log.write(cd + f.read()+"\n")
        elif line == "read_entire other":
            fscr = input("enter src>>>")
            log.write(cd + " user want to read other thing\n")
            try:
                text_str = open(fscr, 'rb')
                text_b = ' '.join(format(ord(x), 'b') for x in str(text_str))
                print(text_b)
            except Exception as e:
                print(e)
        elif line == "read_entire script_custom":
            print("write a input or a directory")
            log.write(cd  +" user want to read other thing\n")
            direct_url_read_entire_script_custom = input(">>>")
            timestamp1 = time.time()
            filename = direct_url_read_entire_script_custom
            direct_url_opening_custom_file = open(filename, 'r')
            print(direct_url_opening_custom_file.read())
            timestamp2 = time.time()
            print ("This took %.2f seconds" % (timestamp2 - timestamp1))
        elif line == "exit":
            print("EXITING WRITING LOG")
            filename = "exit.logs"
            elog = open(filename, 'w')
            elog.write(current_directory+"\class_commandLine.py exiting \n")
            elog.write(current_directory + "\class_commandLine.py exit  ")
            elog.close()
            log.write(cd + " User try to exit\n")
            log.write(cd + " Exit sucessfully complete\n")
            log.write(cd + " Exit")
            log.close()
            exit(1)
        elif line == "change title":
            change_title = input("new title>>>")
            #same things, ignore this error
            ctypes.windll.kernel32.SetConsoleTitleW(change_title)
            log.write(cd + " title changed to "+change_title+"\n")
        elif line == "change title _back":
            ctypes.windll.kernel32.SetConsoleTitleW(cd + "\class_commandLine.py")
        elif line == "text-editor":
            line_limit = input("Line-Limit>>>")
            name_txt = input("File_name>>>")
            filename = name_txt
            file = open(filename, 'w')
            for x in range(int(line_limit)):
                line_txt = input("")
                log.write(cd + " IN text-editor USER WRITE "+line_txt+"\n")
                file.write(line_txt + "\n")
                log.write(cd + " IN text-editor TEXT-EDITOR write the text in the file \n")
            file.close()
            log.write(cd + " IN text-editor TEXT-EDITOR save the file \n")
        elif line == "loader-text":
            try:
                file_name = input("File_name>>>")
                log.write(cd + "IN loader-text USER WRITE the file name"+file_name+" to READ \n")
                format = input("read_format>>>")
                try:
                    file = open(file_name, format)
                    print(file.read())
                except Exception as e:
                    print(e)
            except Exception as e:
                print(e)
                log.write(cd + "IN loader-text LOADER-TEXT has occured A ERROR\n")
            file.close()
        elif line == "deleter":
            delete_path = input(">>>")
            try:
                os.remove(delete_path)
                print("SUCESSFULLY DELETED "+delete_path)
                log.write(cd + " IN deleter DELETER WANT TO PRINT A MESSAGE : SUCESSFULLY DELETED "+delete_path+"\n")
            except Exception as e:
                print(e)
                log.write(cd + " IN deleter DELETER has occured A ERROR\n")
        elif line == "ret _ rl":
            os.startfile('release01.py')
            exit(0)        
        else:
            if line == " ", "":
                print("text please")
                log.write(cd + " user did not write nothing\n")
        