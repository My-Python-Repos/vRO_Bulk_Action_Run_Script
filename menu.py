#!/usr/bin/python
#=========================================================================================================
#
#   NAME        :      menu.py
#
#   DESC        :      All The Menu Function to provide the vRA Action run on multiple VMs
#
#   DESCRIPITON :      vRA Action Run
#
#   AUTHOR      :      Praveen Beniwal
#
#   EMAIL ID    :      praveen1664@outlook.com
#                      
#
#   HISTORY     :      04-05-2020
#
#
#   version     :  1.0
#
#=========================================================================================================
#import urllib.request
import sys
import json
import os
import base64
from Crypto.Cipher import AES
import urllib3
urllib3.disable_warnings()
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from requests.auth import HTTPBasicAuth
import ssl
from contextlib import contextmanager
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from getpass import getpass
from menu import *
import xlrd
import csv
import datetime
import time
import MySQLdb
import os
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

try:
    from collections import OrderedDict;
except ImportError:
    from odict import odict as OrderedDict;

def printTable(valDict, colList=None):
    if not colList:
        colList = list(valDict[0].keys() if valDict else [])
    valList = [colList]  # 1st row = header
    for item in valDict:
        valList.append([str(item[col] or '') for col in colList])
    colSize = [max(map(len, col)) for col in zip(*valList)]
    for i in range(0, len(valList) + 1)[::-1]:
        valList.insert(i, ['-' * i for i in colSize])
    formatStr = ' | '.join(["{{{0}:<{1}}}".format(idx, val) for idx, val in enumerate(colSize)])
    formatSep = '-+-'.join(["{{{0}:<{1}}}".format(idx, val) for idx, val in enumerate(colSize)])
    for item in valList:
        if item[0][0] == '-':
            print(formatSep.format(*item))
        else:
            print(formatStr.format(*item))


def rmfile(dirpath):
    try:
        os.remove(dirpath)
    except:
        pass

