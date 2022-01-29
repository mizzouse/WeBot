import multiprocessing
import os

import WebullTradingBot

class MultiProcess():
    """Initiates a single process using a unique id
    as a distinguisher and the target is the function
    being called.
    """

    def __init__(self, Id: int = 0):
        """Initiates a Multiprocess object to support an async
        function.
        
        Usage:
        ----
        MultiProcess(int: Id, target = function or None)
        """
        # Lets check for an available ID
        if len(WebullTradingBot.process) > 0:
            while Id in WebullTradingBot.process:
                Id = Id + 1

        self.Id = Id
        self.target = None
        self.process: multiprocessing.Process = None

    def run(self, targetFunction = None):
        """Will run the target process if the target
        function exists.
        """
        if targetFunction is None:
            print("Cannot run a process without a target process to use.")
            return
        self.target = targetFunction

        process = multiprocessing.Process(target = targetFunction)
        self.process = process

        print("Starting " + targetFunction)
        process.start()

        return

    def stop(self):
        """Will stop the process if the process still exists"""
        if self.process is None:
            print("Cannot stop a process that doesn't exist.")
            return

        print("Stopping " + self.target)
        self.process.terminate()

        if self.process.is_alive() == False:
            self.process.close()
            self.process = None

        return

    def get_id(self):
        """Returns the ID that was set during initialization"""
        return self.Id
