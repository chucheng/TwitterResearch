"""Configuration.py take charges of all configurations.

This moudle serves the following purposes:
(1) Load the cfg file(s).
(2) Determine the "base" dir based on machine name.

Ref:
http://docs.python.org/library/configparser.html
"""

import ConfigParser 
import socket

def getConfig():
    """Read TwitterResearch.cfg and dynamically determine base dir by hostname.    
    """
    #check host name to determine base dir
    project_base_dir = None
    hostname = socket.gethostname()
    if hostname == "chucheng-410s":
        project_base_dir = "/home/chucheng/Projects/github/TwitterResearch/"
    elif hostname == "Shahinshah.local":
        project_base_dir = "/Users/cmoghbel/Code/TwitterResearch/"
    elif hostname == "shahin-desktop" or hostname == "birch":
        project_base_dir = "/home/cmoghbel/Code/TwitterResearch/"
    else:
        log("Error: hostname unknown - " + hostname)
        return None
    
    
    config = ConfigParser.ConfigParser()
    config.read("TwitterResearch.cfg")
    config.set("Path", "base-dir", project_base_dir)
    return config
    
def log(msg):
    print msg
    
    
if __name__ == '__main__':
    """Print all configuration. """
    config = getConfig()
    for section in config.sections():
        print "[" + section + "]"
        for option in config.options(section):
            print option + " = " + str(config.get(section, option))
        
