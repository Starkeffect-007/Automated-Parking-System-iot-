#!/usr/bin/python
import mysql.connector as MySQLdb
import sys
from mfrc522 import SimpleMFRC522
import time
import RPi.GPIO as GPIO
import requests

GPIO.setwarnings(False)

dbase = MySQLdb.connect(host='localhost',user='admin1',password='root',db='parking')
print ("Connect")

GPIO.setmode(GPIO.BCM)
buzzer=23
GPIO.setup(buzzer,GPIO.OUT)
    

slots = 3
reader=SimpleMFRC522()
cursor = dbase.cursor()


def message(id2):
     cursor.execute("""select price from completed_records where uid={} """.format(id2))
     data=cursor.fetchall()
     for row in data:
         value = row[0]
     
     cursor.execute("""select contact from user_details where uid={} """.format(id2))
     data1=cursor.fetchall()
     for row in data1:
         num = row[0]
     url = "https://www.fast2sms.com/dev/bulk"
     payload = "sender_id=FSTSMS&message=       Thank you for using our service. Your total challan is:{}&language=english&route=p&numbers={}".format(value,num)
     headers = {
     'authorization': "cV9XaDIv4J3isCEOhYjTql2WoZRHQpM1Gk87zLduK6FmyP5bettynQ4UA6XfugeEmoKBd9VWp1Rv8hkC",
     'Content-Type': "application/x-www-form-urlencoded",
     'Cache-Control': "no-cache",
     }
     response = requests.request("POST", url, data=payload, headers=headers)
     



def buzz():
    GPIO.output(buzzer,GPIO.HIGH)
    time.sleep(1)
    GPIO.output(buzzer,GPIO.LOW)


def entry(uid):
    global slots
    if(slots>0):
          sql1 = """insert into entry_exit(uid,entry_time) values ({},curtime());""".format(uid)
          cursor.execute(sql1)
          slots = slots-1
          print ("free slots available:- {}".format(slots))
    else:
        buzz()
        print("No free slots available right now")
        return   
    dbase.commit()
 
 #print("You have successfully entered the facility")

 
 
 #reader1=SimpleMFRC522()
 #cursor = dbase.cursor()
 
def exit(id1):
     global slots
     sql = """UPDATE entry_exit set exit_time=curtime() where uid={}""".format(id1)
     cursor.execute(sql)
     time.sleep(1)
     sql2="""delete from entry_exit where uid={}""".format(id1)
     cursor.execute(sql2)
     message(id1)
     slots=slots+1
     dbase.commit()
     print("You are now leaving the facility")
     print("Thank u you for using our services")
     print ("free slots available:- {}".format(slots))     




def read():
     uid,text=reader.read()
     query = """select uid from entry_exit where uid = {}""".format(uid)
     cursor.execute(query)
     if cursor.fetchone():
         exit(uid)
         return
     else:
        entry(uid)
        return

while True:
    try:
        read()
        time.sleep(2)
    except KeyboardInterrupt:
        GPIO.cleanup()
        break
