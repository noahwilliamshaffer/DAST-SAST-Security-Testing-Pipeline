# pwmodule.py
#
# Module to handle passwords
# 

import os
import re

import abacfg
import pwcrypto

# PwSetup
#
# Open Open the password database, extract the hashes
def PwSetup():
    global accountdict 
    global accountschanged

    accountdict = {}
    accountschanged = False # Flag to keep track of changes to accounts

    completionCode = "OK"

    try:
        pwfile = open(abacfg.PWFILE, "a+")
        pwfile.seek(0)
        pwaccountlist = pwfile.read().splitlines()
        #print("(debugging) pwmodule.PwSetup pwaccountlist = ", pwaccountlist)
        for line in pwaccountlist:
        #    print("(debugging) pwmodule.PwSetup line = ", line)
            acct = line.split(':')
        #    print("(debugging) pwmodule.PwSetup acct = ", acct)
            if len(acct) == 1: # There is no password, set to ''
                accountdict[acct[0]] = ''
            else:
                accountdict[acct[0]] = acct[1]
        #    print("(debugging) pwmodule.PwSetup accountdict = ", accountdict)
            # If no admin account (i.e., first time program runs), add it
        if not ('admin' in accountdict.keys()):
            accountdict['admin'] = ''
        #print("(debugging) pwmodule.PwSetup accountdict = ", accountdict)
    except Exception as e:
        completionCode = "UNEXPECTED ERROR (pwmodule.PwSetup): " + str(e)


    return completionCode


# PwShutdown
#
# Close the password database, flushing all changes to the password file
def PwShutdown():
    global accountdict
    global accountschanged

    completionCode = "OK"

    #print("(debugging) pwmodule.PwShutdown accountschanged = ", accountschanged)

    if accountschanged == True: # Need to write changes to password file
        try:
            pwfile = open(abacfg.PWFILE, "w") # Truncate file for writing
            for uname, pw in accountdict.items():
                #print("(debugging) pwmodule.PwShutdown writing to file: ", uname, ", ", pw)
                if pw == '': # No password yet
                    pwfile.write('%s:\n' % (uname))
                else: 
                    pwfile.write('%s:%s\n' % (uname, pw))
            pwfile.close()
        except Exception as e:
            completionCode = ("UNEXPECTED ERROR: pwmodule.PwShutdown - ", e)
    else: # No account changes
        pass

    return completionCode





def GoodUsrID(userID):
    # Check if a UserID meets all requirements
    #
    if len(userID) > 0 and len(userID) <= 16 and userID.isalnum():
        result = True
    else:
        result = False

    return result




# AccountExists
#
# Return True if an account exists; False otherwise
def AccountExists(userID):
    global accountdict

    if userID.lower() in accountdict.keys():
        result = True
    else:
        result = False

    return result


# HasPassword
#
# True if the account has a password; False otherwise
def HasPassword(userID):
    global accountdict

    result = False
    if AccountExists(userID):
        if accountdict.get(userID.lower()) != '':
            result = True

    return result


# SetPassword
#
# If account exists, update the password.
# If account does not exist, create it with that password
# If the password is '' (empty string), don't hash it
# The only requirement on the passwd argument is that it is not equal to None
# 
def SetPassword(userID, passwd):
    global accountdict
    global accountschanged

    completionCode = "UNEXPECTED ERROR (pwmodule.SetPassword): 'None' argument"

    if passwd != None:
        if passwd == '': # New account
            accountdict.update({userID: ''})
        else:
            accountdict.update({userID: pwcrypto.CreatePwHash(passwd)})
        accountschanged = True
        completionCode = "OK"
        #print("(debugging) pwmodule.SetPassword accountdict = ", accountdict)

    return completionCode


# Login
#
# Permit user to enter their password; check if it is correct
def Login(userID, passwd):
    global accountdict
    completionCode = "UNEXPECTED ERROR (pwmodule.Login)"

    if not GoodUsrID(userID):
        completionCode = "Invalid userID"
    elif AccountExists(userID):
        #print("(debugging) pwmodule.Login userID, pwd = ", userID, ", ", passwd)
        if pwcrypto.CheckPw(accountdict[userID.lower()], passwd):
            completionCode = "OK"
        else:
            completionCode = "Invalid credentials"

    return completionCode


# AddUsr
#
# Add a user account with a null password
def AddUsr(userID):
    global accountdict
    global accountschanged

    if not GoodUsrID(userID):
        completionCode = "Invalid userID"
    elif AccountExists(userID):
        completionCode = "Account already exists"
    else: # Create the new user account, with a null password
        completionCode = SetPassword(userID, '')
        if completionCode == "OK":
            accountschanged = True

    return completionCode


# DelUsr
#
# Delete a user account
def DelUsr(userID):
    global accountdict
    global accountschanged

    if not GoodUsrID(userID):
        completionCode = "Invalid userID"
    elif not AccountExists(userID):
        completionCode = "Account does not exist"
    else: # Delete the user and their password
        del accountdict[userID]
        accountschanged = True
        completionCode= "OK"

    return completionCode


# ListUsr
#
# Return a list of all user account names
def ListUsr():
    global accountdict

    return "OK", accountdict.keys()


