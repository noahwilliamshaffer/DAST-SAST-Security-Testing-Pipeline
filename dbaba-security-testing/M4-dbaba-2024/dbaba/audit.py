# audit.py
#
# Routines to manage the audit database
#

import abacfg
from datetime import datetime


# AuditSetup
#
# Open the audit file
def AuditSetup():
    global auditfile

    completionCode = "OK"

    try:
        auditfile = open(abacfg.AUDITDB, "a+")
    except Exception as e:
        completionCode = "UNEXPECTED ERROR (audit.AuditSetup): " + str(e)
        print("(debugging) ", completionCode)

    return completionCode


# AuditShutdown
#
# Close the audit file
def AuditShutdown():
    global auditfile

    completionCode = "OK"

    try:
        auditfile.close()
    except Exception as e:
        completionCode = "UNEXPECTED ERROR (audit.AuditShutdown): " + str(e)
        print("(debugging) ", completionCode)

    return completionCode


# AuditWrite
#
# Write an audit record
def AuditWrite(audittype, userID):
    global auditfile

    completionCode = "OK"

    presenttime = (datetime.now()).strftime("%c")
 
    if userID == '' or userID == None:
        userID = "(None)"

    # print("(debugging) AuditWrite: TYPE- ", audittype, "USERID- ", userID)

    try:
        auditfile.seek(0, 2) # Seek to the end of the audit file
    except Exception as e:
        completionCode = "UNEXPECTED ERROR (audit.AuditWrite): " + str(e)
        return completionCode

    try:
        auditfile.write(presenttime + "," + audittype + "," + userID + "\n")
        auditfile.flush()
    except Exception as e:
        completionCode = "UNEXPECTED ERROR (audit.AuditWrite): " + str(e)

    if completionCode != "OK":
        print("(debugging) ", completionCode)

    return completionCode

    
# AuditRead
#
# Read the audit log, all records or records for just one user
def AuditRead(usrID):
    global auditfile

    completionCode = "OK"

    recordList = []

    # print("{debugging} AuditRead(usrID): ", usrID)
    # print("{debugging} len(usrID): ", len(usrID))

    try:
        auditfile.seek(0) # Seek to beginning of audit file
    except Exception as e:
        completionCode = "UNEXPECTED ERROR (audit.AuditRead (seek)): " + str(e)
        return completionCode

    if usrID == '': # If no user ID is specified, read all
        recordList = auditfile.readlines()
    else: # Else read only records for the specified user ID
        for line in auditfile:
            recordfields = line.split(',')
            if recordfields[2].strip() == usrID:
                recordList.append(line)
            else: # It doesn't match, so skip it
                pass

    return completionCode, recordList



# AuditDelete
#
# Deletes all audit records
# Do you really want to do that? Perhaps when the audit log gets too full.
def AuditDelete():
    global auditfile

    completionCode = "OK"

    try:
        auditfile.truncate(0)
    except Exception as e:
        completionCode = "UNEXPECTED ERROR (audit.AuditDelete (truncate)): " + str(e)
        return completionCode

    try:
        auditfile.seek(0) # Seek to beginning of (now empty) audit file
    except Exception as e:
        completionCode = "UNEXPECTED ERROR (audit.AuditDelete (seek)): " + str(e)
        return completionCode

    return completionCode


