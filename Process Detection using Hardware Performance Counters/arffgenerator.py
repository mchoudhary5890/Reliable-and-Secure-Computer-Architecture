#! usr/bin/python

import os
import sys, getopt
import zipfile
import numpy as np
import collections 
import numpy as np
import arff
import ntpath
import shutil

class ArffGeneration:

  def __init__(self):
    self.inDir = ''
    self.groupValuesDict = dict()
    self.groupNamesDict = dict()
    self.extractTo = os.path.join(os.getcwd(),'current')
    self.dumpTo = os.path.join(os.getcwd(), 'arffs')
    self.processClassLabelDict = dict()
    if os.path.exists(self.dumpTo):
      shutil.rmtree(self.dumpTo)
    os.makedirs(self.dumpTo)
    self.classLabelCounter = 0


  def absoluteFilePaths(self):
    for dirpath,_,filenames in os.walk(self.inDir):
      for f in filenames:
        yield os.path.abspath(os.path.join(dirpath, f))

  def getImmediateSubdirectories(self, currentDir):
    return [os.path.join(currentDir, name) for name in os.listdir(currentDir)
      if os.path.isdir(os.path.join(currentDir, name))]

  
  def pathLeaf(self, path):
	head, tail = ntpath.split(path)
	return tail or ntpath.basename(head)

  def dataHandler(self):
    if os.path.isdir(self.inDir):
      for eachZip in self.absoluteFilePaths():
	self.classLabelCounter += 1
	processName = os.path.splitext(self.pathLeaf(eachZip))[0]
	self.processClassLabelDict[processName] = self.classLabelCounter
        if not os.path.exists(self.extractTo):
	  os.makedirs(self.extractTo)
      	with zipfile.ZipFile(eachZip, "r") as z:
	  z.extractall(self.extractTo)  
	groups = self.getImmediateSubdirectories(self.extractTo)
	for eachGroup in groups:
	  if "mem-stores,instructions,cache-references,L1-dcache-prefetch-misses" in eachGroup:
	    continue
	  groupName = self.pathLeaf(eachGroup)
          doAdd = None
	  if groupName not in self.groupNamesDict.keys():
	    self.groupNamesDict[groupName] = []
            doAdd = 1
	  listOfLists = []
	  eventFileList = sorted(os.listdir(eachGroup))
	  for eachFile in eventFileList:
	    if doAdd and ("raw" not in eachFile):
	      self.groupNamesDict[groupName].append(os.path.splitext(eachFile)[0])
	    if "raw" in eachFile:
	      continue
	    fileAbsPath = os.path.abspath(os.path.join(eachGroup, eachFile))
	    with open(fileAbsPath) as f:
              listOfLists.append(map(int, f.read().splitlines()))
	  if doAdd:
	    self.groupNamesDict[groupName].append('classLabel')
	  minLength = len(listOfLists[0])
	  for eachList in listOfLists:
	    if len(eachList) < minLength:
	      minLength = len(eachList)
	  for eachList in listOfLists:
	    if len(eachList) > minLength:
	      del eachList[minLength:len(eachList)]
	  listOfLists.append([self.classLabelCounter] * minLength)
	  if groupName in self.groupValuesDict.keys():
	    self.groupValuesDict[groupName].extend(zip(*listOfLists))
	  else:
	    self.groupValuesDict[groupName] = zip(*listOfLists)
	shutil.rmtree(self.extractTo)
      print self.processClassLabelDict
      #print self.groupValuesDict['instructions,branch-misses,mem-stores,cache-references']  
  
  def arffGenerator(self, dataList, rawNamesList, group):
    namesList = []
    for name in rawNamesList:
      namesList.append((name,'REAL'))
    arffDict = {}
    arffDict['description'] = u''
    arffDict['relation'] = 'perfEvents'
    arffDict['attributes'] = namesList
    arffDict['data'] = dataList
   # print arff.dumps(arffDict)
    outFile = os.path.join(self.dumpTo, group + '.arff')
    with open(outFile, 'w') as f:
      f.write(arff.dumps(arffDict))

  def main(self,argv):
    try:
      opts, args = getopt.getopt(argv,"hi:",["ifile="])
    except getopt.GetoptError:
      print 'arffgenerator.py -i <inDir>'
      sys.exit(2)
    if(len(opts) != 1):
      print 'arffgenerator.py -i <inDir>'     
      exit()
    for opt, arg in opts:
      if opt == '-h':
        print 'arffgenerator.py -i <inDir>'
        sys.exit()
      if opt in ("-i", "--ifile"):
        self.inDir = arg
    print 'Input Dir: ', self.inDir
    self.dataHandler()
    for element in self.groupNamesDict.keys():
      self.arffGenerator(self.groupValuesDict[element], self.groupNamesDict[element], element)
 
if __name__ == "__main__":
   arffObject = ArffGeneration()
   arffObject.main(sys.argv[1:])  
