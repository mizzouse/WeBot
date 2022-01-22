import multiprocessing
import os

class MultiProcess:
    """Initiates a single process using a unique id
    as a distinguisher and the target is the function
    being called.
    """

    def __init__(self, Id: int = 0, target = None):
        self.Id = Id
        self.target = target

    def run(self):
        if target is None:
            print("Cannot run a process without a target process to use.")
            return

        process = multiprocessing.Process(target = self.target)
        return process
