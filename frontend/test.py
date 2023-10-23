import Crypto
from Crypto.PublicKey import RSA
from Crypto import Random
import ast
from Crypto.Cipher import PKCS1_OAEP
import Crypto.IO.PKCS8

import bson
from bson.binary import Binary
from pymongo import MongoClient
import src.gmailAPI as gmail
global uri
uri = "mongoDBURL"
client = MongoClient(uri)

random_generator = Random.new().read
print(str(random_generator))
key = RSA.generate(1024, random_generator) #generate pub and priv key

publickey = key.publickey() # pub key export for exchange
encryptor = PKCS1_OAEP.new(publickey)
encrypted = encryptor.encrypt( str.encode('encrypt this message'))
#message to encrypt is in the above line 'encrypt this message'

# print('encrypted message:', encrypted) #ciphertext
f = open ('encryption.txt', 'w')
f.write(str(encrypted)) #write ciphertext to file
f.close()

#decrypted code below

f = open('encryption.txt', 'r')
message = f.read()

decryptor = PKCS1_OAEP.new(key)
decrypted = decryptor.decrypt(ast.literal_eval(str(encrypted)))

# print('decrypted', decrypted.decode("utf-8"))
print(publickey)
print(key)
f = open ('encryption.txt', 'w')
f.write(str(message))
f.write(str(decrypted))
f.close()
f = open('mykey.pem','wb')
print((key.export_key('PEM')))
f.write(key.export_key('PEM'))
f.close()
file_used = "mykey.pem"
with open("mykey.pem", "rb") as f:
    coded = f.read()
    print("type of coded: " , type(coded))
    encoded = Binary(coded)
print("encoded: ", str(encoded))
print("type of encoded: " , type(encoded))

client = MongoClient(uri)
db = client["lastwill"]
contract = db["contract"]
contract.insert_one({"filename": "test1", "file": (coded), "description": "test"})
pemKey = (contract.find_one({"filename": "test1"})["file"])
print("pemKey: ",(pemKey))
print("type of pemKey: " , type(pemKey))
key = RSA.importKey(pemKey)

print(PKCS1_OAEP.new(key).decrypt( ast.literal_eval( str(encrypted) ) ))
