# dbaba.py
#
# Entrypoint/main loop for dbaba program.
#
# 2024-08-22 Fixed re.search to use r" instead of just ', updated version to 0.3

import getpass
import re
import shlex
import os.path
import csv

import abacfg
import pwmodule
import db
import audit


VALIDCMDS = ('LIN', 'LOU', 'CHP', 'ADU', 'DEU', 'LSU', 'RAL', 'DAL', 'ADR', 'DER', 'EDR', 'RER', 'REA', 'IMD', 'EXD', 'HLP', 'EXT', 'WAI') 

VERSION = "Address Book Application, version 0.3"


# AbaStartup
#
# Do what needs to be done to get ready to run (open DB, passwords, etc.)
def AbaStartup():
    completion_code = db.Db_setup()
    if completion_code == "OK":
        completion_code =  audit.AuditSetup()
        if completion_code == "OK":
            completion_code = pwmodule.PwSetup()

    return completion_code


# aba_shutdown
#
# Close files, tie up loose ends, before exiting.
def aba_shutdown():
    db.Db_shutdown()
    audit.AuditShutdown()
    pwmodule.PwShutdown()

    return "OK"


# GoodRecordID
#   Check if the record_id meets spec
#   "16 characters maximum, upper- or lower-case letters, or numbers"
def GoodRecordID(record_id):

    if (len(record_id) > 0 and len(record_id) <= 16) and record_id.isalnum():
        return True
    else:
        return False



# StrongPassword
#
# Check if a proposed password satisfies strength requirements
# Return True if it does, False otherwise.
# Uses "Top 200 worst passwords of 2019"
#   from https://nordpass.com/blog/top-worst-passwords-2019/
def StrongPassword(pwd):

    badpwds = ('12345', '123456', '123456789', 'test1', 'password', '12345678', 'zinch', 'g_czechout', 'asdf', 'qwerty', '1234567890', '1234567', 'Aa123456.', 'iloveyou', '1234', 'abc123', '111111', '123123', 'dubsmash', 'test', 'princess', 'qwertyuiop', 'sunshine', 'BvtTest123', '11111', 'ashley', '00000', '000000', 'password1', 'monkey', 'livetest', '55555', 'soccer', 'charlie', 'asdfghjkl', '654321', 'family', 'michael', '123321', 'football', 'baseball', 'q1w2e3r4t5y6', 'nicole', 'jessica', 'purple', 'shadow', 'hannah', 'chocolate', 'michelle', 'daniel', 'maggie', 'qwerty123', 'hello', '112233', 'jordan', 'tigger', '666666', '987654321', 'superman', '12345678910', 'summer', '1q2w3e4r5t', 'fitness', 'bailey', 'zxcvbnm', 'fuckyou', '121212', 'buster', 'butterfly', 'dragon', 'jennifer', 'amanda', 'justin', 'cookie', 'basketball', 'shopping', 'pepper', 'joshua', 'hunter', 'ginger', 'matthew', 'abcd1234', 'taylor', 'samantha', 'whatever', 'andrew', '1qaz2wsx3edc', 'thomas', 'jasmine', 'animoto', 'madison', '0987654321', '54321', 'flower', 'Password', 'maria', 'babygirl', 'lovely', 'sophie', 'Chegg123', 'computer', 'qwe123', 'anthony', '1q2w3e4r', 'peanut', 'bubbles', 'asdasd', 'qwert', '1qaz2wsx', 'pakistan', '123qwe', 'liverpool', 'elizabeth', 'harley', 'chelsea', 'familia', 'yellow', 'william', 'george', '7777777', 'loveme', '123abc', 'letmein', 'oliver', 'batman', 'cheese', 'banana', 'testing', 'secret', 'angel', 'friends', 'jackson', 'aaaaaa', 'softball', 'chicken', 'lauren', 'andrea', 'welcome', 'asdfgh', 'robert', 'orange', 'Testing1', 'pokemon', '555555', 'melissa', 'morgan', '123123123', 'qazwsx', 'diamond', 'brandon', 'jesus', 'mickey', 'olivia', 'changeme', 'danielle', 'victoria', 'gabriel', '123456a', '0.00000000', 'loveyou', 'hockey', 'freedom', 'azerty', 'snoopy', 'skinny', 'myheritage', 'qwerty1', '159753', 'forever', 'iloveu', 'killer', 'joseph', 'master', 'mustang', 'hellokitty', 'school', 'Password1', 'patrick', 'blink182', 'tinkerbell', 'rainbow', 'nathan', 'cooper', 'onedirection', 'alexander', 'jordan23', 'lol123', 'jasper', 'junior', 'q1w2e3r4', '222222', '11111111', 'benjamin', 'jonathan', 'passw0rd', '0123456789', 'a123456', 'samsung', '123', 'love123', )


    result = False

    if (len(pwd) >= 1) and (len(pwd) <= 24) and (pwd.isalnum()) and (not pwd in badpwds):
        result = True

    return result





