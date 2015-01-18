from __future__ import division
from random import *
from math import *
import sys, getopt
import scipy
from scipy.spatial.distance import cityblock
from multiprocessing import Process
import time
import collections
import numpy as np
import os

class SOM:
    def __init__(self, height=5, width=5, fv_size=4, learning_rate=0.005, seed=100):
        self.height = height
        self.width = width
        self.fv_size = fv_size
        #self.radius = (height + width)*2
	self.radius = 5      
	self.learning_rate = learning_rate
        self.seed = seed
	#self.max_train_values = []
        #self.threshold = 0
        #self.nodes = scipy.array([[[random()*seed for i in range(fv_size)] for x in range(width)] for y in range(height)])
	#print self.nodes
    # train_vector: [ fv0, fv1, fv2, ...] -> [ [...], [...], [...], ...]
    # train vector may be a list, will be converted to a list of scipy arrays
   
    def initialize(self):
        self.max_train_values = []
	self.threshold = 0
	self.nodes = scipy.array([[[randrange(10, 90) for i in range(self.fv_size)] for x in range(self.width)] for y in range(self.height)])

    def train(self, train_vector, iterations=1000):
        for t in range(len(train_vector)):
            train_vector[t] = scipy.array(train_vector[t])
        time_constant = iterations/log(self.radius)
        delta_nodes = scipy.array([[[0 for i in range(self.fv_size)] for x in range(self.width)] for y in range(self.height)])

        for i in range(1, iterations+1):
            delta_nodes.fill(0)
            radius_decaying = self.radius * exp(-1.0 * i / time_constant)
            rad_div_val = 2 * radius_decaying * i
            learning_rate_decaying = self.learning_rate * exp(-1.0 * i / time_constant)
            sys.stdout.write("\rTraining Iteration: " + str(i) + "/" + str(iterations))

            for j in range(len(train_vector)):
                best = self.best_match(train_vector[j])
                if i == iterations:
                    min_y = max(int(best[0] - 1), 0)
                    max_y = min(int(best[0] + 1), self.height - 1)
                    min_x = max(int(best[1] - 1), 0)
                    max_x = min(int(best[1] + 1), self.width - 1)

                    distance = cityblock(self.nodes[best[0], best[1]], self.nodes[max_y, best[1]])
                    distance += cityblock(self.nodes[best[0], best[1]], self.nodes[min_y, best[1]])
                    distance += cityblock(self.nodes[best[0], best[1]], self.nodes[best[0], min_x])
                    distance += cityblock(self.nodes[best[0], best[1]], self.nodes[best[0], max_x])
                    if self.threshold < distance:
                        self.threshold = distance

                for loc in self.find_neighborhood(best, radius_decaying):
                    influence = exp((-1.0 * (loc[2]**2)) / rad_div_val)
                    inf_lrd = influence*learning_rate_decaying
		    #if isnan(inf_lrd):
		    # 	print "NaN@@@@@@@@@@@@@@@@@@@@@@@@@@@@@"
		    with np.errstate(invalid='ignore'):
                      delta_nodes[loc[0], loc[1]] += inf_lrd*(train_vector[j] - self.nodes[loc[0], loc[1]])
            self.nodes += delta_nodes
        sys.stdout.write("\n")
	#print "Final"
	#print self.nodes

    def predict(self, feature_vector):
        data_point = feature_vector[:]
        for i in range(self.fv_size):
            data_point[i] = int(data_point[i] * 100.0 / self.max_train_values[i])
	#print "FV: " 
	#print data_point

        best = self.best_match(data_point)
        min_y = max(int(best[0] - 1), 0)
        max_y = min(int(best[0] + 1), self.height - 1)
        min_x = max(int(best[1] - 1), 0)
        max_x = min(int(best[1] + 1), self.width - 1)

        distance = cityblock(self.nodes[best[0], best[1]], self.nodes[max_y, best[1]])
        distance += cityblock(self.nodes[best[0], best[1]], self.nodes[min_y, best[1]])
        distance += cityblock(self.nodes[best[0], best[1]], self.nodes[best[0], min_x])
        distance += cityblock(self.nodes[best[0], best[1]], self.nodes[best[0], max_x])
        if distance > self.threshold:
            return "Anomaly"
        else:
            return "Normal"

    # Returns a list of points which live within 'dist' of 'pt'
    # Uses the Chessboard distance
    # pt is (row, column)
    def find_neighborhood(self, pt, dist):
        min_y = max(int(pt[0] - dist), 0)
        max_y = min(int(pt[0] + dist), self.height)
        min_x = max(int(pt[1] - dist), 0)
        max_x = min(int(pt[1] + dist), self.width)
        neighbors = []
        for y in range(min_y, max_y):
            for x in range(min_x, max_x):
                dist = abs(y - pt[0]) + abs(x - pt[1])
                neighbors.append((y, x, dist))
        return neighbors

    # Returns location of best match, uses Euclidean distance
    # target_fv is a scipy array
    def best_match(self, target_fv):
        loc = scipy.argmin((((self.nodes - target_fv)**2).sum(axis=2))**0.5)
	#print "Distance: " + str(loc) + "\n"
        r = 0
        while loc >= self.width:
            loc -= self.width
            r += 1
        c = loc
        return (r, c)

    # returns the Euclidean distance between two Feature Vectors
    # FV_1, FV_2 are scipy arrays
    def fv_distance(self, fv_1, fv_2):
        return (sum((fv_1 - fv_2)**2))**0.5

    def normalizer(self, train_vector):
        self.max_train_values = [0] * self.fv_size
        for i in range(len(train_vector)):
            for j in range(self.fv_size):
                    if train_vector[i][j] > self.max_train_values[j]:
                        self.max_train_values[j] = train_vector[i][j]
        #print train_vector
        for i in range(len(train_vector)):
            for j in range(self.fv_size):
                train_vector[i][j] = int(train_vector[i][j] * 100.0 / self.max_train_values[j])
	#print train_vector
	return train_vector

    def absoluteFilePaths(self, indir):
    	for dirpath,_,filenames in os.walk(indir):
      	    for f in filenames:
                yield os.path.abspath(os.path.join(dirpath, f))

    def get_immediate_subdirectories(self, a_dir):
        return [name for name in os.listdir(a_dir)
            if os.path.isdir(os.path.join(a_dir, name))]

    def executioner(self, traindir, testdir):
        absTrainDir = os.path.join(os.getcwd(), traindir)
	subTrainDirs = self.get_immediate_subdirectories(absTrainDir)
	print subTrainDirs
	absTestDir = os.path.join(os.getcwd(), testdir)
        #trainFiles = os.listdir(absTrainDir)
	testFiles = os.listdir(absTestDir)
        resultsDict = collections.OrderedDict()
	testFiles.sort()
	for eachFile in testFiles:
	    print "File: " + eachFile + " \n"
	    #if eachFile in testFiles:
            train_vector = []
	    for eachDir in subTrainDirs:
		dirPath = os.path.join(absTrainDir, eachDir)
	        if eachFile in os.listdir(dirPath):
		    with open(os.path.join(dirPath, eachFile)) as f:
                        for each_line in f:
                            train_vector.append(map(int, each_line.rstrip().split(',')))
	    print "Total learning set size: " + str(len(train_vector)) + " \n"
	    print "Last: \n"
	    print train_vector[len(train_vector)-1]
	    print "\nFirst: \n"
	    print train_vector[0] 
            test_data = []
            with open(os.path.join(absTestDir, eachFile)) as f:
                for each_line in f:
                    test_data.append(map(int, each_line.rstrip().split(',')))
	    print "Test size: " + str(len(test_data)) + " \n"
            #test_data = train_vector[len(train_vector)-30:]
            #print test_data
            #train_vector = train_vector[:len(train_vector)-30]
	    self.initialize()
            train_vector = self.normalizer(train_vector)
            print "Training Started.\n"
            self.train(train_vector, 20)
            print "Training Completed.\n"
            #feature_vector = [276,799,799,5272]    
            count = 0
            print "Analyzing test data..\n"
            for eachList in test_data:
                if (self.predict(eachList) == 'Anomaly'):
                    count+=1
            if count >= len(test_data)/2:
                resultsDict[eachFile] =  "Is it some malicious process?!! Anomaly rate: " + str((count*100)/len(test_data))
            else:
                resultsDict[eachFile] =  "Process Behavior Matched!! False detection rate: " + str((count*100)/len(test_data))
	    print "Result for "+eachFile + ": \n"
	    print resultsDict[eachFile]
	print "\nTrain dir: "
	print subTrainDirs
	print "\nTest dir: " + absTestDir + "\n"
        for eachkey in resultsDict.keys():
            print eachkey + "  :  " + resultsDict[eachkey] +"\n"
       # for eachkey in resultsDict.keys():
       #     print resultsDict[eachkey] + "\n"  	


    def main(self,argv):
        try:
            opts, args = getopt.getopt(argv,"hl:p:",["ldir=","pdir="])
        except getopt.GetoptError:
            print 'som.py -l <learn-dir> -p <predict-dir>'
            sys.exit(2)
        if(len(opts) != 2):
            print 'som.py -l <learn-dir> -p <predict-dir>'     
            exit()
        for opt, arg in opts:
            if opt == '-h':
                print 'som.py -l <learn-dir> -p <predict-dir>'
                sys.exit()
            if opt in ("-l", "--ldir"):
                traindir = arg
            if opt in ("-p", "--pdir"):
                testdir = arg
	print traindir
	print testdir
        self.executioner(traindir, testdir)
 
if __name__ == "__main__":
    width = 100
    height = 100
    somObj = SOM(height, width, 4, 0.5)
    somObj.main(sys.argv[1:])
