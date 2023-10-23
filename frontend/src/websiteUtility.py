import apscheduler as scheduler
from apscheduler.schedulers.background import BackgroundScheduler
from time import sleep
import datetime
from pymongo import MongoClient
import web3
from src import databaseUtil as DButi
import json
import itertools
from src import gmailAPI as gmail
from src import lastwilldata
from threading import Thread
"""
when a contract is created it will activate schedulecontractDeadlines function to schedule 2 deadlines
same as when the server starts up

when confirm live is clicked, it will activate confirm live

when confirm live is confirmed by the smart contract, then it will schedule checkLive for the next inspection
of ending the contract early, unless another confirm live is confirmed
"""
def confirmLive(contractAddress):
    web3 = getWeb3()
    contract = web3.eth.contract(address=contractAddress, abi=abi)
    pastLive = contract.functions.isPastLive().call()
    client = MongoClient(DButi.uri)
    db = client["lastwill"]
    contrac = db["contract"]
    document = contrac.find_one({"contractAddress": contractAddress})
    NextLiveFrequency = document["frequency"]
    print("checking live")
    print(pastLive)
    if (pastLive):
        deadLine(contractAddress)
    else:
        contract.functions.confirmLive().call()
        nextLive = getTimestamp(datetime.datetime.today()) + float(NextLiveFrequency)
        DButi.confirmLive(contractAddress, nextLive)
        scheduler.reschedule_job("Live"+contractAddress, trigger='interval', seconds=NextLiveFrequency)
        print("confirming live")
        job = scheduler.get_jobs()
        for i in job:
            print("name: %s, trigger: %s, handler: %s" % (
                i.id, i.trigger, i.func))
# reschedule next live time after receiving smart contract event confirmation

def checkLive(contractAddress):
    print("checking Live")
    web3 = getWeb3()
    contract = web3.eth.contract(address=contractAddress, abi=abi)
    pastLive = contract.functions.isPastLive().call()
    print(pastLive)
    if (pastLive):
        deadLine(contractAddress)
    print("checking live")
    # reschedule for next live inspection, might not need the if or is pastlive, depending on whether
    # solidity will have accurate time, or just only increment by mined time
    # if solidity don't have accurate time then schedules will be entirely dependent on server
    # therefore smart contract won't need checking date functions, but just operations of when dates are reached

def deadLine(contractAddress):
    """
    this function will call the contract function deadline, and this will end the contract, since deadline is reached
    """
    """
    as a temporary fix, this function will be used as the main function for when contact ends
    """
    # web3 = getWeb3()
    # contract = web3.eth.contract(address=contractAddress, abi=abi)
    # contract.functions.deadLine().call()
    cancelContractSchedules(contractAddress)
    files = DButi.getFileURLs(contractAddress)
    for file in files:
        print(file)
        gmail.sendEmail(file["remail"], file["url"])
    # DButi.cancelContractDB(event["address"])
    print("event  deadline reached") # for both live deadline and contract dealine

def scheduleContractDeadlines(contractAddress, deadline, frequency):

    scheduler.add_job(deadLine, "interval", [contractAddress], seconds=deadline, id=contractAddress)
    scheduler.add_job(checkLive, "interval", [contractAddress], seconds=frequency, id="Live"+contractAddress)
    # scheduler.start()
    print("scheduling deadline")
#cancel live function for that address, but also have a function in contract to disable the live function and contract
# if confirmed then perform smart contract action, if not then send money back and disable contract
def cancelLiveSchedule(contractAddress):

    scheduler.remove_job("Live"+contractAddress)

    print("cancelling live schedule")
 # def __get_jobs(self, name):
#        return [job for job in self.scheduler.get_jobs() if job.name == name AND job.subname == subname] this line to get the job

def cancelContractSchedules(contractAddress):

    try:
    # job1 = scheduler.get_job(contractAddress)
    # job1.remove()
        scheduler.remove_job(contractAddress)
        scheduler.remove_job("Live"+contractAddress)
    except Exception as e:
        print(e)

    print("cancelling contract schedules")

def getWeb3():
    w3 = web3.Web3(web3.Web3.HTTPProvider("http://localhost:7545"))
    return w3

def processEvent(event):
    if (event["event"] == "CheckIn"):
        print("event is confirmed live")
        scheduler.remove_job("Live"+event["address"])
        scheduler.add_job(checkLive, "interval", [event["address"]], seconds=event["args"]["nextLive"], id="Live"+event["address"])
        scheduler.start()
    elif (event["event"] == "DeadlineConfirmed"):
        print("cancelling contract")
        # cancelContractSchedules(event["address"])
        files = DButi.getFileURLs(event["address"])
        for file in files:
            print(file)
            gmail.sendEmail(file["remail"], file["url"])
        # DButi.cancelContractDB(event["address"])
        print("event  deadline reached") # for both live deadline and contract dealine
    elif (event["event"] == "FundReceived"):
        print("money received")
        print(event["args"]["funds"]/(10**18))
        DButi.sendFundDB(event["address"], float((event["args"]["funds"]/(10**18))))

    else:
        print("other event or error")