# print_help
#
# Print help information for using the program
def print_help():
    print("\n", VERSION, "\n")
    print("Valid commands: \n \
    login: LIN <userID> \n \
    logout: LOU \n \
    Change Password: CHP \n \
    Add Record: ADR <record_id> [<field1=value1> <field2=value2> ...] \n \
    Delete Record: DER <record_id> \n \
    Edit Record: EDR <record_id> <field1=value1> [<field2=value2> ...] \n \
    Read Record: RER <record_id> [<fieldname> ...] \n \
    Read All Records: REA [<fieldname> ...] \n \
    Import Database: IMD <Input_File> \n \
    Export Database: EXD <Output_file> \n \
    Help: HLP \n \
    Who Am I: WAI \n \
    Exit: EXT \n \
    \n \
Admin-only commands: \n \
    Add User: ADU <userID> \n \
    Delete User: DEU <userID> \n \
    List Users: LSU \n \
    Read Audit Log: RAL [<userID>] \n \
    Delete Audit Log: DAL [<userID>] \n")

    return "OK"


# GetCommand
#
# Read a command line, separate parameters on whitespace, handles quotes
def GetCommand():
    cmdlst = []
    cmdtxt = ''

    print("\n")
    try:
        cmdtxt = input("ABA> ")
    except Exception as e:
        aba_shutdown() # Clean up and close databases
        print("Exiting ...")

    try:
        cmdlst = shlex.split(cmdtxt)
        #print("(debugging) GetCommand line is: ", cmdlst)
    except Exception as e:
        print("Missing close-quote")


    return(cmdlst)




# create_new_password
#
# Create a new password when none exists (e.g., for first login)
def create_new_password(usr):

    completion_code = "UNEXPECTED ERROR (create_new_password)"

    print("Create a new password. \n \
Passwords may contain up to 24 upper- or lower-case letters or numbers.\n \
Choose an uncommon password that would be difficult to guess.")
    passwd = getpass.getpass(prompt="\nEnter new password: ")
    #print("(debugging change_password) The password is: ", passwd)
    passwd2 = getpass.getpass(prompt="Reenter the same password: ")
    if passwd2 != passwd:
        completion_code = "Passwords do not match"
    elif (not passwd2.isalnum()) or not (len(passwd) >= 1 and len(passwd)<= 24):
        completion_code = "Password must be 1-24 alphanumeric characters"
    elif not StrongPassword(passwd2):
        completion_code = "Password is too easy to guess"
    else:
        completion_code = pwmodule.SetPassword(usr, passwd)

    return completion_code



# login
#
# Lets a user log in
def login(cur_usr, params):
    new_usr = cur_usr
    completion_code = "UNEXPECTED ERROR (login)"
    first = False
    try_usr = ''

    if cur_usr != None: # An account is already active!
        completion_code = "An account is currently active; logout before proceeding"
    elif len(params) == 0: # Missing the userID or have extra params
        completion_code = "Missing parameter"
    elif not pwmodule.AccountExists(params[0]): # UserID doesn't exist
        completion_code = "Invalid credentials"
    else: # UserID exists; perform login process
        try_usr = params[0]
        if pwmodule.HasPassword(try_usr): # Password exists for account
            passwd = getpass.getpass(prompt="Enter your password: ")
            #print("(debugging login) The password is: ", passwd)
            completion_code = pwmodule.Login(try_usr, passwd)
            if completion_code == "OK": # login succeeded
                #print("(debugging login) login succeeded.")
                new_usr = params[-1]
            else: 
                pass
                #print("(debugging login) Failed login.")
        else: # First login; initial password is '': need to create a new password
            first == True
            completion_code = create_new_password(try_usr)
            if completion_code == "OK":
                new_usr = try_usr
            #print("(debugging) Result from create_new_password: ", completion_code)

    if completion_code == "OK":
        audit.AuditWrite("LS", new_usr)
        if first == True:
            audit.AuditWrite("L1", new_usr)
    else:
        audit.AuditWrite("LF", try_usr)

    return completion_code, new_usr