def sleep_tm(tm_scd):
    print "\n"
    sleep_counter=1
    ping_loop=True
    while ping_loop:
        print ".",
        sys.stdout.flush()
        if sleep_counter == tm_scd:
            break
        sleep_counter += 1
        time.sleep(1)


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    SKYBLUE = '\33[96m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    CWHITE  = '\33[37m'
    CWHITE2  = '\33[97m'
    CWHITEBG2  = '\33[107m'
    CWHITEBG  = '\33[47m'
    NEWCOL = '\33[96m'
    PINK = '\033[95m'



def read_file():
    contents=open('/tmp/report.csv','r')
    return ''.join(contents.readlines())


class mysql_connection(object):
    __host       = None
    __user       = None
    __password   = None
    __database   = None
    __session    = None
    __connection = None

    def __init__(self, host='localhost', user='root', password='', database=''):
        self.__host     = host
        self.__user     = user
        self.__password = password
        self.__database = database

    def __open(self):
        try:
            cnx = MySQLdb.connect(self.__host, self.__user, self.__password, self.__database)
            self.__connection = cnx
            self.__session    = cnx.cursor()
        except MySQLdb.Error as e:
            print "Error %d: %s" % (e.args[0],e.args[1])

    def __close(self):
        self.__session.close()
        self.__connection.close()

    def select_query(self, table, where=None, *args, **kwargs):
        result = None
        query = 'SELECT * '
        keys = args
        values = tuple(kwargs.values())
        l = len(keys) - 1
        for i, key in enumerate(keys):
            query += "`"+key+"`"
            if i < l:
                query += ","
        query += 'FROM  %s' % table
        if where:
            query += " WHERE %s" % where
        self.__open()
        self.__session.execute(query, values)
        number_rows = self.__session.rowcount
        number_columns = len(self.__session.description)
        if number_rows >= 1 and number_columns > 1:
            result = [item for item in self.__session.fetchall()]
        else:
            result = [item[0] for item in self.__session.fetchall()]
        self.__close()
        return result

    def update_query(self, table, where=None, *args, **kwargs):
        query  = "UPDATE %s SET " % table
        keys   = kwargs.keys()
        values = tuple(kwargs.values()) + tuple(args)
        l = len(keys) - 1
        for i, key in enumerate(keys):
            query += "`"+key+"` = %s"
            if i < l:
                query += ","
        query += " WHERE %s" % where
        self.__open()
        self.__session.execute(query, values)
        self.__connection.commit()
        update_rows = self.__session.rowcount
        self.__close()
        return update_rows

    def insert_query(self, table, *args, **kwargs):
        values = None
        query = "INSERT INTO %s " % table
        if kwargs:
            keys = kwargs.keys()
            values = tuple(kwargs.values())
            query += "(" + ",".join(["`%s`"] * len(keys)) %  tuple (keys) + ") VALUES (" + ",".join(["%s"]*len(values)) + ")"
        elif args:
            values = args
            query += " VALUES(" + ",".join(["%s"]*len(values)) + ")"
        self.__open()
        self.__session.execute(query, values)
        self.__connection.commit()
        self.__close()
        return self.__session.lastrowid

    def delete_query(self, table, where=None, *args):
        query = "DELETE FROM %s" % table
        if where:
            query += ' WHERE %s' % where
        values = tuple(args)
        self.__open()
        self.__session.execute(query, values)
        self.__connection.commit()
        delete_rows = self.__session.rowcount
        self.__close()
        return delete_rows


def mail_status_send(sender_id,receiver_id,mail_subject):
    msg = MIMEMultipart()
    msg['Subject'] = mail_subject
    msg['From'] = sender_id
    msg['To'] = receiver_id
    mail_body = MIMEText(read_file(), 'plain')
    msg.attach(mail_body)
    with open(file, "rb") as attachment:
         # The content type "application/octet-stream" means that a MIME attachment is a binary file
         part = MIMEBase("application", "octet-stream")
         part.set_payload(attachment.read())

         # Encode to base64
         encoders.encode_base64(part)

    # Add header 
    part.add_header("Content-Disposition","part; filename= report",
    )	
    msg.attach(part)
    text = msg.as_string()
    #msg.attach(mail_body)
    sender_host = smtplib.SMTP('localhost')
    sender_host.sendmail(sender_id, receiver_id.split(","), text)
    sender_host.quit()
    #rmfile('/tmp/tmp_email')
'''
def mail_status_send(sender_id,receiver_id,mail_subject):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = mail_subject
    msg['From'] = sender_id
    msg['To'] = receiver_id
    mail_body = MIMEText(read_file(), 'plain')
    msg.attach(mail_body)
    sender_host = smtplib.SMTP('localhost')
    sender_host.sendmail(sender_id, receiver_id.split(","), msg.as_string())
    sender_host.quit()
    #rmfile('/tmp/tmp_email')
'''

def env_selection():
    clear()
    print 60 * " "
    print 60 * " "
    print bcolors.OKBLUE + 77 * "-" + bcolors.ENDC
    print bcolors.OKBLUE + 1 * "|" + bcolors.ENDC, 20 * " ", bcolors.BOLD + bcolors.CWHITE2 + "Environment Selection"+ bcolors.ENDC, 30 * " ", bcolors.OKBLUE + 1 * "|" + bcolors.ENDC
    print bcolors.OKBLUE + 77 * "-" + bcolors.ENDC
    print 60 * " "
    print bcolors.BOLD + bcolors.CWHITE2 + 4 * " ", "1. Dev"
    print bcolors.BOLD + bcolors.CWHITE2 + 4 * " ", "2. Test"
    print bcolors.BOLD + bcolors.CWHITE2 + 4 * " ", "3. Stage"
    print bcolors.BOLD + bcolors.CWHITE2 + 4 * " ", "4. Prod"
    print bcolors.BOLD + bcolors.CWHITE2 + 4 * " ", "5. Exit" + bcolors.ENDC	
    print 60 * " "
    print bcolors.OKBLUE + 77 * "-" + bcolors.ENDC


def clear():
    os.system('clear')

def act_selection():
    clear()
    print 60 * " "
    print 60 * " "
    print bcolors.OKBLUE + 77 * "-" + bcolors.ENDC
    print bcolors.OKBLUE + 1 * "|" + bcolors.ENDC, 20 * " ", bcolors.BOLD + bcolors.CWHITE2 + "Action Selection"+ bcolors.ENDC, 35 * " ", bcolors.OKBLUE + 1 * "|" + bcolors.ENDC
    print bcolors.OKBLUE + 77 * "-" + bcolors.ENDC
    print 60 * " "
    print bcolors.BOLD + bcolors.CWHITE2 + 4 * " ", "1. Power Off "
    print bcolors.BOLD + bcolors.CWHITE2 + 4 * " ", "2. Destroy"
    print bcolors.BOLD + bcolors.CWHITE2 + 4 * " ", "3. Change Owner"
    print bcolors.BOLD + bcolors.CWHITE2 + 4 * " ", "4. Reboot"
    print bcolors.BOLD + bcolors.CWHITE2 + 4 * " ", "5. Shutdown"
    print bcolors.BOLD + bcolors.CWHITE2 + 4 * " ", "6. Set Shared Access Control"
    print bcolors.BOLD + bcolors.CWHITE2 + 4 * " ", "7. Decommission"		
    print bcolors.BOLD + bcolors.CWHITE2 + 4 * " ", "8. Exit" + bcolors.ENDC
    print 60 * " "
    print bcolors.OKBLUE + 77 * "-" + bcolors.ENDC

def WAITContinue():
    wailtC=True
    while wailtC:
        EntExt = raw_input("\nPress [Yes] key to continue Or Type [Exit/No] to Exit the code.: ")
        if EntExt in ('EXIT', 'exit', 'Exit', 'NO','N','No','no'):
            sys.exit()
        elif EntExt in ('YES','Y','Yes','yes','y'):
            break
        else:
            input("Wrong input selection. Press [Yes] key to continue Or Type [Exit/No]  and try again... ")

class date_time(object):
    def sqldate(self):
        return datetime.datetime.now().strftime('%d-%m-%Y')

    def sqltime(self):
        return datetime.datetime.now().strftime('%H-%M-%S')


sender_id = 'your_email@your_org_name.com'
connect_mysql = mysql_connection(user='root', password='your_password', database='day_two_action_DB')
clear()
print 60 * " "
print 60 * " "
file="/tmp/report.csv"
