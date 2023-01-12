''' 
pyPr0xyChecker
a fast python proxy checker
made by github.com/n0nexist
'''

import threading # for multithreading
import requests # to make http requests
import argparse # to parse command-line arguments
from pystyle import Colors, Colorate # to print colored text
import time 
import os
import signal 
import sys
from colorama import Fore, Back, Style
from colorama import init # to print the colored status bar
init()

class logging:
    '''
    Functions for 
    loggin errors and informations 
    '''
    
    def info(text):
        print(Colorate.Horizontal(Colors.blue_to_cyan, f"🔹 {text}", 1))
    
    def error(text):
        print(Colorate.Horizontal(Colors.blue_to_red, f"❌ {text}", 1))
        
    def printProgressBar(iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
        '''
        Taken (and modified) from:
        https://stackoverflow.com/questions/3173320/text-progress-bar-in-terminal-with-block-characters/13685020
        (the only function in this code that isn't mine)
        '''
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        print(f'\r {Fore.BLUE}{prefix}{Fore.CYAN} |{Fore.BLUE}{bar}{Fore.CYAN}|{Fore.BLUE} {percent}%{Fore.CYAN} {suffix}{Fore.RESET}',end="\r")
        if iteration == total: 
            print()

            
# Arguments
parser = argparse.ArgumentParser(
                    prog = 'pyPr0xyChecker',
                    description = 'a fast python proxy checker',
                    epilog = 'www.github.com/n0nexist')
parser.add_argument('-t', '--threads',
                    help="The number of threads the program will use. (default=25)")
parser.add_argument('-i', '--input',
                    help="The input file to check proxies from.")
parser.add_argument('-o', '--output',
                    help="The output file to save the results in.")
parser.add_argument('-pt', '--type',
                    help="Proxies type, http/socks4/socks5. (default=http)")
parser.add_argument('-v', '--verbose',
                    action='store_true',
                    help="Shows errors. (default=False)")
args = vars(parser.parse_args())

arg_threads = args['threads']
arg_input = args['input']
arg_output = args['output']
arg_type = args['type']
arg_verbose = args['verbose']

if arg_threads == None:
    arg_threads = 25
    
if arg_type == None:
    arg_type = "http"

if arg_input == None or arg_output == None:
    parser.print_help()
    logging.error("You must at least provide --input and --output arguments.")
    exit()

class proxies:
    '''
    All the functions this program needs
    to work with proxies
    '''
    
    def checkproxy(proxy,proxytype,f):
        '''
    Checks if a proxy is working and it's delay
    when making a request to ifconfig.me/ip.
    Valid proxy types:
    http, socks4, socks5 
        '''
        
        try:
            start = time.perf_counter()
            
            # makes a request with the selected proxy to 
            # this website, which tells the visitor their ip address
            response = requests.get("http://www.ifconfig.me/ip", proxies={'http': f'{proxytype}://{proxy}'})
            request_time = time.perf_counter() - start # calculate how much milliseconds have passed
            
            request_time = str(request_time)[:3] # limits this string by the first 3 characters
            
            
            # writes proxy's info on the output file
            valid = proxy.startswith(response.text)
            content = f"Proxy({proxytype}): {proxy} - Working: {valid} - Delay(seconds): {request_time}\n"
            
        except requests.exceptions.ProxyError: # if we get this error, the proxy doesen't work at all
            pass
        
        except ValueError as e: # we probably already closed the file, hence we're done with the task of checking
            if "operation on closed file" in str(e):
                exit()
        
        except Exception as e:
            if arg_verbose:
                logging.error(str(e))
            pass
            
        
    
    def load_list(path,proxytype,threads,output):
        ''' 
        Loads the proxy lists
        and divides (in threads)
        the task to complete, which
        is checking every proxy's delay
        '''
        
        try:
            f = open(path,"r") # opens the file
            
            logging.info("loading proxy list..") 
            content = f.readlines() # saves the lines in a list inside of this variable
        
            f.close() # closes the file
            logging.info("proxy list loaded")

            # starts checking the proxies
            logging.info("checking proxies..")

            f = open(output,"a")
            l = len(content)
            print("")
            logging.printProgressBar(0, l, prefix = 'Progress:', suffix = 'Complete', length = 50) # creates the progress bar
            for x in range(l):
                proxy = content[x].strip() # .strip() removes any newline from the string
                logging.printProgressBar(x, l-1, prefix = 'Progress:', suffix = 'Complete', length = 50) # updates the progress bar
                threading.Thread(target=proxies.checkproxy,args=(proxy, proxytype, f)).start()                        
            f.close()
                        
        
        except Exception as e:
            logging.error(str(e)) # if there's an error, print it
            

class main:
    '''
    The main functions of the program 
    '''

    def cls():
        '''
        Clears the screen
        (working for windows and linux)
        '''
        os.system("cls" if os.name=="nt" else "clear")
    
    def logo():
        '''
        Returns the program's ascii logo
        '''
        return """

┌─┐┬ ┬               
├─┘└┬┘               
┴   ┴                
╔═╗┬─┐─┐ ┬┬ ┬        
╠═╝├┬┘┌┴┬┘└┬┘        
╩  ┴└─┴ └─ ┴         
╔═╗┬ ┬┌─┐┌─┐┬┌─┌─┐┬─┐
║  ├─┤├┤ │  ├┴┐├┤ ├┬┘
╚═╝┴ ┴└─┘└─┘┴ ┴└─┘┴└─
> Fast python proxy checker by github.com/n0nexist
              """
        
              
    def main():
        '''
        Prints the logo and processes system arguments
        '''
        main.cls()
        print(Colorate.Diagonal(Colors.blue_to_cyan, main.logo(), 1))
        logging.info(f"threads > {arg_threads}")
        logging.info(f"input file > {arg_input}")
        logging.info(f"output file > {arg_output}")
        logging.info(f"proxy type > {arg_type}")
        logging.info(f"verbosity > {arg_verbose}")
        print("")
        proxies.load_list(arg_input,arg_type,int(arg_threads),arg_output)
        
        
main.main()