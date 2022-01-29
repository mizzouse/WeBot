# Config Ini parser for read and writing capabilities

class IniOpen:
    def __init__(self, file):
        self.parse = {}
        self.file = file
        self.open = open(file, "r")
        self.f_read = self.open.read()
        split_content = self.f_read.splitlines()

        section = ""
        pairs = ""

        # internal function to get the string between section brackets
        def string_between(section):
            start = section.index('[')
            end = section.index(']', start + 1)

            substring = section[start + 1:end]
            return substring

        for i in range(len(split_content)):
            if split_content[i].find("[") != -1: # if it does exist
                section = split_content[i]
                section = string_between(section)
                self.parse.update({section: {}})
            elif split_content[i].find("[") == -1 and split_content[i].find("=") != -1: # if '[' doesnt exist but '=' does
                pairs = split_content[i]
                split_pairs = pairs.split("=")
                key = split_pairs[0].strip()
                value = split_pairs[1].strip()
                self.parse[section].update({key: value})

    def read(self, section, key):
        """Checks to see if the section has a key value

        Usage:
        ---
        if read(section, key)

        Return:
        ---
        Returns key value if found, Key not found otherwise
        """
        try:
            return self.parse[section][key]
        except KeyError:
            return "Sepcified Key Not Found!"

    def write(self, section, key, value):
        """Writes a value to the section and key of your choice

        Usage:
        ----
        .write("section", "key", value)
        """

        if self.parse.get(section) is None:
            self.parse.update({section: {}})
        
        if self.parse.get(section) is not None:
            if self.parse[section].get(key) is None:
                self.parse[section].update({key: value})
            elif self.parse[section].get(key) is not None:
                return "Content Already Exists"

        return "File updated"

    def hasKey(self, section, key) -> bool:
        """Checks to see if the section has a key value

        Usage:
        ---
        if hasKey(section, key) == True

        Return:
        ---
        Returns true if found, false otherwise
        """

        try:
            valid = self.parse[section][key]
            if valid:
                return True
        except KeyError:
            return False

    def close(self):
        """Closes the file, if opened"""
        self.open.close()
        