def rescheduleEvents():
    # fetch from database and schedule all existing jobs
    client = MongoClient(DButi.uri)
    db = client["lastwill"]
    contract = db["contract"]
    contracts = contract.find()
    global scheduler
    scheduler = BackgroundScheduler()
    global threads
    threads = list()
    for document in contracts:
        print(document["contractAddress"])
        address = document["contractAddress"]
        # nextLive = int(document["lastLive"]) + int(document["liveInterval"])
        today = getTimestamp(datetime.datetime.today())
        lastLive = getTimestamp(getDatetime(document["lastLive"]))
        nextLive = (lastLive + document["frequency"]) - today
        if (nextLive < 0):
            checkLive(address)
        # deadline = int(document["deadLine"])
        deadline = getTimestamp(datetime.datetime.strptime(document["expirationDate"], "%Y-%m-%d"))


        if (today > deadline):
            deadLine(address)
            print("hi")
        else:
            scheduler.add_job(deadLine, "interval", [address], seconds=deadline-today, id=address)
            scheduler.add_job(checkLive, "interval", [address], seconds=nextLive, id="Live"+address)

        thread = Thread(target=listenToEvent, args=(address,))
        threads.append(thread)
        thread.start()

    scheduler.start()
    for job in scheduler.get_jobs():
        print("name: %s, trigger: %s, handler: %s" % (
          job.id, job.trigger, job.func))

def listenToEvent(contractAddress):
    print("listening to event with address") # not needed as you can just listen for specific events


    w3 = getWeb3()
    contract = w3.eth.contract(abi=abi, address=contractAddress)
    # deadline_filter = contract.events.DeadlineConfirmed.createFilter(fromBlock='latest')
    checkin_filter = contract.events.CheckIn.createFilter(fromBlock='latest')
    fund_filter = contract.events.FundReceived.createFilter(fromBlock='latest')
    print("listening to event on contract: " + contractAddress)
    while True:
        events = fund_filter.get_new_entries() + checkin_filter.get_new_entries()
        for event in events:
            print(web3.Web3.toJSON(event))
            processEvent(event)
        # for event in checkin_filter.get_new_entries():
        #     print(web3.Web3.toJSON(event))
        #     processEvent(event)
        # for event in deadline_filter.get_new_entries():
        #     print(web3.Web3.toJSON(event))
        #     processEvent(event)
        sleep(1)
            # processEvent(event)
        # await asyncio.sleep(2)

def sendEmail(to, subject, message):
    print("sending email")


def testSchedule(text):
    print(text)

def getDatetime(string):
    return datetime.datetime.strptime(string, "%Y-%b-%d %H:%M:%S")
def getTimestamp(date):
    return int(datetime.datetime.timestamp(date))
#
# scheduler = BackgroundScheduler()
# scheduler.add_job(testSchedule, "interval", seconds=10, id="test")
# scheduler.start()
#
# print(scheduler.get_jobs())
#
# try:
#         # This is here to simulate application activity (which keeps the main thread alive).
#     while True:
#         time.sleep(15)
# except (KeyboardInterrupt, SystemExit):
#         # Not strictly necessary if daemonic mode is enabled but should be done if possible
#     scheduler.shutdown()
    #situation deadline reached but live is not confirmed is not an elif because
    #in that situation, there is nothing to alert except the contract functions
    # of refunding money back to original address, same with missed live
# if event emitted is confirm live then use confirmLive
global abi
abi = """[
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "timeLimit",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "interval",
				"type": "uint256"
			},
			{
				"internalType": "address payable[]",
				"name": "sendTo",
				"type": "address[]"
			},
			{
				"internalType": "uint256[]",
				"name": "sendPercentage",
				"type": "uint256[]"
			}
		],
		"stateMutability": "nonpayable",
		"type": "constructor"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"internalType": "address",
				"name": "from",
				"type": "address"
			},
			{
				"indexed": false,
				"internalType": "uint256",
				"name": "nextLive",
				"type": "uint256"
			}
		],
		"name": "CheckIn",
		"type": "event"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"internalType": "address",
				"name": "from",
				"type": "address"
			}
		],
		"name": "DeadlineConfirmed",
		"type": "event"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"internalType": "address",
				"name": "from",
				"type": "address"
			},
			{
				"indexed": false,
				"internalType": "uint256",
				"name": "funds",
				"type": "uint256"
			}
		],
		"name": "FundReceived",
		"type": "event"
	},
	{
		"stateMutability": "payable",
		"type": "fallback"
	},
	{
		"inputs": [],
		"name": "Deadline",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "confirmLive",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "contractAddress",
		"outputs": [
			{
				"internalType": "address payable",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "deadLine",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "getFund",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "getTime",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "getTimeNow",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "isDeadLine",
		"outputs": [
			{
				"internalType": "bool",
				"name": "",
				"type": "bool"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "isPastLive",
		"outputs": [
			{
				"internalType": "bool",
				"name": "",
				"type": "bool"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "lastLive",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "liveInterval",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "nextLive",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "owner",
		"outputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"name": "recipents",
		"outputs": [
			{
				"internalType": "address payable",
				"name": "reciAddress",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "receivePercentage",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "totalFunds",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"stateMutability": "payable",
		"type": "receive"
	}
]"""
def testDeadLine(contractAddress):
    files = DButi.getFileURLs(contractAddress)
    for file in files:
        print(file)
        gmail.sendEmail(file["remail"], file["url"])
    # DButi.cancelContractDB(event["address"])
    print("event  deadline reached") # for both live deadline and contract dealine
