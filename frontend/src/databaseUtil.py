from pymongo import MongoClient
import src.gmailAPI as gmail
global uri
import datetime
uri = "insert_your_own_mongoDBURL"
client = MongoClient(uri)
# db = client["lastwill"]
# account = db["account"]
# contract = db["contract"]


# All these functions will only be mainly used to interact with the mongdoDB
# database and will differ from function with similar names


def createAccountDB(email, password, username):
    response = ""
    try:
        client = MongoClient(uri)
        db = client["lastwill"]
        account = db["account"]
        if (account.find_one({"email": email}) == None):
            account.insert_one({"email": email, "password": password, "username": username, "activated": False})
            activationUrl = "http://localhost:8000/pages/activation.html?email=" + email
            print(activationUrl)
            response = "Created Account"
            gmail.sendEmail(email, activationUrl)

        # sendEmail(String(credentials.email), "Account Activation",  activationUrl)

        elif (account.find_one({"email": email}) != None):
            # to filter out error when sending email failed
            print("account with email already exist");
            response = "error";

        else:
            print("error");
            response = "error";

    finally:
        client.close()
        return response


def activateAccountDB(email):
    response = ""
    try:
        client = MongoClient(uri)
        db = client["lastwill"]
        account = db["account"]
        account.update_one({"email": email}, {"$set": {"activated": True}})
        response = "Activated Account"

        # sendEmail(String(credentials.email), "Account Activation",  activationUrl)

    except:
            print("error");
            response = "error";

    finally:
        client.close()
        return response


def checkAccountDB(email, password):
    response = None
    try:
        print("starting database")
        client = MongoClient(uri)
        db = client["lastwill"]
        account = db["account"]
        if (account.find_one({"email": email})["password"] == password):
            # location.replace("./pages/menu.html")
            if (account.find_one({"email": email})["activated"] == False):
                print("account not activated")
                response = False
            else:
                print("logging in")
                response = account.find_one({"email": email})["username"]

        else:
            print("error")
            response = False
    except:
        print("error")
        response = False


    finally:
        client.close()
        return response



def createContractDB(form):
    response = ""
    try:

        client = MongoClient(uri)
        db = client["lastwill"]
        contract = db["contract"]
        today = datetime.datetime.today().strftime(("%Y-%b-%d %H:%M:%S"))
        contract.insert_one({
            "contractAddress": form["contractAddress"],
            "contractName": form["contractName"],
            "surname": form["surname"],
            "firstname": form["firstname"],
            "email": form["email"],
            "expirationDate": form["expirationDate"],
            "lastLive": today,
            "frequency": form["frequency"],
            "recipents": form["recipents"],
            "contractFunds": 0.0
          })
        # for recipent in recipents:
        #     print(recipent)
        #     print(address)
        #     contract.update_one({"contractAddress": address}, {"$push": {"recipents": recipent}})
            # if have file then storeFileDB()
        response = "Contract Created"
    except Exception as e:
        print(e)
        response = "error"

    finally:
        client.close()
        return response




def storeFilesDB(files, address):
    response = ""
    try:
        client = MongoClient(uri)
        db = client["lastwill"]
        contract = db["contract"]
        for file in files:
            print(file)
            # file = {
            # "publicKey": file["publicKey",
            # "privateKey": file["privateKey",
            # "url": file["url"]
            # }
            if (file != None):
                print("not none")
                contract.update_one(
                    {"contractAddress": address, "recipents":{"$elemMatch":{"remail": file["remail"]}}},
                    {"$set": {"recipents.$.url": file["url"]}}
                )

                # print(contract.find_one({"recipents":{"$elemMatch":{"remail": file["remail"]}}}))
                print("file stored")
        response = "File(s) Stored"
    except Exception as e:
        print(e)
        response = "error"

    finally:
        client.close()
        return response

  # for (item in files) {

   # collection.modify(address).add(item.data)
   # element.innerhtml = contracts
  # }


