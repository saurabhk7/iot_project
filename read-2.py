 #!/usr/bin/env python
# -*- coding: utf8 -*-
import requests
import json
import RPi.GPIO as GPIO
import MFRC522
import signal
import time
import threading
from firebase import firebase

continue_reading = True

webhost_db_dumpscript_url = "https://bobtail-chapter.000webhostapp.com/dump.php"
firebase_db_url = 'https://iot-project-c1c1a.firebaseio.com/'
last_read_uid = []
# Capture SIGINT for cleanup when the script is aborted
def end_read(signal,frame):
    global continue_reading
    print "Ctrl+C captured, ending read."
    continue_reading = False
    GPIO.cleanup()
def get_timestamp():
    return 222222222
def init_firebase():
    fire_obj=firebase.FirebaseApplication(firebase_db_url, None)
    return fire_obj
    
def write_to_firebase(fire_obj, path, data):
    fire_obj.patch(path,data)
    print "posted: "+str(data)+"at: "+str(path)
def post_to_webhost(data_to_post):
    r = requests.post(url=webhost_db_dumpscript_url,data=data_to_post)
    response = json.loads(r.text)
    if response['timestamp'] is not None:
        return response['timestamp']
    else:
        st=datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
        return st
     
    #print r['timestamp']
    
# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)

# Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()

# Welcome message
print "Welcome to the MFRC522 data read example"
print "Press Ctrl-C to stop."
counter = 0
firebase_root=init_firebase()
# This loop keeps checking for chips. If one is near it will get the UID and authenticate
while continue_reading:

    
    # Scan for cards    
    (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

    # If a card is found
    if status == MIFAREReader.MI_OK:
        print "Card detected"
        
    # Get the UID of the card
    (status,uid) = MIFAREReader.MFRC522_Anticoll()

    # If we have the UID, continue
    if status == MIFAREReader.MI_OK:

        last_read_uid = uid

        print "UID Contents: ",uid

        # Print UID
        print "Current Card read UID: "+str(uid[0])+","+str(uid[1])+","+str(uid[2])+","+str(uid[3])
        print "Last Card read UID: "+str(last_read_uid[0])+str(last_read_uid[1])+str(last_read_uid[2])+str(last_read_uid[3])

        #if uid[0]==last_read_uid[0] and uid[1]==last_read_uid[1] and uid[2]==last_read_uid[2] and uid[3]==last_read_uid[3] :
            
        # This is the default key for authentication
        key = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]
        
        # Select the scanned tag
        MIFAREReader.MFRC522_SelectTag(uid)

        # Authenticate
        status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, 8, key, uid)

        read_data =[]
        # Check if authenticated
        if status == MIFAREReader.MI_OK:
            print "in read"
	    read_data=MIFAREReader.MFRC522_Read(8)
            #read_timestamp_in=MIFAREReader.MFRC522_Read(9)
            #read_timestamp_out=MIFAREReader.MFRC522_Read(10)
            
	    print "data read: ",read_data
	    print "-------------------------"
	    print "flag_bit: ",read_data[5]

            student_path = '/school/'+str(read_data[0])+'/'+str(read_data[2])+'/'+str(read_data[3])+'/'+str(read_data[4])
            #data = {}
	    if read_data != "error":
               # if __name__ == "__main__" :
		    if read_data[5] == 0:
			print "Going IN"
			read_data[5]=0xFF
                                         
                        MIFAREReader.MFRC522_Write(8, read_data)
                        data = {
                            'bus_id':str(read_data[1]),
                            'student_id':str(str(read_data[0])+str(read_data[2])+str(read_data[3])+str(read_data[4])),
                            'status':'IN'
                            }
                        print data
                        timest = post_to_webhost(data)
                        time_in_data = {"time_in":timest}
                        write_to_firebase(firebase_root, student_path, time_in_data)
                        #t1=threading.Thread(target=MIFAREReader.MFRC522_Write,args = (8,read_data))
                        #t2=threading.Thread(target=write_to_firebase, args = (firebase_root, student_path, time_in_data))
                        #t1.start()
                        #t2.start()
		    else:
			print "Going OUT"
                        read_data[5]=0x00
                        
                        MIFAREReader.MFRC522_Write(8, read_data)
                        data = {
                            'bus_id':str(read_data[1]),
                            'student_id':str(str(read_data[0])+str(read_data[2])+str(read_data[3])+str(read_data[4])),
                            'status':'OUT'
                            }
                        print data
                        timest = post_to_webhost(data)
                        time_out_data = {"time_out":timest}
                        write_to_firebase(firebase_root, student_path, time_out_data)
                        #t1=threading.Thread(target=MIFAREReader.MFRC522_Write,args = (8,read_data,))
                        #t2=threading.Thread(target=write_to_firebase, args = (firebase_root, student_path, time_out_data, ))
                        #t1.start()
                        #t2.start()

            MIFAREReader.MFRC522_StopCrypto1()
            time.sleep(3)
       	    print "-----------DONE---------------"
        else:
            print "Authentication error"

