#!/usr/bin/env python
import time
import RPi.GPIO as GPIO
from pn532 import *
import mysql.connector

active = True

db = mysql.connector.connect(
  host="localhost",
  user="admin",
  passwd="pimylifeup",
  database="attendancesystem"
)

cursor = db.cursor()


if __name__ == '__main__':
    try:
        pn532 = PN532_SPI(debug=False, reset=20, cs=4)

        ic, ver, rev, support = pn532.get_firmware_version()
        print('Found PN532 with firmware version: {0}.{1}'.format(ver, rev))

        # Configure PN532 to communicate with MiFare cards
        pn532.SAM_configuration()

        print('Place card to\nrecord attendance')
        while active:
            # Check if a card is available to read
            bar=[]
            uid = pn532.read_passive_target(timeout=0.5)
            # Try again if no card is available.
            if uid is None:
                continue
            for foo in uid:
                bar.append(foo)
            bar = ''.join(map(str, bar)).replace('.', '')
            print(f"Found card with UID: {bar}")
            cursor.execute("SELECT id, name FROM users WHERE rfid_uid="+str(bar))
            result = cursor.fetchone()

            if cursor.rowcount >= 1:
                print("Welcome " + result[1] + "! Enjoy rehearsal!")
                cursor.execute("INSERT INTO attendance (user_id) VALUES (%s)", (result[0],) )
                db.commit()
            else:
                print("The user can't be found.")

    except Exception as e:
        print(e)
    finally:
        GPIO.cleanup()