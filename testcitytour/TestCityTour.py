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

    def usage(self,exit=0):
        print 'TestCityTour.py -h -c <configFile> -l <logLevel>'
        sys.exit(exit)
            
    def configure(self,argv):
        configFile = ''
        logLevel = 'info'
        try:
            opts, args = getopt.getopt(argv[1:],"hc:l:",["cfile=","lLevel="])
        except getopt.GetoptError:
            self.usage(2)
        for opt, arg in opts:
            if opt == '-h':
                self.usage()
            elif opt in ("-c", "--cfile"):
                configFile = arg
            elif opt in ("-l", "--lLevel"):
                logLevel = arg

        if (configFile == '' or not os.path.exists(configFile)): # add a check for ending with '/' on configDir later
            self.usage(2)
            
        print 'Config File is ', configFile
        print 'Log level is ', logLevel
        props = dict(line.strip().split('=') for line in open(configFile))
        return props,logLevel
                
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
        connections = props['map']
        citymap = CityMap()
        edges = {}
        
        noOfEdges = len(connections.split(';'))
        
        if(noOfEdges == 0 ):
            raise ValueError('No Edges are specified')
        
        for node in connections.split(';'):
            logger.debug('Next node ' + node)
            edges[node.split(':')[0]] = node.split(':') [1].split(',')
        
        logger.info('Edges initialized as ' + str(edges))
        citymap.edges = edges
        

        
        # can be optimized to hold single entry for bi-directional paths
        connections = props['dist']

        noOfDistances = len(connections.split(';'))

        if(0 == noOfDistances or noOfDistances != noOfEdges):
            raise ValueError('No Distances specified OR does not match with edges')

        edgeDistances = {}
        for currentNode in connections.split(';'):
            logger.debug('Next node ' + currentNode)
            source = currentNode.split(':')[0]
            distances = currentNode.split(':')[1].split(',')
            destinations = edges[source]
            for dist, dest  in zip(distances,destinations):
                edgeDistances[source + '-' + dest] = dist
        
        logger.info('Distances initialized as ' + str(edgeDistances))
        citymap.distances = edgeDistances

        # can be optimized to hold single entry for bi-directional paths
        connections = props['waittimes']

        noOfWaits = len(connections.split(';'))

        if(0 == noOfWaits or noOfWaits!= noOfDistances ):
            raise ValueError('No Wait times specified OR does not match with edges')

        waitTimes = {}
        for currentNode in connections.split(';'):
            logger.debug('Next node ' + currentNode)
            source = currentNode.split(':')[0]
            waittime = currentNode.split(':')[1]
            waitTimes[source] = waittime
        
        logger.info('Wait times initialized as ' + str(waitTimes))
        citymap.waitTimes = waitTimes
        
        return citymap

if __name__ == '__main__':

    testcitytour = TestCityTour()
    props,logLevel = testcitytour.configure(sys.argv)
    testcitytour.setUpLogging(props,logLevel)
    citymap = testcitytour.getCityMap(props)
    
    path = findQuickestPath(citymap,'D','E')
    print path
    