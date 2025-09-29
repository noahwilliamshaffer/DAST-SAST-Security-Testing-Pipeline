# abacfg.py
#
# Global definitions for aba program


# DATABASE RECORD FORMAT
# Define the fields in a database record
# "uname" and "recordid" must be present; the others can be changed
DBFIELDS = ("uname", "recordid", "sn", "gn", "pem", "wem", "pph", "wph", "sa", "city", "stp", "cty", "pc") # The list of field names, in order

# DATABASE FILE and TABLE Names
# If you change the format for the database, and if you are not starting
#   the database file from scratch, you must change the table name
#   at the same time or else there will be an operational error when the
#   program tries to insert a record that does not match the table format
DBFNAME = "dbadb-db"     # The database file name
DBTNAME = "AbaTable"         # The table name in the database file


# PASSWORD FILE
PWFILE = "abapwfile"


# AUDIT RECORD DATABASE
AUDITDB = "abaaudit" # The name of the audit file

# Define the audit record types
AUDITTYPES = ["LF", "LS", "L1", "LO", "SPC", "FPC", "AU", "DU"]