def cancelContractDB(address):
    response = ""
    try:
        client = MongoClient(uri)
        db = client["lastwill"]
        contract = db["contract"]
        document = contract.delete_one({"contractAddress": address})
        response = "Contract Cancelled"
    except Exception as e:
        print(e)
        response = "error"

    finally:
        client.close()
        return response



def getAllContractSimpleDetailsDB(email):
    # collection.fetchAll(email).address&&contractName
    # element.innerhtml = contracts
    try:
        client = MongoClient(uri)
        db = client["lastwill"]
        contract = db["contract"]
        results = contract.find({"email": email})
        contracts = []
        for result in results:
            print(result)
            print(result["contractName"])
            print(result["contractAddress"])
            print(result["expirationDate"])
            print(str(datetime.datetime.fromtimestamp(result["frequency"])))
            print(result["contractFunds"])
            contracts.append([result["contractName"], result["contractAddress"],
            result["expirationDate"], str(datetime.datetime.fromtimestamp(result["frequency"])),
            result["contractFunds"]])

    # except:
    #     print("error")
    #     client.close()
    #     return "error"

    finally:
        client.close()
        print(contracts)
        return contracts



def getContractDetailsDB(address):
  # collection.fetchAll(email).details
  # element.innerhtml = contractDetails
    contracts = []
    try:
        client = MongoClient(uri)
        db = client["lastwill"]
        contract = db["contract"]
        result = contract.find_one({"contractAddress": address})
        #result = contract.find_one({"contractAddress": address, "recipents":{"$elemMatch":{"remail": remail}}})
                # print(result)
        #url = result["recipents"][0]
        print(result)
        #print(url["url"])
        contracts.append([result["contractName"], result["contractAddress"],
        result["expirationDate"], result["frequency"],
        result["contractFunds"]])
        print(contracts)

    except:
        print("error")
        client.close()
        return "error"

    finally:
        client.close()
        return contracts



def sendFundDB(address, amount):
    response = ""
    try:
        print("at sending fund")
        client = MongoClient(uri)
        db = client["lastwill"]
        contract = db["contract"]
        contractDestination = contract.find_one({"contractAddress": address})
        contract.update_one({"contractAddress": address}, {"$set": {"contractFunds": (contractDestination["contractFunds"] + amount)}})
        response = "Fund Sent"

    # except:
    #     print("error")
    #     response = "error"

    finally:
        client.close()
        return response

def confirmLive(address, nextLive):
    response = ""
    try:
        print("at checking in")
        client = MongoClient(uri)
        db = client["lastwill"]
        contract = db["contract"]
        contractDestination = contract.find_one({"contractAddress": address})
        contract.update_one({"contractAddress": address}, {"$set": {"lastLive": datetime.datetime.today().strftime(("%Y-%b-%d %H:%M:%S"))}})
        response = "confirmed Live status"

    except Exception as e:
        print(e)
        response = "error"

    finally:
        client.close()
        return response


def getFileURLs(address):
    files = []
    try:
        client = MongoClient(uri)
        db = client["lastwill"]
        contract = db["contract"]
        contract = contract.find_one({"contractAddress": address})
        for recipent in contract["recipents"]:

            files.append({
            "remail": recipent["remail"],
            "url": recipent["url"]})

    except:
        print("error")

    finally:
        client.close()
        return files

# createAccountDB("email", "password", "username")
# checkAccountDB("email", "password")
# createContractDB("form", "address", ["array1", "array2"])
# storeFileDB("pkey", "skey", "url", "address", "email")
# getAllContractSimpleDetailsDB("form.email.value")
# getContractDetailsDB("address")
# sendFundDB("address", 2)
# async def run():
#   try:
#     await
#     const database = client.db("lastwill")
#     const collection = database.collection("contract")
#
#
#     print("closed the change stream");
#    finally :
#     await client.close();
#     run().catch(console.dir);
