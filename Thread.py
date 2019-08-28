#!/usr/bin/python

import threading

class myThread (threading.Thread):
   def __init__(self, threadID, name):
      threading.Thread.__init__(self)
      self.threadLock = threading.Lock()
      self.threadID = threadID
      self.name = name
   def run(self):
      print ("Starting " + self.name)
      # Get lock to synchronize threads
      self.threadLock.acquire()
      self.execution(self.name)
      # Free lock to release next thread
      self.threadLock.release()


   def execution(self, threadName):
       pass


# threads = []
#
# # Create new threads
# thread1 = myThread(1, "Thread-1", 1)
# thread2 = myThread(2, "Thread-2", 2)
#
# # Start new Threads
# thread1.start()
# thread2.start()
#
# # Add threads to thread list
# threads.append(thread1)
# threads.append(thread2)
#
# # Wait for all threads to complete
# for t in threads:
#     t.join()
# print ("Exiting Main Thread")