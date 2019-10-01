#!/usr/bin/python

import threading


class myThread(threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadLock = threading.Lock()
        self.threadID = threadID
        self.name = name

    def run(self):
        print("Starting " + self.name)
        # Get lock to synchronize threads
        self.threadLock.acquire()
        self.execution(self.name)
        # Free lock to release next thread
        self.threadLock.release()

    def execution(self, threadName):
        pass