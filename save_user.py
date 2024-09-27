#!/usr/bin/env Python

import time
import RPi.GPIO as GPIO

from pn532 import *

import mysql.connector

db = mysql.connector.connect(user='admin', passwd='pimylifeup', database='attendancesystem')

cursor = db.cursor()

active=True


if __name__ == '__main__':
    try:
        pn532 = PN532_SPI(debug=False, reset=20, cs=4)

        ic, ver, rev, support = pn532.get_firmware_version()
        print('Found PN532 with firmware version: {0}.{1}'.format(ver, rev))

        # Configure PN532 to communicate with MiFare cards
        pn532.SAM_configuration()

        print('Waiting for RFID/NFC card...')
        while active:
            # Check if a card is available to read
            bar=[]
            uid = pn532.read_passive_target(timeout=0.5)
            # Try again if no card is available.
            if uid is None:
                continue
            for foo in uid:
                bar.append(foo)
            #print('Found card with UID:', [print(i) for i in uid])
            bar = ''.join(map(str, bar)).replace('.', '')
            print(f"Found card with UID: {bar}")
            cursor.execute("SELECT * FROM users WHERE rfid_uid="+str(bar))
            #cursor.fetchone()
            rows = cursor.fetchone()

            if cursor.rowcount >= 1:
                print(f'Exisiting user found. {rows[2]} is attached to this card')
                overwrite = input("Overwrite (Y/N)? ")

                if overwrite[0] == 'Y' or overwrite[0] == 'y':
                    print("Overwriting user.")
                    time.sleep(1)
                    sql_insert = "UPDATE users SET name = %s WHERE rfid_uid=%s"
                else:
                  print('Waiting for RFID/NFC card...')
            else:
              sql_insert = "INSERT INTO users (name, rfid_uid) VALUES (%s, %s)"
              print('Enter new name:')
              new_name = input("Name: ")

              cursor.execute(sql_insert, (new_name, bar))

              db.commit()

              print("User " + new_name + "\nSaved")
    except Exception as e:
        print(e)
    finally:
        GPIO.cleanup()
