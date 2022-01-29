# Ini file data structure
from configparser import ConfigParser

class IniForm:
    def __init__(self, file):
        """This form creates a blank User_Credentials.ini file
        for reading and writing

        Usage:
        ----
        IniForm(filename)
        """
        self.parse = {}
        self.file = file
        self.open = open(file, "w")

        # Write our header first
        self.open.write("# User Credentials File\n")
        self.open.write("\n")

        config = ConfigParser()
        config['Credentials'] = {
            'user': '',
            'pass': '',
        }

        config['TradeToken'] = {
            'token': 0,
        }

        config.write(self.open)

        # Close the file after writing
        self.open.close()
