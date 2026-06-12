import random
import time
import datetime
import threading
import logging

logger = logging.getLogger(__name__)

class SimThread(threading.Thread):
    def __init__(self,sol):
        threading.Thread.__init__(self)
        self.sol=sol
        self._stopEvent=threading.Event()
        self.daemon = True

    def run_one_step(self):
        sol=self.sol
#       print "SimThread starting another month"
        sol.current_date = datetime.timedelta(30)+sol.current_date
        sol.evaluate_each_game_step()
        for company_instance in list(sol.companies.values()):
            company_instance.evaluate_self()

    def sleep_between_steps(self):
        delay_milliseconds = getattr(self.sol, "step_delay_time", 100)
        time.sleep(max(0, delay_milliseconds) / 1000.0)

    def run(self):
        try:
            while(not self._stopEvent.is_set()):
                self.run_one_step()
                self.sleep_between_steps()
        except Exception:
            logger.exception("Unhandled exception in simulation thread")
            raise
    def join(self,timeout=None):
        self._stopEvent.set()
        threading.Thread.join(self,timeout)

