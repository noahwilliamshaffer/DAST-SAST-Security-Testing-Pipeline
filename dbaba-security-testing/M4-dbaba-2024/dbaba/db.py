# db.py
# Database module for dbaba
#
# Stores record values as TEXT.
# Preserves uniqueness of records based on first two fields, 
#  but enforces no other value or integrity constraints.

import abacfg
import sqlite3


# Db_setup
#
# Establish connection to db, create the file and table if they don't exist

# Establish connection to database
def Db_setup():
    global connection
    global cursor

    completionCode = "OK"

    connection = sqlite3.connect(abacfg.DBFNAME)
    cursor = connection.cursor()

# Create the database table, if it doesn't already exist.
# Construct the table out of the DBFIELDS defined in abacfg

    Dbfields = ""
    for field in abacfg.DBFIELDS:
        Dbfields += field + " TEXT, "

#   print("Dbfields : ", Dbfields)

    SQLTableCreateString = f"CREATE TABLE if not exists {abacfg.DBTNAME} ({Dbfields} UNIQUE ({abacfg.DBFIELDS[0]}, {abacfg.DBFIELDS[1]}))"

#   print("\nSQLTableCreateString: ", SQLTableCreateString)

# Create the database if it doesn't already exist
    try:
         cursor.execute(SQLTableCreateString)

    except sqlite3.OperationalError as e:
        completionCode = ("\ndb.py Create table operational ERROR: ", e)

    except Exception as e:
        completionCode = ("\ndb.py Create Table other ERROR: ", e)

    return completionCode

# end Db_setup


# Db_shutdown
#   Close the connection the database, committing all changes
def Db_shutdown():
    global connection

    connection.commit()
    connection.close()

    return "OK"


# Db_emptyrecord
# 
# Returns a conveniently empty dictionary with all record fields in order
def Db_emptyrecord():
    return dict.fromkeys(abacfg.DBFIELDS, "") 



# Insert_record
#   Insert a record into the database
#   The input parameter is a complete list of values in the record
def Insert_record(recordvals):  
    global cursor

    completionCode = "OK"

    if len(recordvals) < len(abacfg.DBFIELDS): # If not a complete record
        completionCode = "db.py: Incomplete record passed to Insert_record"
    else:
        try:
             cursor.execute(f"INSERT INTO {abacfg.DBTNAME} VALUES {*recordvals,}")

        except Exception as e:
#            print("\ndb.py Insert ERROR: ", e)
            if "UNIQUE constraint failed" in str(e):
#                print("\ndb.py Caught a duplicate, setting error code")
                completionCode = "Duplicate recordID"
            else:
                completionCode = "db.py: Unknown error - " + str(e)

        if completionCode == "OK":
             connection.commit()

    return(completionCode)


# Delete_record
#   Delete records from the database where the 2 input parameters match
#   the first 2 fields of the record.
def Delete_record(uname, recordid):
    global cursor

    completionCode = "OK"

    try: # Find out first if any such records exist
        cursor.execute(f"SELECT * FROM {abacfg.DBTNAME} WHERE {abacfg.DBFIELDS[0]} = '{uname}' AND {abacfg.DBFIELDS[1]} = '{recordid}'")
        row =  cursor.fetchone()
        if row is None:
            completionCode = "RecordID not found"
            return(completionCode)

    except Exception as e:
        completionCode = "b.py Delete record (find): ", str(e)
        return(completionCode)

#    print(f"DELETE FROM {abacfg.DBTNAME} WHERE {abacfg.DBFIELDS[0]} = '{uname}' AND {abacfg.DBFIELDS[1]} = '{recordid}'")
    try:
         cursor.execute(f"DELETE FROM {abacfg.DBTNAME} WHERE {abacfg.DBFIELDS[0]} = '{uname}' AND {abacfg.DBFIELDS[1]} = '{recordid}'")

    except Exception as e:
#        print("\ndb.py Delete record ERROR: ", e)
        completionCode = "db.py: Unknown DELETE error - " + str(e)

    if completionCode == "OK":
         connection.commit()

    return(completionCode)


# Delete_all_records
#   Delete all records from the database where the input parameter matches
#   the first field of the record.
def Delete_all_records(uname):
    global cursor

    completionCode = "OK"

    try: # 
        cursor.execute(f"DELETE FROM {abacfg.DBTNAME} WHERE {abacfg.DBFIELDS[0]} = '{uname}'")
    except Exception as e:
        completionCode = "b.py Delete all records: ", str(e)

    if completionCode == "OK":
         connection.commit()

    return(completionCode)


# Read_record
#   Read and return records from the database where either
#   the input parameters match the first two fields of the record
#   (uname and recordid) or else, if the "recordID" parameter is '', read and return all records for the
#   uname.
#
#   Return the completion code and a list of tuples - one tuple for each record.
#
def Read_record(uname, recordid):
    global cursor

    completionCode = "OK"
    records = []

  
    try:
        if recordid == '':
            cursor.execute(f"SELECT * FROM {abacfg.DBTNAME} WHERE {abacfg.DBFIELDS[0]} = '{uname}'")
        else:
            cursor.execute(f"SELECT * FROM {abacfg.DBTNAME} WHERE {abacfg.DBFIELDS[0]} = '{uname}' AND {abacfg.DBFIELDS[1]} = '{recordid}'")
        records = cursor.fetchall()
        #print("\n(debugging) db.py Read_record records =  ", records)
    
        if records == []:
            completionCode = "No record found"

    except Exception as e:
        print("\ndb.py Read record ERROR - ", str(e))
        completionCode = "db.py: Read_record unknown SELECT error - " + str(e)

#    print ("(debugging) db.Read_record record: ", record)

#    print("(debugging) leaving db.Read_record, completionCode: ", completionCode)
    return(completionCode, records)



# end Code