# change_password
#
# A user can change their password
def change_password(cur_usr):
    completion_code = "UNEXPECTED ERROR (change_password)"

    if cur_usr is None:
        completion_code = "No active login session"
    elif not pwmodule.AccountExists(cur_usr): # UserID doesn't exist
        completion_code = "Invalid credentials"
    else: 
        completion_code = create_new_password(cur_usr)

    if completion_code == "OK":
        audit.AuditWrite("SPC", cur_usr)
    else:
        audit.AuditWrite("FPC", cur_usr)

    return completion_code




# logout
#
# Logs out the current user
def logout(cur_usr):
    new_usr = None
    completion_code = "OK"
    if cur_usr is None:
        completion_code = "No active login session"
    else: # do logout stuff
        new_usr = None

    if completion_code == "OK":
        audit.AuditWrite("LO", cur_usr)

    return completion_code, new_usr


# add_usr
#
# Allows admin to add a new user account
def add_usr(cur_usr, params):
    completion_code = "UNEXPECTED ERROR (add_usr)"

    if cur_usr is None:
        completion_code = "No active login session"
    elif cur_usr != "admin":
        completion_code = "Admin not active"
    elif len(params) != 1: # Missing the userID or have extra params
        completion_code = "Missing or extra parameters"
    else:
        completion_code = pwmodule.AddUsr(params[0])

    if completion_code == "OK":
        audit.AuditWrite("AU", params[0])

    return completion_code




def del_usr(cur_usr, params):
    completion_code = "UNEXPECTED ERROR (del_usr)"

    if cur_usr is None:
        completion_code = "No active login session"
    elif cur_usr != "admin":
        completion_code = "Admin not active"
    elif len(params) != 1: # Missing the userID or have extra params
        completion_code = "Missing or extra parameters"
    else:
        completion_code = pwmodule.DelUsr(params[0])
        if completion_code == "OK": # Now delete all of the users reccords
            completion_code = db.Delete_all_records(params[0])

    if completion_code == "OK":
        audit.AuditWrite("DU", params[0])

    return completion_code


def list_usr(cur_usr):
    completion_code = "UNEXPECTED ERROR (list_usr)"
    usr_list = [] 

    if cur_usr is None:
        completion_code = "No active login session"
    elif cur_usr != "admin":
        completion_code = "Admin not active"
    else:
        completion_code, usr_list = pwmodule.ListUsr()

    return completion_code, usr_list


# read_audit_log
#
# Admin can list contents of audit log, entire or just one user
def read_audit_log(cur_usr, params):
    completion_code = "UNEXPECTED ERROR (read_audit_log)"

    auditrecords = []
    targetUsr = ''

    if cur_usr is None:
        completion_code = "No active login session"
    elif cur_usr != "admin":
        completion_code = "Admin not active"
    elif len(params) > 1: # Extra params
        completion_code = "Missing or extra parameters"
    else: # If a target specified, read just those records; else read all
        if len(params) == 1:
            targetUsr = params[0]
        completion_code, auditrecords = audit.AuditRead(targetUsr)

    return completion_code, auditrecords


# delete_audit_log
#
# Admin can delete the entire audit log
def delete_audit_log(cur_usr):
    if cur_usr is None:
        completion_code = "No active login session"
    elif cur_usr != "admin":
        completion_code = "Admin not active"
    else:
        completion_code = audit.AuditDelete()
    
    return completion_code




