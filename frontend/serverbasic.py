import http.server
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import json
import web3
from web3 import Web3
from web3.auto import w3
import asyncio
from src import websiteUtility as uti
from src import databaseUtil as DButi
from threading import Thread
from time import sleep
import datetime
import time

class S(http.server.SimpleHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    # def do_GET(self):
    #     logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
    #     self._set_response()
    #     self.wfile.write("GET request for {}".format(self.path).encode('utf-8'))

    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
            post_data = self.rfile.read(content_length) # <--- Gets the data itself
            # post_file = self.request.FILES
            # print("post_file : !!!",post_file)
            post =  post_data.decode('utf-8')
            json_acceptable_string = post.replace("'", "\"")
            d = json.loads(json_acceptable_string) # this also converts null to None for python
            logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                    str(self.path), str(self.headers), post_data.decode('utf-8'))
            # logging.info(d["name"])

            if (d["operationType"] == "createContract"):

                print("creating contract")
                response = DButi.createContractDB(d)
                if (response != False):
                    thread = Thread(target=uti.listenToEvent, args=(d["contractAddress"],))
                    threads.append(thread)
                    thread.start()
                deadline = uti.getTimestamp(datetime.datetime.strptime(d["expirationDate"], "%Y-%m-%d"))
                today = uti.getTimestamp(datetime.datetime.today())
                print(deadline-today)
                uti.scheduleContractDeadlines(d["contractAddress"], deadline-today, d["frequency"])
                jdata = json.dumps({"response":response})
                print(jdata)
                self._set_response()
                self.wfile.write(bytes(jdata.encode(encoding='utf_8')))
                # DButi.createAccountDB()
                # uti.scheduleLive(d["contractAddress"], d["frequency"])
                # uti.scheduleContractDeadline(d["contractAddress"], d["expirationDate"])

            elif (d["operationType"] == "confirmLive"):
                print("confirm live")
                uti.confirmLive(d["contractAddress"])

            elif (d["operationType"] == "cancelContract"):
                print("cancelling contract")
                uti.cancelLiveSchedule(d["contractAddress"])
                uti.cancelContractSchedules(d["contractAddress"])
                DButi.cancelContractDB(d["contractAddress"])

            elif (d["operationType"] == "createAccount"):
                try:
                    response = DButi.createAccountDB(d["email"], d["password"], d["username"])
                    jdata = json.dumps({"response": response})
                    self._set_response()
                    self.wfile.write(bytes(jdata.encode(encoding='utf_8')))
                    print("creating account")
                except Exception as e:
                    print(e)

            elif (d["operationType"] == "accountActivation"):
                response = DButi.activateAccountDB(d["email"])
                jdata = json.dumps({"response":response})
                self._set_response()
                self.wfile.write(bytes(jdata.encode(encoding='utf_8')))
                print("activating account")


            elif (d["operationType"] == "checkLogin"):
                # try:
                response = DButi.checkAccountDB(d["email"], d["password"])
                jdata = json.dumps({"response":response})
                print(jdata)
                self._set_response()
                self.wfile.write(bytes(jdata.encode(encoding='utf_8')))
                print("checking credentials")
                # except Exception as e:
                #     print(e)


            elif (d["operationType"] == "updateFiles"):
                try:
                    response = DButi.storeFilesDB(d["uploadedFiles"], d["contractAddress"])
                    jdata = json.dumps({"response":response})
                    print(jdata)
                    self._set_response()
                    self.wfile.write(bytes(jdata.encode(encoding='utf_8')))
                    print("Adding files")
                except Exception as e:
                    print(e)
                    print("updating files failed")

            elif (d["operationType"] == "getAllContracts"):
                try:
                    response = DButi.getAllContractSimpleDetailsDB(d["email"])
                    jdata = json.dumps({"response":response})
                    print(jdata)
                    self._set_response()
                    self.wfile.write(bytes(jdata.encode(encoding='utf_8')))
                    print("getting contracts")
                except Exception as e:
                    print(e)
                    print("getting all contracts")


            elif (d["operationType"] == "getContractDetails"):
                try:
                    response = DButi.getContractDetailsDB(d["contractAddress"])
                    jdata = json.dumps({"response":response})
                    print(jdata)
                    self._set_response()
                    self.wfile.write(bytes(jdata.encode(encoding='utf_8')))

                except Exception as e:
                    print(e)
                    print("getting contract details")


            elif (d["operationType"] == "sendFunds"):
                print("sending funds")


            else:
                logging.info("at else")

        except Exception as e:
            print(e)

        # jdata = json.dumps({'hello': 'world', 'received': 'ok'})
        # self._set_response()
        # self.wfile.write(bytes(jdata.encode(encoding='utf_8')))

def run(server_class=HTTPServer, handler_class=S, port=8000):
    logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    # block_filter = w3.eth.filter("latest")
    logging.info('Starting httpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    except ConnectionAbortedError:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')





def printing():
    while True:
        print("printing")
        sleep(5)

if __name__ == '__main__':
    from sys import argv
    global threads
    threads = list()
    # t1 = Thread(target=uti.listenToEvent)
    # t2 = Thread(target=listenToEvent, args=("0xfF6bB121572a55dD0dB6430a2f26568bdd88b3A8",))
    # asyncio.run(scheduleEvents())
    if len(argv) == 2:
        run(port=int(argv[1]))
        print("arg 2")
    else:
        # t1.start()
        start = time.process_time()

        uti.rescheduleEvents()
        print("scheduling time: " + time.process_time() - start)
        # uti.listenToEvent("0x54540279e7f3FaC898a50B5b715F5Aa81132d9Ee")

        # t2.start()
        run()
        print("arg none")
