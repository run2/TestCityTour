'''
Created on Jun 28, 2015

@author: run2
'''
import logging
import os 
from citytour import CityMap
from citytour import findQuickestPath
import sys, getopt

logger = logging.getLogger()

LEVELS = { 'debug':logging.DEBUG,
            'info':logging.INFO,
            'warning':logging.WARNING,
            'error':logging.ERROR,
            'critical':logging.CRITICAL,
            }


class TestCityTour():

    default_log_file = 'testcitytour.log'
    default_log_dir = '.'

    def usage(self,ex=0):
        print 'TestCityTour.py -c <configFile> -l <logLevel> -s<start> -e<end>'
        sys.exit(ex)
            
    def configure(self,argv):
        configFile = ''
        logLevel = 'info'
        start = ''
        end = ''
        try:
            opts, args = getopt.getopt(argv[1:],"hc:l:s:e:",["help","cfile=","lLevel=","start=","end="])
        except getopt.GetoptError as err:
            print(err)
            self.usage(2)
        for opt, arg in opts:
            if opt == '-h':
                self.usage()
            elif opt in ("-c", "--cfile"):
                configFile = arg
            elif opt in ("-l", "--lLevel"):
                logLevel = arg
            elif opt in ("-s", "--start"):
                start = arg
            elif opt in ("-e", "--end"):
                end = arg

        if (configFile == '' or not os.path.exists(configFile)): # add a check for ending with '/' on configDir later
            self.usage(2)
        
        print 'Config File is ', configFile
        print 'Log level is ', logLevel
        print 'Log file is at ', self.default_log_file

        print 'Start at ' + start
        print 'End at ' + end

        props = dict(line.strip().split('=') for line in open(configFile))
        return props,logLevel,start,end
                
    def setUpLogging(self,props,logLevel):
        
        logFile = self.default_log_file
        logDir = self.default_log_dir
        if 'LOGFILE' in props:
            logFile = props['LOGFILE']
        else:
            print 'Missing log file setting in config file - will use default testcitytour.log'
        if 'LOGDIR' in props:
            logDir = props['LOGDIR']
        else:
            print 'Missing log dir setting in config file - will use default .'

        info_hdlr = logging.FileHandler(logDir + '/' + logFile)
        info_fmtr =  logging.Formatter('%(asctime)s\t%(levelname)s -- %(processName)s %(filename)s:%(lineno)s -- %(message)s')
        info_hdlr.setFormatter(info_fmtr)
        logger.addHandler(info_hdlr) 
        logger.setLevel(level=LEVELS[logLevel])
    
    def getCityMap(self,props):
        
        value = props.get('map')
        if(value==None):
            raise ValueError('Could not find map in properties')
        
        citymap = CityMap()
        citymap.setEdges(value)

        # can be optimized to hold single entry for bi-directional paths
        value = props.get('dist')
        if(value==None):
            raise ValueError('Could not find distances in properties')
        citymap.setDistances(value)

        value = props.get('waittimes')
        if(value==None):
            raise ValueError('Could not find wait times in properties')
        citymap.setWaitTimes(value)

        value = props.get('avgspeed')
        if(value==None):
            raise ValueError('Could not find avg speed in properties')
        citymap.setAvgSpeed(value)

        for l in ['leftright_of_X','topbottom_of_X','leftWait','rightWait','topWait','bottomWait']:
            value = props.get(l)
            if(value==None):
                raise ValueError('Could not find ' + l + ' ' + ' of X in properties')

        citymap.setXWaitingList(props['leftright_of_X'],props['topbottom_of_X'],props['leftWait'],props['rightWait'],props['topWait'],props['bottomWait'])

        return citymap

if __name__ == '__main__':
    
    try:
        
        testcitytour = TestCityTour()
        
        props,logLevel,start,end = testcitytour.configure(sys.argv)
        
        if (start=='' or end == ''):
            raise ValueError('Invalid start or end specified ')

        testcitytour.setUpLogging(props,logLevel)
        
        logger.info('-----------------------------START PROCESSING---------------------------------------')
        citymap = testcitytour.getCityMap(props)

        path,timetaken = findQuickestPath(citymap,start,end)
        
        logger.info('Fastest Path is ' + str(path))
        logger.info('Time taken ' + str(timetaken))
        print 'Fastest Path is ' + str(path)
        print 'Time taken ' + str(timetaken) + ' seconds'

    except ValueError as err:
        
        logger.error(err)
        print 'There was an error . Please check the log file for details '
        
    logger.info('-----------------------------END PROCESSING---------------------------------------')