def add_record(cur_usr, params):
    completion_code = "UNEXPECTED ERROR (add_record)"
    tmpparamdict = db.Db_emptyrecord()
    record_id = ''

    #print("(debugging) In add_record ", cur_usr, ", ", params)
    #print("(debugging) In add_record initial tmpparamdict ", tmpparamdict)

    if cur_usr is None:
        completion_code = "No active login session"
    elif cur_usr == "admin":
        completion_code = "Admin not authorized"
    elif len(params) < 1:
        completion_code = "No record_id"
    elif not GoodRecordID(params[0]):
        completion_code = "Invalid record_id"
    else:
        record_id = params.pop(0)
        #print("(debugging) Have record ID; remaining params", params)
        # Check that each parameter has the correct form <string>=<string>
        if len(params) > 0: # If there are values to process...
            for param in params:
                if not re.search(r"\w+=[^\S]*", param): # A parameter has wrong form
                    completion_code = "One or more invalid record data fields"
                    #print("(debugging) add_record bad parameter: ", param)
                    break
                else: # Continue checking if valid field=value
                    tmplist = param.split("=", 1)
                    tmpparamdict[tmplist[0].lower()] = str(tmplist[1])
                    #print("(debugging) add_record tmpparamdict ", tmpparamdict)
                    # Make sure that the uname and recordid are not being changed
                    if (str(tmpparamdict[abacfg.DBFIELDS[0]]) != '') or (str(tmpparamdict[abacfg.DBFIELDS[1]]) != ''):
                        completion_code = "One or more invalid record data fields"
                        #print("(debugging) add_record checking uname and recordid, tmpparamdict = ", tmpparamdict)
                    else:
                        completion_code = "OK"
        else: # No values to set, so OK
            completion_code = "OK" # OK for now, assuming all params are good


    #print("(debugging) add_record after processing params tmpparamdict ", tmpparamdict)

    if completion_code == "OK": # If all OK so far...
        if (not (set(tmpparamdict.keys()) <= set(abacfg.DBFIELDS))):
            # If keys in tmpparamdict are not a subset of total set of fields
            # then one or more a fields are invalid
            completion_code = "One or more invalid record data fields"
            #print("(debugging) add_record illegal key ", tmpparamdict)
        else: # Everything looks good; create a record to store in database
            # First, create the complete record
            tmpparamdict[abacfg.DBFIELDS[0]] = cur_usr
            tmpparamdict[abacfg.DBFIELDS[1]] = record_id
            # Call db.Insert_record. It will return an "already exists error"
            #   if (cur_usr, record_id) duplicates an existing entry
            completion_code = db.Insert_record(list(tmpparamdict.values()))
            #print("(debugging) add_record CompletionCode", completion_code)
    else:
        pass
        #print("(debugging) add_record final tmpparamdict ", tmpparamdict)
        #print("(debugging) add_record CompletionCode", completion_code)



    return completion_code

        


# del_record
#
# Delete a record specified by (cur_usr, record_id)
def del_record(cur_usr, params):
    completion_code = "UNEXPECTED ERROR (del_record)"

    #print("(debugging) In del_record ", cur_usr, ", ", params)

    if cur_usr is None:
        completion_code = "No active login session"
    elif cur_usr == "admin":
        completion_code = "Admin not authorized"
    elif len(params) < 1:
        completion_code = "No record_id"
    elif not GoodRecordID(params[0]):
        completion_code = "Invalid record_id"
    else:
        record_id = params.pop(0)
        #print("(debugging) del_record cur_usr record_id", cur_usr, ", ", record_id)
        completion_code = db.Delete_record(cur_usr, record_id)

    return completion_code



# edt_record
#
# Make changes to an existing record, if it exists.
def edt_record(cur_usr, params):
    completion_code = "UNEXPECTED ERROR (edt_record)"
    emptyparamdict = db.Db_emptyrecord()
    tmpparamdict = db.Db_emptyrecord()
    tmprecordlist = []
    tmprecorddict = db.Db_emptyrecord()
    record_id = ''

    #print("(debugging) In edt_record ", cur_usr, ", ", params)
# First, check that there is a current user, not the admin, and a valid record ID
    if cur_usr is None:
        completion_code = "No active login session"
    elif cur_usr == "admin":
        completion_code = "Admin not authorized"
    elif len(params) < 1:
        completion_code = "No record_id"
    elif not GoodRecordID(params[0]):
        completion_code = "Invalid record_id"
    else:
# Now check that all of the parameters (the fields to change) are valid
        record_id = params.pop(0)
        #print("(debugging) Have record ID; remaining params", params)
        # Check that each parameter has the correct form <string>=<string>
        if len(params) > 0: # If there are values to process...
            for param in params:
                if not re.search(r"\w+=[^\S]*", param): # A parameter has wrong form
                    completion_code = "One or more invalid record data fields"
                    #print("(debugging) add_record bad parameter: ", param)
                    break
                else: # Continue checking if valid field=value
                    tmplist = param.split("=", 1)
                    tmpparamdict[tmplist[0].lower()] = str(tmplist[1])
                    #print("(debugging) edt_record tmpparamdict ", tmpparamdict)
                    # Make sure that the uname and recordid are not being changed
                    if (str(tmpparamdict[abacfg.DBFIELDS[0]]) != '') or (str(tmpparamdict[abacfg.DBFIELDS[1]]) != ''):
                        completion_code = "One or more invalid record data fields"
                        #print("(debugging) edt_record checking uname and recordid, tmpparamdict = ", tmpparamdict)
                    else:
                        completion_code = "OK"
        else: # No values to set, so OK
            completion_code = "OK" # OK for now, given no params


    if completion_code == "OK": # If all OK so far...
        if (not (set(tmpparamdict.keys()) <= set(abacfg.DBFIELDS))):
            # If keys in tmpparamdict are not a subset of total set of fields
            # then one or more fields are invalid
            completion_code = "Invalid fieldname(s)"
            #print("(debugging) edt_record illegal key ", tmpparamdict)
        else: # Everything looks good; create a complete record
            tmpparamdict[abacfg.DBFIELDS[0]] = cur_usr
            tmpparamdict[abacfg.DBFIELDS[1]] = record_id
# At this point, we know all parameters are valid.
# Now read in the original record. We already know it exists.
            completion_code, tmprecordlist = db.Read_record(cur_usr, record_id) # Returns list of tuples
            #print("(debugging) edt_record result of db.Read_record: ", completion_code)
            if completion_code == "OK": # If the read succeeds
                # There should be exactly one record in the dictionary because we are using
                #   a record_id, which must be unique for that user.
                if len(tmprecordlist) != 1: # This should never happen
                    completion_code == "UNEXPECTED edt_record ERROR: Read returned != 1 records" 
                else: 
                # Create a temporary record dictionary of the returned record
                    # Copy the record values from the record to the dictionary
                    for i in range(0, len(abacfg.DBFIELDS)): 
                        tmprecorddict[abacfg.DBFIELDS[i]] = str(tmprecordlist[0][i])
                    #print("(debugging) edt_record tmprecordict: ", tmprecorddict)
# Copy the new values to the record
                    for i in range(2, len(abacfg.DBFIELDS)):
                        if tmpparamdict[abacfg.DBFIELDS[i]] != '': 
                            tmprecorddict[abacfg.DBFIELDS[i]] = tmpparamdict[abacfg.DBFIELDS[i]]
# Delete the old record and save the edited record
# (This is easier than trying to directly update the existing record
# and makes use of the existing Delete and Add record functions.)
                    completion_code = db.Delete_record(cur_usr, record_id)
                    if completion_code == "OK":
                        completion_code == db.Insert_record(list(tmprecorddict.values()))
                    else: # This should never happen!
                        completion_code == "UNEXPECTED ERROR (edt_record) deleting old record = " + completion_code


    return completion_code




# rd_record
#
# Read a database record for the current user for specified fields.
# If no fields specified, read all fields.
def rd_record(cur_usr, params):
    completion_code = "UNEXPECTED ERROR (rd_record)"
    emptyparamdict = db.Db_emptyrecord()
    tmprecorddict = {}
    tmprecordlist = []
    requestedfields = []
    record_id = '' # Default value '' for record_id => all records

    returnvaluelist = []

    #print("(debugging) In rd_record ", cur_usr, ", ", params)

    if cur_usr is None:
        completion_code = "No active login session"
    elif cur_usr == "admin":
        completion_code = "Admin not authorized"
    elif (len(params) == 0) or (not GoodRecordID(params[0])):
        completion_code = "Invalid record_id"
    else: # There must be a record id
        record_id = params.pop(0)
        #print("(debugging) rd_record cur_usr record_id", cur_usr, ", ", record_id)
        # Are all of the field names in the param list valid?
        # First convert all to lower case
        params = [x.lower() for x in params]
        # Check that all params are valid field names, but not "uname" or "recordid"
        if (not (set(params) <= set(abacfg.DBFIELDS))) or (abacfg.DBFIELDS[0] in params) or (abacfg.DBFIELDS[1] in params):
            completion_code = "Invalid fieldname(s)"
        else: # All params are valid field names, read the record or records
            completion_code, tmprecordlist = db.Read_record(cur_usr, record_id) # Returns list of tuples
            #print("(debugging) rd_record result of db.Read_record: ", completion_code)
            if completion_code == "OK": # If the read succeeds
                # Create a temporary record dictionary of dictionaries of the returned records
                # with record_ids as first level keys and field names as second level keys
                for rec in tmprecordlist:
                    # Skip the userID in the first field. Use the record_id in the second as key
                    tmprecorddict[rec[1]] = emptyparamdict.copy() # Initialize all values to ''
                    # Copy the record values from the record to the dictionary
                    for i in range(2, len(abacfg.DBFIELDS)): 
                        tmprecorddict[rec[1]][abacfg.DBFIELDS[i]] = str(rec[i])
                #print("(debugging) rd_record tmprecordict: ", tmprecorddict)
                # Now all record tuples are copied into the nested dictionary
                # Select only the requested fields
                if len(params) > 0:  # Use only the selected fields
                    requestedfields = params.copy()
                else: # Use all of the fields (except the first two)
                    requestedfields = list(abacfg.DBFIELDS)[2::] # Copy all except first two
                for keyrecid in tmprecorddict: # For each record
                    tmprecstring = str(keyrecid)
                    for field in requestedfields: # For each of the requested fields
                    #   add <field>=<value> to the return string for that record
                        tmprecstring += f', {str(field)}={str(tmprecorddict[keyrecid][field])}'
                    tmprecstring += "\n"
                    #print("(debugging) rd_record tmprecstring = ", tmprecstring)
                    # Add the tmprecstring for that record to the return list
                    returnvaluelist += [tmprecstring]


    #print("(debugging) rd_record returnvaluelist: ", returnvaluelist)
    return completion_code, returnvaluelist


