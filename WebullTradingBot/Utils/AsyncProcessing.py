import multiprocessing
import os

_lastMultiProcessId = -1 # Start of our initial id

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
        if Id == _lastMultiProcessId or _lastMultiProcessId == -1:
            Id = _lastMultiProcessId + 1

        _lastMultiProcessId = Id

        self._Id = Id
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

    @property
    def get_id(self):
        """Returns the ID that was set during initialization"""
        return self._Id

class ProcessContainer():
    """Container list that holds each async process being called
    Usage:
    ----
    process = ProcessContainer()
    process.add_or_delete(MultiProcess, delete = True or False)
    """
    def __init__(self, processList = {}) -> None:
        self._processList = processList

    def add_or_delete_processList(Process: MultiProcess, delete: bool = False):
        """Adds or deletes a multiprocess object within the process
        list by using the id as an index
        Usage:
        ----
        add_or_delete_processList(Multiprocess object, delete = True or False)
        """
        id = Process.get_id

        if delete is True:
            if id in self._processList.keys():
                del[id]
        else:
            self._processList[id] = Process

    def id_in_processList(Process: MultiProcess, Id: int) -> bool:
        """Checks for a valid id within the process list
        Returns:
        ----
        {Bool} -- Returns true if id exists, false otherwise
        """
        if Id in self._processList.keys():
            return True
        return False

    @property
    def ProcessList(self):
        """Gets the process list dictionary for the Process
        Container
        """
        return self._processList