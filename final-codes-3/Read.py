 #!/usr/bin/env python
# -*- coding: utf8 -*-
import sqlite3 as lite
import requests
import json
import RPi.GPIO as GPIO
import MFRC522
import signal
import time
import datetime
import threading
import RPi.GPIO as GPIO
from Queue import Queue

GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.OUT)
GPIO.output(11, False)
GPIO.setup(13, GPIO.OUT)
GPIO.output(13, False)
GPIO.setup(18, GPIO.OUT)
GPIO.output(18, False)
GPIO.setup(35, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(37, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)


def led_start_seq():

    count = 2
    td = 0.15
    
    GPIO.output(11, True)
    GPIO.output(13, True)
    GPIO.output(18, True)
    time.sleep(td+0.5)
    
    while count!=0:
        GPIO.output(11, True)
        GPIO.output(13, False)
        GPIO.output(18, False)
        time.sleep(td)
        GPIO.output(11, False)
        GPIO.output(13, True)
        GPIO.output(18, False)
        time.sleep(td)
        GPIO.output(11, False)
        GPIO.output(13, False)
        GPIO.output(18, True)
        time.sleep(td)
        GPIO.output(11, False)
        GPIO.output(13, True)
        GPIO.output(18, False)
        time.sleep(td)
        count-=1



led_start_seq()

GPIO.output(11, False)
GPIO.output(18, False)
time.sleep(0.5)
GPIO.output(13, True)

from firebase import firebase

con = lite.connect('local_data.db')

continue_reading = True
 
webhost_db_dumpscript_url = "https://bobtail-chapter.000webhostapp.com/dump.php"
firebase_db_url = 'https://iot-project-c1c1a.firebaseio.com/'
last_read_uid = []
data_queue = Queue()
fire_data_queue = Queue()
busid_str = ''
schoolid_str = ''

webhost_done = True
firebase_done = True

# Capture SIGINT for cleanup when the script is aborted
def end_read(signal,frame):
    global continue_reading
    #global data_thread_event
    GPIO.cleanup()
    print "Ctrl+C captured, ending read."
    continue_reading = False
    
def get_timestamp():
    return 222222222
def init_firebase():
    fire_obj=firebase.FirebaseApplication(firebase_db_url, None)
    return fire_obj
    
def write_to_firebase(fire_obj, path, data):
    fire_obj.patch(path,data)
    print "posted: "+str(data)+"at: "+str(path)
def post_to_webhost(data_to_post):
    st=datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    r = requests.post(url=webhost_db_dumpscript_url,data=data_to_post)
    response = json.loads(r.text)
    if response['timestamp'] is not None:
        return response['timestamp']
    else:
        
        return st
def post_queue_to_webhost(event):
    global webhost_done
    global firebase_done
    global data_queue
    print "Webhost Listening Queue for Data"
    e = threading.Event()
    t = threading.Thread(name='non-block', target=flashLed, args=(18,e, 2))
    t.start()
    while not event.isSet():
        webhost_done = True
        while not data_queue.empty():
            webhost_done = False
            #e = threading.Event()
            #t = threading.Thread(name='non-block', target=flashLed, args=(18,e, 2))
            #t.start()
            top_data = data_queue.get()
            print "Data Arrived: ", str(top_data)
            server_timest = post_to_webhost(top_data)
            print "posted to webhost"
            #if top_data['status']== 'OUT':
            #server_time_data = {"time_out":str(top_data['local_timestamp'])}
            #else:
            #server_time_data = {"time_in":str(top_data['local_timestamp'])}
            #write_to_firebase(firebase_root, student_path, server_time_data)
            data_queue.task_done()
            #e.set()

def post_queue_to_firebase(event):
    global webhost_done
    global firebase_done
    global fire_data_queue
    print "Firebase Listening Queue for Data"
    while not event.isSet():
        firebase_done = True
        while not fire_data_queue.empty():
            firebase_done = False
            #e2 = threading.Event()
            #t2 = threading.Thread(name='non-block', target=flashLed, args=(18,e, 2))
            #t2.start()
            top_data = fire_data_queue.get()
            #print "Data Arrived: ", str(top_data)
            #server_timest = post_to_webhost(top_data)
            if top_data['status']== 'OUT':
                server_time_data = {"time_out":str(top_data['local_timestamp'])}
            else:
                server_time_data = {"time_in":str(top_data['local_timestamp'])}
            write_to_firebase(firebase_root, student_path, server_time_data)
            print "posted to firebase"
            fire_data_queue.task_done()
            #e.set()


def post_queue_to_db(event):
    print "DB Listening Queue for Data"
    e = threading.Event()
    t = threading.Thread(name='flashLed', target=flashLed, args=(18,e, 2))
    t.start()
    global webhost_done
    global firebase_done
    while not event.isSet():
        webhost_done = True
        firebase_done = True
        #try:
        if data_queue is not None:
            while not data_queue.empty():

                if not t.is_alive():
                    e = threading.Event()
                    t = threading.Thread(name='flashLed', target=flashLed, args=(18,e, 2))
                    t.start()
                           
                
                webhost_done = False
                
                top_data = data_queue.get()
                print "Data Arrived: ", str(top_data)
                server_timest = post_to_webhost(top_data)
                print "posted to webhost"
                #if top_data['status']== 'OUT':
                #server_time_data = {"time_out":str(top_data['local_timestamp'])}
                #else:
                #server_time_data = {"time_in":str(top_data['local_timestamp'])}
                #write_to_firebase(firebase_root, student_path, server_time_data)
                #data_queue.task_done()
                #e.set()
                firebase_done = False
                #e2 = threading.Event()
                #t2 = threading.Thread(name='non-block', target=flashLed, args=(18,e, 2))
                #t2.start()
                #top_data = fire_data_queue.get()
                #print "Data Arrived: ", str(top_data)
                #server_timest = post_to_webhost(top_data)
                if top_data['status']== 'OUT':
                    server_time_data = {"time_out":str(top_data['local_timestamp'])}
                else:
                    server_time_data = {"time_in":str(top_data['local_timestamp'])}
                write_to_firebase(firebase_root, student_path, server_time_data)
                print "posted to firebase"
                data_queue.task_done()
        #else:
            #print "***exception raised in post_queue_to_db()***"
            
            
def flashLed(pin_no, e, t):
    global webhost_done
    global firebase_done
    #pin_n = 18
    #GPIO.setmode(GPIO.BOARD)
    #print "flashing pin no: ", pin_n
    #GPIO.setup(pin_n, GPIO.OUT)
    while True:
        global webhost_done
        global firebase_done
        while ((webhost_done == False) or (firebase_done == False)):
            #print "processing .."
            GPIO.output(pin_no, True)
            time.sleep(0.05)
            event_is_set = ((webhost_done == True) and (firebase_done == True))
            if event_is_set:
                GPIO.output(pin_no, False)
                return
                #print('stop led from flashing')
            else:
                GPIO.output(pin_no, False)
                #print('leds off')
                time.sleep(0.05)

        
# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)

# Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()

# Welcome message
print "Welcome,"
print "Press Ctrl-C to stop."
counter = 0
firebase_root=init_firebase()



data_thread_event = threading.Event()
data_thread = threading.Thread(name='post_webhost', target=post_queue_to_webhost, args=(data_thread_event, ))
data_thread.setDaemon(True)
#data_thread.start()

fire_data_thread_event = threading.Event()
fire_data_thread = threading.Thread(name='post_firebase', target=post_queue_to_firebase, args=(fire_data_thread_event, ))
fire_data_thread.setDaemon(True)
#fire_data_thread.start()

db_data_thread_event = threading.Event()
db_data_thread = threading.Thread(name='non-block', target=post_queue_to_db, args=(db_data_thread_event, ))
db_data_thread.setDaemon(True)
db_data_thread.start()


with con:
    cur = con.cursor()
    cur.execute("SELECT school_id, bus_id FROM bus_details")
    rows = cur.fetchall()
    for row in rows:
        busid_str = str(row[1])
        schoolid_str = str(row[0])
        print "School ID: ", schoolid_str, "Bus ID: ", busid_str           

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

        print "CARD UID: ",uid

        # Print UID
        #print "Current Card read UID: "+str(uid[0])+","+str(uid[1])+","+str(uid[2])+","+str(uid[3])
        #print "Last Card read UID: "+str(last_read_uid[0])+str(last_read_uid[1])+str(last_read_uid[2])+str(last_read_uid[3])

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
            GPIO.output(13, False)
            GPIO.output(18, False)
            GPIO.output(11, True)
            
            #print "in read"
	    read_data=MIFAREReader.MFRC522_Read(8)
            #read_timestamp_in=MIFAREReader.MFRC522_Read(9)
            #read_timestamp_out=MIFAREReader.MFRC522_Read(10)
            
	    print "data read: ",read_data
	    #print "-------------------------"
	    #print "flag_bit: ",read_data[5]

            student_path = '/school/'+str("school_"+str(schoolid_str))+'/'+str("class_"+str(read_data[2]))+'/'+str("div_"+str(read_data[3]))+'/'+str(read_data[4])
            #data = {}
            #print "hello1"
	    if read_data != "error":
               # if __name__ == "__main__" :
                st=datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
		if (GPIO.input(35)==1):
		    #print "Going IN"
		    #read_data[5]=0xFF

                    
                    #MIFAREReader.MFRC522_Write(8, read_data)
                    data = {
                        'bus_id':str(busid_str),
                        'school_table':str("school_"+str(schoolid_str)),
                        'student_id':str(str(read_data[0])+str(read_data[2])+str(read_data[3])+str(read_data[4])),
                        'status':'IN',
                        'local_timestamp': str(st)
                    }
                    print data
                    data_queue.put(data)
                    fire_data_queue.put(data)
                    #timest = post_to_webhost(data)
                    #time_in_data = {"time_in":timest}
                    #write_to_firebase(firebase_root, student_path, time_in_data)
                    #t1=threading.Thread(target=MIFAREReader.MFRC522_Write,args = (8,read_data))
                    #t2=threading.Thread(target=write_to_firebase, args = (firebase_root, student_path, time_in_data))
                    #t1.start()
                    #t2.start()
		elif (GPIO.input(37)==1):
		    #print "Going OUT"
                    read_data[5]=0x00
                    
                    #MIFAREReader.MFRC522_Write(8, read_data)
                    data = {
                        'bus_id':str(busid_str),
                        'school_table':str("school_"+str(schoolid_str)),
                        'student_id':str(str(read_data[0])+str(read_data[2])+str(read_data[3])+str(read_data[4])),
                        'status':'OUT',
                        'local_timestamp':str(st)
                    }
                    print data
                    data_queue.put(data)
                    fire_data_queue.put(data)
                    #timest = post_to_webhost(data)
                    #time_out_data = {"time_out":timest}
                    #write_to_firebase(firebase_root, student_path, time_out_data)
                    #t1=threading.Thread(target=MIFAREReader.MFRC522_Write,args = (8,read_data,))
                    #t2=threading.Thread(target=write_to_firebase, args = (firebase_root, student_path, time_out_data, ))
                    #t1.start()
                    #t2.start()
                else:
                    #e.set()
                    GPIO.output(11, False)
                    GPIO.output(13, False)
                    GPIO.output(18, True)
                    print "Select In/Out"
                    time.sleep(0.5)
            print "**num threads** ", threading.active_count()
            MIFAREReader.MFRC522_StopCrypto1()
            time.sleep(1)
            #e.set()
            
            GPIO.output(11, False)
            GPIO.output(18, False)
            GPIO.output(13, True)
            time.sleep(0.5)
       	    print "-----------DONE---------------"
        else:
            #e.set()
            GPIO.output(11, False)
            GPIO.output(13, False)
            GPIO.output(18, True)
            print "Authentication error"
            time.sleep(0.5)
    