# read_all_record
#
# Read all database record for the current user for specified fields.
# If no fields specified, read all fields.
def read_all_record(cur_usr, params):
    completion_code = "UNEXPECTED ERROR (rd_record)"
    emptyparamdict = db.Db_emptyrecord()
    tmprecorddict = {}
    tmprecordlist = []
    requestedfields = []
    record_id = '' # Default value '' for record_id => all records

    returnvaluelist = []

    #print("(debugging) In read_all_record ", cur_usr, ", ", params)

    if cur_usr is None:
        completion_code = "No active login session"
    elif cur_usr == "admin":
        completion_code = "Admin not authorized"
    else: # No record_id for read all. All params, if any exist, are field names
        # Are all of the field names in the param list valid?
        # First convert all to lower case
        params = [x.lower() for x in params]
        # Check that all params are valid field names, but not "uname" or "recordid"
        if (not (set(params) <= set(abacfg.DBFIELDS))) or (abacfg.DBFIELDS[0] in params) or (abacfg.DBFIELDS[1] in params):
            completion_code = "Invalid fieldname(s)"
        else: # All params are valid field names, read the record or records
            completion_code, tmprecordlist = db.Read_record(cur_usr, record_id) # Returns list of tuples
            #print("(debugging) read_all_record result of db.Read_record: ", completion_code)
            if completion_code == "OK": # If the read succeeds
                # Create a temporary record dictionary of dictionaries of the returned records
                # with record_ids as first level keys and field names as second level keys
                for rec in tmprecordlist:
                    # Skip the userID in the first field. Use the record_id in the second as key
                    tmprecorddict[rec[1]] = emptyparamdict.copy() # Initialize all values to ''
                    # Copy the record values from the record to the dictionary
                    for i in range(2, len(abacfg.DBFIELDS)): 
                        tmprecorddict[rec[1]][abacfg.DBFIELDS[i]] = str(rec[i])
 #               #print("(debugging) read_all_record tmprecorddict: ", tmprecorddict)
                # Now all record tuples are copied into the nested dictionary
                # Select only the requested fields
                if len(params) > 0:  # Use only the selected fields
                    requestedfields = params.copy()
                else: # Use all of the fields (except the first two)
                    requestedfields = list(abacfg.DBFIELDS)[2::] # Copy all except first two
                for keyrecid in tmprecorddict: # For each record
                    tmprecstring = str(keyrecid)
                    for field in requestedfields: # For each of the requested fields
                    #   add <field>=<value> to the return string for that record
                        tmprecstring += f', {str(field)}={str(tmprecorddict[keyrecid][field])}'
                    tmprecstring += "\n"
                    #print("(debugging) read_all_record tmprecstring = ", tmprecstring)
                    # Add the tmprecstring for that record to the return list
                    returnvaluelist += [tmprecstring]


    #print("(debugging) read_all_record returnvaluelist: ", returnvaluelist)
    return completion_code, returnvaluelist



