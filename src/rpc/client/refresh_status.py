import time
import threading

class RefreshInterval:
    def __init__(self,interval,action) :
        self.interval=interval
        self.action=action
        self.status=False
        self.stopEvent=threading.Event()
        thread=threading.Thread(target=self.__setInterval)
        thread.start()

    def __setInterval(self):
        nextTime=time.time()+self.interval
        while not self.stopEvent.wait(nextTime-time.time()) :
            nextTime+=self.interval
            self.status = True
            self.action()
            
    def get_status(self):
        return self.status

    def cancel_interval(self):
        self.stopEvent.set()
        self.status = False

    def restart_interval(self):
        self.stopEvent=threading.Event()
        thread=threading.Thread(target=self.__setInterval)
        thread.start()