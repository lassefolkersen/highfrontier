import random
import time
import datetime
import threading

class SimThread(threading.Thread):
    def __init__(self,sol):
        threading.Thread.__init__(self)
        self.sol=sol
        self._stopEvent=threading.Event()
        self.setDaemon(True)
    def run(self):
        sol=self.sol
        while(not self._stopEvent.isSet()):
            print "SimThread starting another month"
            sol.current_date = datetime.timedelta(30)+sol.current_date
            sol.evaluate_each_game_step()
            for company_instance in sol.companies.values():
                company_instance.evaluate_self()
            time.sleep(1)
    def join(self,timeout=None):
        self._stopEvent.set()
        threading.Thread.join(self,timeout)