# imp_db
#
# Import database records from the specified file
# Imported records must be in CSV format, with len(abacfg.DBFIELDS)-1 fields
#   and the first value a valid record_id.
# Imported records replace existing records if they have the same record_id
#
def imp_db(cur_usr, params):

    fname = ''
    imprecordlines = []
    completion_code = "UNEXPECTED ERROR: imp_db"
    tmprecordlist = []

    if cur_usr is None:
        completion_code = "No active login session"
    elif cur_usr == "admin":
        completion_code = "Admin not authorized"
    elif len(params) == 0:
        completion_code = "No input file specified"
    elif not os.path.exists(params[0]): # There is a file name parameter; does the file exist?
        completion_code = "File doesn't exist"
    else: # File exists, try to open it
        fname = params.pop(0)
        try:
            impfile = open(fname, "r")
            completion_code = "OK"
            #print("(debugging) imp_db file open succeded")
        except Exception as e:
            completion_code = "Can't open file " + str(e)
            #print("(debugging) ", completion_code)

    if completion_code == "OK": # The input DB file is open; read the records
#        imprecordlines = impfile.readlines()
        imprecordlines = csv.reader(impfile) # Automatically splits on commas into list 

        # Check each line to make sure they are in the proper format
        # with a valid record_id as the first of a CSV line
        for line in imprecordlines:
            if len(line) == 0: # Skip empty lines
                continue
            else: # Check for valid record_id
#                tmplist = line.split(",")
                tmplist = line
                #print("(debugging) imp_db line = ", tmplist)
                if len(tmplist) != (len(abacfg.DBFIELDS) - 1): # Skip uname, but need all other fields
                    completion_code = "Incomplete record or invalid format in import database"
                elif not GoodRecordID(tmplist[0]):
                    #print("(debugging) imp_db record_id = ", tmplist[0])
                    completion_code = "Invalid record ID"
                else: # Record looks good
                    record_id = tmplist[0]
                    tmplist.insert(0, str(cur_usr)) # Insert the current user first
                    # Check if the record already exists
                    # db.Read_record returns a list of tuples, but will only be 1 tuple
                    rdcompletion_code, tmprecordlist = db.Read_record(cur_usr, record_id) 
                    if (rdcompletion_code != "OK") and (rdcompletion_code != "No record found"):
                        # Unknown error, so bail out
                        completion_code == "UNEXPECTED ERROR (imp_db) reading record " + rdcompletion_code
                        break
                    else:
                        # If a record with that record_id already exists, delete it
                        if rdcompletion_code == "OK": # Record exists
                            decompletion_code = db.Delete_record(cur_usr, record_id)
                            if decompletion_code != "OK":
                                # Unknown error, so bail out
                                completion_code == "UNEXPECTED ERROR (imp_db) deleting record " + decompletion_code
                                break
                        # Write the record
                        #print("(debugging) imp_db writing this record: ", tmplist)
                        incompletion_code = db.Insert_record(tmplist)
                        if incompletion_code != "OK": # This should never happen
                            completion_code == "UNEXPECTED ERROR (imp_db) writing record " + incompletion_code

        impfile.close()
    else: # Never opened the file
        pass

    return completion_code



# exp_db
#
# Export all of the records for a user to the specified file
# Won't overwrite an existing file
#
def exp_db(cur_usr, params):

    fname = ''
    completion_code = "UNEXPECTED ERROR: exp_db"
    tmprecordlist = []

    if cur_usr is None:
        completion_code = "No active login session"
    elif cur_usr == "admin":
        completion_code = "Admin not authorized"
    elif len(params) == 0:
        completion_code = "No output file specified"
    elif os.path.exists(params[0]): # There is a file name parameter; does the file exist?
        completion_code = "File already exists"
    else: # File doesn't already exist
        fname = params.pop(0)
        completion_code = "OK" # OK, so far

    if completion_code  == "OK": # Try to open the file
        try:
            outfile = open(fname, "w+")
        except Exception as e:
            completion_code = "Can't open output file " + str(e)
        if completion_code == "OK": # The output DB file is open; write the records
            completion_code, tmprecordlist = db.Read_record(cur_usr, '') # Returns list of tuples
            #print("(debugging exp_db) result of db.Read_record: ", completion_code)
            if completion_code == "OK": # If the read succeeds
                # Write each record to the output file in CSV format
                for rec in tmprecordlist:
                    reclist = list(rec)
                    discard = reclist.pop(0) # Remove the uname
                    tmprecline = [str(element) for element in reclist]
                    tmprecline = ",".join(tmprecline)
                    tmprecline += "\n"
                    #print("(debugging exp_db) tmprecline = ", tmprecline)
                    try:
                        outfile.write(tmprecline)
                        #print("(debugging exp_db) wrote tmprecline")
                    except Exception as e:
                        completion_code = "Can't write to output file " + str(e)
                        break

            outfile.close()
            #print("(debugging exp_db) output file closed")
        else: # The file is not open
            pass
    
    return completion_code




