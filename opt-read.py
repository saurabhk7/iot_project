 #!/usr/bin/env python
# -*- coding: utf8 -*-
import sqlite3 as lite
import requests
import json
import MFRC522
import signal
import time
import datetime
import threading
import RPi.GPIO as GPIO
from Queue import Queue
from firebase import firebase

# Takes pin_numbers-boolean_value pairs and time delay
# For turns a particular pin on based on boolean value
def toggle_leds(pin_boolval_pairs, td):
    global GPIO
    for pin_num in pin_boolval_pairs:
        GPIO.output(pin_num, pin_boolval_pairs[pin_num])
        time.sleep(td)

GPIO.setmode(GPIO.BOARD)

GPIO.setup(11, GPIO.OUT)
GPIO.setup(13, GPIO.OUT)
GPIO.setup(18, GPIO.OUT)
GPIO.setup(35, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(37, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

toggle_leds({11:False, 13:False, 18:False}, 0)

def led_start_seq():
    count = 2
    td = 0.15
    toggle_leds({11:True, 13:True, 18:True}, td+0.5)

    for i in range(count):
        toggle_leds({11:True, 13:False, 18:False}, td)
        toggle_leds({11:False, 13:True, 18:False}, td)
        toggle_leds({11:False, 13:False, 18:True}, td)
        toggle_leds({11:False, 13:True, 18:False}, td)
        count-=1

led_start_seq()
toggle_leds({11:False, 18:False}, 0.5)
GPIO.output(13, True)


webhost_done = True
firebase_done = True
continue_reading = True

con = lite.connect('local_data.db')

webhost_db_dumpscript_url = "https://bobtail-chapter.000webhostapp.com/dump.php"
firebase_db_url = 'https://iot-project-c1c1a.firebaseio.com/'

last_read_uid = []

data_queue = Queue()
fire_data_queue = Queue()

busid_str = ''
schoolid_str = ''

# handler for SIGINT
# Capture SIGINT for cleanup when the script is aborted
def end_read(signal, frame):
    global continue_reading
    #global data_thread_event
    GPIO.cleanup()
    print "Ctrl+C captured, ending read."
    continue_reading = False

def get_timestamp():
    return 222222222

# Returns a firebase application object
def init_firebase():
    fire_obj = firebase.FirebaseApplication(firebase_db_url, None)
    return fire_obj


def write_to_firebase(fire_obj, path, data):
    fire_obj.patch(path, data)
    print "posted: "+str(data)+"at: "+str(path)

def post_to_webhost(data_to_post):
    st = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    r = requests.post(url=webhost_db_dumpscript_url, data=data_to_post)
    response = json.loads(r.text)
    if response['timestamp'] is not None:
        return response['timestamp']
    return st

def post_queue_to_webhost(event):
    global webhost_done, firebase_done, data_queue
    print "Webhost Listening Queue for Data"
    while not event.isSet():
        webhost_done = True
        while not data_queue.empty():
            webhost_done = False
            e = threading.Event()
            t = threading.Thread(name='non-block', target=flashLed, args=(18, e, 2))
            t.start()
            top_data = data_queue.get()
            print "Data Arrived: ", str(top_data)
            server_timest = post_to_webhost(top_data)
            print "posted to webhost"
            data_queue.task_done()
            #e.set()

def post_queue_to_firebase(event):
    global webhost_done, firebase_done, fire_data_queue
    print "Firebase Listening Queue for Data"
    while not event.isSet():
        firebase_done = True
        while not fire_data_queue.empty():
            firebase_done = False
            top_data = fire_data_queue.get()
            if top_data['status']== 'OUT':
                server_time_data = {"time_out":str(top_data['local_timestamp'])}
            else:
                server_time_data = {"time_in":str(top_data['local_timestamp'])}
            write_to_firebase(firebase_root, student_path, server_time_data)
            print "posted to firebase"
            fire_data_queue.task_done()


def post_queue_to_db(event):
    print "DB Listening Queue for Data"
    global webhost_done, firebase_done
    while not event.isSet():
        webhost_done = True
        firebase_done = True
        #try:
        if data_queue is not None:
            while not data_queue.empty():
                webhost_done = False
                e = threading.Event()
                t = threading.Thread(name='flashLed', target=flashLed, args=(18,e, 2))
                t.start()
                top_data = data_queue.get()
                print "Data Arrived: ", str(top_data)
                server_timest = post_to_webhost(top_data)
                print "posted to webhost"
                firebase_done = False
                if top_data['status']== 'OUT':
                    server_time_data = {"time_out":str(top_data['local_timestamp'])}
                else:
                    server_time_data = {"time_in":str(top_data['local_timestamp'])}
                write_to_firebase(firebase_root, student_path, server_time_data)
                print "posted to firebase"
                data_queue.task_done()


def flashLed(pin_no, e, t):
    global webhost_done, firebase_done
    while True:
        while ((webhost_done == False) or (firebase_done == False)):
            #print "processing .."
            GPIO.output(pin_no, True)
            time.sleep(0.05)
            GPIO.output(pin_no, False)
            if (webhost_done == True) and (firebase_done == True):
                return
            time.sleep(0.05)


# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)

# Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()

# Welcome message
print "Welcome,"
print "Press Ctrl-C to stop."
counter = 0
firebase_root = init_firebase()


data_thread_event = threading.Event()
data_thread = threading.Thread(name='post_webhost', target=post_queue_to_webhost, args=(data_thread_event, ))
data_thread.setDaemon(True)
data_thread.start()

fire_data_thread_event = threading.Event()
fire_data_thread = threading.Thread(name='post_firebase', target=post_queue_to_firebase, args=(fire_data_thread_event, ))
fire_data_thread.setDaemon(True)
fire_data_thread.start()

db_data_thread_event = threading.Event()
db_data_thread = threading.Thread(name='non-block', target=post_queue_to_db, args=(db_data_thread_event, ))
db_data_thread.setDaemon(True)
# db_data_thread.start()


with con:
    cur = con.cursor()
    cur.execute("SELECT school_id, bus_id FROM bus_details")
    rows = cur.fetchall()
    for row in rows:
        busid_str = str(row[1])
        schoolid_str = str(row[0])
        print "School ID: ", schoolid_str, "Bus ID: ", busid_str

# This loop keeps checking for chips. If one is near it will get the UID and authenticate
#last_read_uid = uid
while continue_reading:
    # Scan for cards
    (status, TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
    if status == MIFAREReader.MI_OK:                    # If a card is found
        print "Card detected"

    (status, uid) = MIFAREReader.MFRC522_Anticoll()     # Get the UID of the card
    if status == MIFAREReader.MI_OK:                    # If we have the UID, continue
        print "CARD UID: ",uid

        # This is the default key for authentication
        key = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]

        MIFAREReader.MFRC522_SelectTag(uid)             # Select the scanned tag
        status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, 8, key, uid)             # Authenticate
        read_data =[]

        # Check if authenticated
        if status == MIFAREReader.MI_OK:
            toggle_leds({13:False, 18:False, 11:False}, 0)
            #print "in read"
	    read_data = MIFAREReader.MFRC522_Read(8)
	    print "data read: ",read_data
	    #print "-------------------------"
	    #print "flag_bit: ",read_data[5]

        student_path = '/school/' \
            + str("school_" + str(schoolid_str)) + '/'  \
            + str("class_"  + str(read_data[2])) + '/'  \
            + str("div_"    + str(read_data[3])) + '/'  \
            + str(read_data[4])

        if read_data != "error":
            st=datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
            data = {
                'school_table': str("school_"+str(schoolid_str)),
                'student_id': str(str(read_data[0])+str(read_data[2])+str(read_data[3])+str(read_data[4])),
                'local_timestamp': str(st)
            }
            if (GPIO.input(35)==1):
                data.update({
                    'bus_id': str(busid_str),
                    'status':'IN',
                })
                print data
                data_queue.put(data)
                fire_data_queue.put(data)

            elif (GPIO.input(37)==1):
                read_data[5]=0x00
                data.update({
                    'bus_id':str(read_data[1]),
                    'status':'OUT',
                })
                print data
                data_queue.put(data)
                fire_data_queue.put(data)
            else:
                toggle_leds({11:False, 13:False, 18:True}, 0.5)
                print "Select In/Out"
            MIFAREReader.MFRC522_StopCrypto1()
            time.sleep(1)
            #e.set()

            toggle_leds({11:False, 13:True, 18:False}, 0.5)
            print "-----------DONE---------------"
        else:
                #e.set()
            toggle_leds({11:False, 13:False, 18:True}, 0.5)
            print "Authentication error"
