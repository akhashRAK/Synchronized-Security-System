import time
import board
import busio
from digitalio import DigitalInOut, Direction
import adafruit_fingerprint
import mysql.connector as mariadb
from datetime import datetime
now = datetime.now()
import cv2
import smtplib
from email.message import EmailMessage
id = 1
formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')

mariadb_localconnection = mariadb.connect(user='root',password= 'SSNSSS',database='SSS', host='localhost')
create_cursor1= mariadb_localconnection.cursor()
mariadb_awsconnection = mariadb.connect(user='admin',password= 'SSNSSSAA',database='SSS', host='sssdatabase.caa9ni3wisfg.ap-south-1.rds.amazonaws.com',port=3306)
create_cursor2= mariadb_awsconnection.cursor()
#led = DigitalInOut(board.D13)
#led.direction = Direction.OUTPUT

#uart = busio.UART(board.TX, board.RX, baudrate=57600)

# If using with a computer such as Linux/RaspberryPi, Mac, Windows with USB/serial converter:
import serial
uart = serial.Serial("/dev/ttyUSB0", baudrate=57600, timeout=1)

# If using with Linux/Raspberry Pi and hardware UART:
# import serial
# uart = serial.Serial("/dev/ttyS0", baudrate=57600, timeout=1)

finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)

##################################################


def get_fingerprint():
    """Get a finger print image, template it, and see if it matches!"""
    print("Waiting for image...")
    while finger.get_image() != adafruit_fingerprint.OK:
        pass
    print("Templating...")
    if finger.image_2_tz(1) != adafruit_fingerprint.OK:
        return False
    print("Searching...")
    if finger.finger_search() != adafruit_fingerprint.OK:
        return False
    return True


# pylint: disable=too-many-branches
def get_fingerprint_detail():
    """Get a finger print image, template it, and see if it matches!
    This time, print out each error instead of just returning on failure"""
    print("Getting image...", end="")
    i = finger.get_image()
    if i == adafruit_fingerprint.OK:
        print("Image taken")
    else:
        if i == adafruit_fingerprint.NOFINGER:
            print("No finger detected")
        elif i == adafruit_fingerprint.IMAGEFAIL:
            print("Imaging error")
        else:
            print("Other error")
        return False

    print("Templating...", end="")
    i = finger.image_2_tz(1)
    if i == adafruit_fingerprint.OK:
        print("Templated")
    else:
        if i == adafruit_fingerprint.IMAGEMESS:
            print("Image too messy")
        elif i == adafruit_fingerprint.FEATUREFAIL:
            print("Could not identify features")
        elif i == adafruit_fingerprint.INVALIDIMAGE:
            print("Image invalid")
        else:
            print("Other error")
        return False

    print("Searching...", end="")
    i = finger.finger_fast_search()
    # pylint: disable=no-else-return
    # This block needs to be refactored when it can be tested.
    if i == adafruit_fingerprint.OK:
        print("Found fingerprint!")
        return True
    else:
        if i == adafruit_fingerprint.NOTFOUND:
            print("No match found")
        else:
            print("Other error")
        return False


# pylint: disable=too-many-statements
def enroll_finger(location):
    """Take a 2 finger images and template it, then store in 'location'"""
    user_id = location
    print(user_id)
    statement_enroll= 'INSERT INTO FINGERPRINT_AUTHENTICATION(ID,DATE_TIME,ACTION,USER_ID) VALUES (1,"'+str(formatted_date)+'","New User enrolled",'+ str(user_id) +');'
    
    for fingerimg in range(1, 3):
        if fingerimg == 1:
            print("Place finger on sensor...", end="")
        else:
            print("Place same finger again...", end="")

        while True:
            i = finger.get_image()
            if i == adafruit_fingerprint.OK:
                print("Image taken")
                break
            if i == adafruit_fingerprint.NOFINGER:
                print(".", end="")
            elif i == adafruit_fingerprint.IMAGEFAIL:
                print("Imaging error")
                return False
            else:
                print("Other error")
                return False

        print("Templating...", end="")
        i = finger.image_2_tz(fingerimg)
        if i == adafruit_fingerprint.OK:
            print("Templated")
        else:
            if i == adafruit_fingerprint.IMAGEMESS:
                print("Image too messy")
            elif i == adafruit_fingerprint.FEATUREFAIL:
                print("Could not identify features")
            elif i == adafruit_fingerprint.INVALIDIMAGE:
                print("Image invalid")
            else:
                print("Other error")
            return False

        if fingerimg == 1:
            print("Remove finger")
            time.sleep(1)
            while i != adafruit_fingerprint.NOFINGER:
                i = finger.get_image()

    print("Creating model...", end="")
    i = finger.create_model()
    if i == adafruit_fingerprint.OK:
        print("Created")
    else:
        if i == adafruit_fingerprint.ENROLLMISMATCH:
            print("Prints did not match")
        else:
            print("Other error")
        return False

    print("Storing model #%d..." % location, end="")
    i = finger.store_model(location)
    if i == adafruit_fingerprint.OK:
        print("Stored")
        create_cursor1.execute(statement_enroll)
        mariadb_localconnection.commit()
        create_cursor2.execute(statement_enroll)
        mariadb_awsconnection.commit()
    else:
        if i == adafruit_fingerprint.BADLOCATION:
            print("Bad storage location")
        elif i == adafruit_fingerprint.FLASHERR:
            print("Flash storage error")
        else:
            print("Other error")
        return False
    
    return True