# main
#
# The main command and control loop.
def main():
    print('\n', VERSION, '. Type "HLP" for a list of commands.')
    completion_code = AbaStartup() # Set up access to databases
    if completion_code != "OK":
        print("UNEXPECTED STARTUP ERROR: ", completion_code)
        completion_code = aba_shutdown() # Try to shutdown cleanly
        quit()


    cur_usr = None # Initially, no one is logged in
    completion_code = None 

    while True: #loop until EXIT command
        comline = GetCommand()
        if len(comline) == 0:
            continue # Nothing to process if empty command line
        #print("(debugging main) cur_usr: ", cur_usr)
        com = str(comline[0]).upper()
        #print("(debugging main) Com: ", com)
        del comline[0]
        params = comline
        #print("(debugging main) Params: ", params)
        if (com in VALIDCMDS):
            if (com == 'HLP'):
                completion_code = print_help()
            elif (com == 'EXT'):
                completion_code = aba_shutdown()
                print(completion_code)
                print("Exiting ...")
                quit()
            elif (com == 'LIN'):
                completion_code, new_usr = login(cur_usr, params)
                print(completion_code)
                if completion_code == "OK": # If login succeeded, new user
                    cur_usr = new_usr
            elif (com == 'LOU'):
                completion_code, new_usr = logout(cur_usr)
                print(completion_code)
                if completion_code == "OK":
                    cur_usr = new_usr
            elif (com == 'CHP'):
                completion_code = change_password(cur_usr)
                print(completion_code)
            elif (com == 'ADU'):
                completion_code = add_usr(cur_usr, params)
                print(completion_code)
            elif (com == 'DEU'):
                completion_code = del_usr(cur_usr, params)
                print(completion_code)
            elif (com == 'LSU'):
                completion_code, usr_list = list_usr(cur_usr)
                print(completion_code)
                if completion_code == "OK":
                    print(*usr_list, sep = "\n")
            elif (com == 'RAL'):
                completion_code, auditlist = read_audit_log(cur_usr, params)
                print(completion_code)
                if completion_code == "OK":
                    print(*auditlist)
                    # print(*auditlist, sep = "\n")
            elif (com == 'DAL'):
                completion_code = delete_audit_log(cur_usr)
                print(completion_code)
            elif (com == 'ADR'):
                completion_code = add_record(cur_usr, params)
                print(completion_code)
            elif (com == 'DER'):
                completion_code = del_record(cur_usr, params)
                print(completion_code)
            elif (com == 'EDR'):
                completion_code = edt_record(cur_usr, params)
            elif (com == 'RER'):
                completion_code, fieldlist = rd_record(cur_usr, params)
                print(completion_code)
                if completion_code == "OK":
                    print(*fieldlist, sep = "")
            elif (com == 'REA'):
                completion_code, fieldlist = read_all_record(cur_usr, params)
                print(completion_code)
                if completion_code == "OK":
                    print(*fieldlist, sep = "")
            elif (com == 'IMD'):
                completion_code = imp_db(cur_usr, params)
                print(completion_code)
            elif (com == 'EXD'):
                completion_code = exp_db(cur_usr, params)
                print(completion_code)
            elif (com == "WAI"):
                print("Current user is ", cur_usr)
                completion_code = "OK"
            else:
                print("(debugging main) Unknown command is: ", com)
                print("(debugging main) Parameters are: ", params)
        else:
            print("Unrecognized command")
            completion_code = "Unrecognized command"

#        print("(debugging) CompletionCode: ", completion_code)
#        print("(debugging main) cur_usr: ", cur_usr)



     
# Start execution here, to catch keyboard interrupts    
try:
    main()

except KeyboardInterrupt as e:
    print(" Interrupted. Exiting ...")
    aba_shutdown()
    quit()
    
    
