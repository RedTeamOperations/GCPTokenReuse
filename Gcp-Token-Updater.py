import sqlite3
import sys
import string
import random
import os
import json
import optparse
import logging
from argparse import RawTextHelpFormatter
import urllib.request

# Global Variable
access_db = ""
credential_db = ""
account_id = ""


def database_location():
    # Access Token Location Retrieve
    global access_db
    global credential_db
    if os.name == 'nt':
        access_db = os.path.join(os.path.expanduser('~'), r"AppData\Roaming\gcloud", "access_tokens.db")
        credential_db = os.path.join(os.path.expanduser('~'), r"AppData\Roaming\gcloud", "credentials.db")
    elif os.name == 'posix':
        access_db = os.path.join(os.path.expanduser('~'), ".config/gcloud", "access_tokens.db")
        credential_db = os.path.join(os.path.expanduser('~'), ".config/gcloud", "credentials.db")
    else:
        pass


def token_validation(access_token):
    print("Validating Access Token ..............")
    try:
        req = "https://www.googleapis.com/oauth2/v1/tokeninfo?access_token="+str(access_token)
        res = urllib.request.urlopen(req)
        response = (res.read(100).decode('utf-8'))
    except:
        print("Invalid / Expired Token.")
        exit()


def token_insertion(access_token,account_id):
    # Updating Access_Token Database
    conn = sqlite3.connect(access_db)
    cursor = conn.execute("select * from access_tokens")
    for row in cursor:
        name = row[0]
        token = row[1]
        date = row[2]
        id_token = row[3]

    token_new = access_token
    rapt_token = ""
    
    try:
        cursor = conn.execute("INSERT into access_tokens (account_id,access_token,token_expiry,rapt_token,id_token) values (?,?,?,?,?)", (account_id,token_new,date,rapt_token,id_token))
        conn.commit()
        conn.close()
        print("Updated access_token database successfully")
    except:
        print("Please use unique profile name")

    # Updating Credential Database
    conn = sqlite3.connect(credential_db)
    cursor = conn.execute("select * from credentials")
    for row in cursor:
        name = row[0]
        value = row[1]
    try:
        cursor = conn.execute("INSERT into credentials (account_id,value) values (?,?)", (account_id,value))
        conn.commit()
        conn.close()
        print("Updated credentials database successfully")
    except:
        pass

def token_deletion(account_name):
    # Deletion Access_Token Database
    conn = sqlite3.connect(access_db)
    query1 = "DELETE FROM access_tokens WHERE account_id = ?"
    try:
        cursor = conn.execute(query1, (account_name,))
        conn.commit()
        conn.close()
        print("Deleted access_token database successfully")
    except:
        print("Please use existing profile name")

    # Deletion Credential Database
    conn = sqlite3.connect(credential_db)
    query2 = "DELETE FROM credentials WHERE account_id = ?"
    try:
        cursor = conn.execute(query2, (account_name,))
        conn.commit()
        conn.close()
        print("Deleted credentials database successfully")
    except: 
       pass 


if __name__ == '__main__':
    # argument Parsing
    cmd_options= {}
    parser = optparse.OptionParser(description='GCP Access Token Reuse',usage="Usage: %prog [options] Access-Token",version="%prog 1.0")
    parser.add_option('-I', '--insert', action="store_true", dest='token_insert', help="Insert New Access Token")
    parser.add_option('-D', '--delete', action="store_true", dest='token_delete',help="Delete Existing Access Token")
    parser.add_option('--access-token', action="store", dest='access_token', help="GCP Access Token")
    parser.add_option('--account-name', action="store", dest='account_name', help="Profile Account Name")
    cmd_options = parser.parse_args()[0]

    if cmd_options.token_insert and cmd_options.token_delete:
        print("Choose only one option Either -I or -D")
        
    elif not cmd_options.token_insert and not cmd_options.token_delete:
        print("Choose at least one option -I for new token updation OR -D for active sesseion Deletion")
        
    elif cmd_options.token_insert:
        if cmd_options.access_token and cmd_options.account_name:
            database_location()
            access_token = cmd_options.access_token
            account_id = cmd_options.account_name
            try:
                token_validation(access_token)
                token_insertion(access_token,account_id)
            except:
                pass        
        elif not cmd_options.access_token:
            print("Specify --access-token TokenValue")
            sys.exit() 
        elif not cmd_options.account_name:
            print("Specify --account-name ProfileName")
            sys.exit()     
        else:
            print("Specify --access-token TokenValue and --account-name ProfileName")
            sys.exit()
            
    elif cmd_options.token_delete:
        if cmd_options.account_name:
            database_location()
            account_name = cmd_options.account_name
            token_deletion(account_name)
        else:
            print("Specify --account-name ActiveProfileName")
            sys.exit()
    else:
        pass