##################################################


def get_num():
    """Use input() to get a valid number from 1 to 127. Retry till success!"""
    i = 0
    while (i > 127) or (i < 1):
        try:
            i = int(input("Enter ID # from 1-127: "))
        except ValueError:
            pass
    return i


while True:
    print("----------------")
    if finger.read_templates() != adafruit_fingerprint.OK:
        raise RuntimeError("Failed to read templates")
    print("Fingerprint templates:", finger.templates)
    print("e) enroll print")
    print("f) find print")
    print("d) delete print")
    print("----------------")
    c = input("> ")

    if c == "e":
        enroll_finger(get_num())
    if c == "f":
        cam=cv2.VideoCapture(0)
        if get_fingerprint() and finger.confidence>100:
            print("Detected #", finger.finger_id, "with confidence", finger.confidence)
            statement_user_detected= 'INSERT INTO FINGERPRINT_AUTHENTICATION(ID,DATE_TIME,ACTION,USER_ID) VALUES (1,"'+str(formatted_date)+'","User detected",'+ str(finger.finger_id) +');'
            create_cursor1.execute(statement_user_detected)
            mariadb_localconnection.commit()
            create_cursor2.execute(statement_user_detected)
            mariadb_awsconnection.commit()
            del(cam)
        else:
            ret,image=cam.read()
            fname= 'Failed attempt.jpg'
            cv2.imwrite(fname,image)
            msg= EmailMessage()
            msg['From']='sssmailservice@gmail.com'
            msg['To']='akhash2110552@ssn.edu.in'
            server=smtplib.SMTP_SSL('smtp.gmail.com',465)
            server.login('sssmailservice@gmail.com','ubpm vwgk rhkh sgyu')
            with open(fname,'rb') as img:
                data=img.read()
            msg.add_attachment(data, maintype = 'image', subtype = 'jpg', filename = fname) 
            server.send_message(msg)
            print("done")
            del(cam)
            
                    
            print("Finger not found")
            statement_no_user= 'INSERT INTO FINGERPRINT_AUTHENTICATION(ID,DATE_TIME,ACTION,USER_ID) VALUES (1,"'+str(formatted_date)+'","Failed attempt",-1);'
            create_cursor1.execute(statement_no_user)
            mariadb_localconnection.commit()
            create_cursor2.execute(statement_no_user)
            mariadb_awsconnection.commit()
            
            
    if c == "d":
        if finger.delete_model(get_num()) == adafruit_fingerprint.OK:
            num=get_num()
            print("Deleted!")
            statement_delete= 'INSERT INTO FINGERPRINT_AUTHENTICATION(ID,DATE_TIME,ACTION,USER_ID) VALUES (1,"'+str(formatted_date)+'","Deleted",'+ str(num)+';'
            create_cursor1.execute(statement_delete)
            mariadb_localconnection.commit()
            create_cursor2.execute(statement_delete)
            mariadb_awsconnection.commit()
        else:
            print("Failed to delete")
            statement_deletefailure= 'INSERT INTO FINGERPRINT_AUTHENTICATION(ID,DATE_TIME,ACTION,USER_ID) VALUES (1,"'+str(formatted_date)+'","Deletion failed",-1;'
            create_cursor1.execute(statement_deletefailure)
            mariadb_localconnection.commit()
            create_cursor2.execute(statement_deletefailure)
            mariadb_awsconnection.commit()

