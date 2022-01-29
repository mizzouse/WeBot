# Webull Trading Bot v1.0

import sys
import json
import os
import os.path
import time

import Parsers.ConfigParser as iniParser
import Data.IniForm as iniForm
import Bots.TradingBot as Bot
from Utils.MultiProcessing import MultiProcess

""" The initial program which runs a credentials check,
creates and initializes a trading bot, then creates a
session with the Webull API through the TradingBot class.
"""

# Global multiprocess tracker used for asyncing methods
process = {}

def add_or_delete_processList(Process: MultiProcess, delete: bool = False):
    id = Process.get_id

    if delete is True:
        if id in process.keys():
            del[id]
    else:
        process[id] = Process

def id_in_processList(Process: MultiProcess, Id: int) -> bool:
    if Id in process.keys():
        return True
    return False

# This is the start of our initialization
if __name__ == '__main__':
    print("Starting program..")
    time.sleep(2)

    print("Checking for a User_Credentials.ini file...")

    # test for our ini file first, if not error
    if (os.path.exists('User_Credentials.ini') is False):
        print('User_Credentials.ini file does not exist.')
        
        answer = input("Would you like to create one? Type y or n\n")
        if (answer == 'y' or answer == 'Y'):
            form = iniForm.IniForm('User_Credentials.ini')
            print('File was created in ' + os.getcwd())

            answer = input("Would you like to add or change your credentials? Type y or n\n")
            if (answer == 'y' or answer == 'Y'):
                ini = iniParser.IniOpen('User_Credentials.ini')

                username = input("What is your username? Type either your Email or Phone number")
                print(ini.write('Credentials', 'user', username))

                password = input("What is your password?")
                print(ini.write('Credentials', 'pass', password))

                ini.close()
        else:
            print('Exiting...')
            sys.exit(0)

    # Get Login credentials
    print("Retrieving user login information...")
    ini_file = iniParser.IniOpen('User_Credentials.ini')

    if ini_file.hasKey("Credentials", "user") == False:
        print("There is no value for username in the User_Credentials.ini file.")
        print("Exiting...")
        sys.exit(0)

    if ini_file.hasKey("Credentials", "pass") == False:
        print("There is no value for password in the User_Credentials.ini file.")
        print("Exiting...")
        sys.exit(0)

    bot = Bot.TradingBot()
    print("Do you want this bot to perform paper trading only? (Note: Paper trading is simulated trading, no real money is used)")
    answer = input("Type y or n\n")

    if (answer == 'n' or answer == 'N'):
        bot.paper_trading = False

    print("Attempting login...")
    
    # Try a normal login without security questions and MfA
    successful = bot._create_session(ini_file.read("Credentials", "user"), ini_file.read("Credentials", "pass"))

    # Check to see if the login failed
    if successful == False:
        userValid = bot.get_mfa(ini_file.read("Credentials", "user"))

        if (userValid):
           print("Username or mobile number valid.")
           print("Awaiting verification code validation...check your mobile device or email for code.")
        else:
           print("Username or mobile number not found, exiting...")
           sys.exit(0)

        # Grab verification code input
        mfa_code = input("MFA Code: ")

        question = bot.get_security(ini_file.read("Credentials", "user"))

        #Show only the question
        print(question[0]['questionName'])
        security_answer = input("Security Question Answer: ")

        # Grab the id
        question_id = question[0]['questionId']

        # Try recreating our login session
        bot._create_session(ini_file.read("Credentials", "user"), ini_file.read("Credentials", "pass"), "WeBot", mfa_code, question_id, security_answer)
    
    if bot.is_logged_in == True:

        # Set up our trading token for the bot
        trade = bot.unlock_trading(ini_file.read("TradeToken", "token"))

        # Was the trade token valid?
        if trade is not True:
            print("Trade token password was not valid. No buying or selling orders will be completed.")

        # Are we automating our trades?
        answer = input("Would you like to start automated trading? Type y or n\n")
        if (answer == 'y' or answer == 'Y'):
            from Bots.AiBot import AiBot
            Ai = AiBot(bot.trading_account, bot)

            Ai.initiate_session()
            

        # Place an order
        #wb.place_order(stock='PROG', price=1.93, quant=1)

        # Get all orders
        orders = bot.get_current_orders()
        print(orders)
