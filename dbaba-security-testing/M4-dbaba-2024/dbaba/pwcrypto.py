# pwcrypto.py
#
# Creates salted password hashes, using bcrypt_hash
# 
# 2024-08-22 Changed all instances of "from Crypto." to "from Cryptodome."
#


from base64 import b64encode
from Crypto.Hash import SHA256
#from Cryptodome.Hash import SHA256
from Crypto.Protocol.KDF import bcrypt
#from Cryptodome.Protocol.KDF import bcrypt
from Crypto.Protocol.KDF import bcrypt_check
#from Cryptodome.Protocol.KDF import bcrypt_check
# from Crypto.Random import get_random_bytes




# CreatePwHash
#
# Given a password, create a salted password hash
def CreatePwHash(pw):
    pwbytes = bytes(pw, 'utf-8') # Convert string to bytes
    b64pwd = b64encode(SHA256.new(pwbytes).digest()).decode('utf-8')

    bcrypt_hash = bcrypt(b64pwd, 12)

    return bcrypt_hash.decode('utf-8')



# CheckPw
#
# Given a password record and a password, check if the password matches
# Returns True if password matches the hash, False otherwise
def CheckPw(pwhash, pw):
    result = False

    pwbytes = bytes(pw, 'utf-8') # Convert string to bytes
    b64pwd = b64encode(SHA256.new(pwbytes).digest()).decode('utf-8')

    try:
        bcrypt_check(b64pwd, pwhash)
        result = True # If no exception, result is True
    except ValueError: # If ValueError, password does not match
        result = False 
    except Exception as e: # Something else bad happened
        print("UNEXPECTED ERROR: pwcrypto.py Decode - ", e)
        result = False

    return result




