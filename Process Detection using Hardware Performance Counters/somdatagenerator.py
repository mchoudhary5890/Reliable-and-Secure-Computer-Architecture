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

class SOMDataGeneration:

  def __init__(self):
    self.inDir = ''
    #self.groupValuesDict = dict()
    #self.groupNamesDict = dict()
    self.extractTo = os.path.join(os.getcwd(),'current')
    self.dumpTo = os.path.join(os.getcwd(), 'somfiles')
    if not os.path.exists(self.dumpTo):
      os.makedirs(self.dumpTo)
    self.processName = ''    

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
        groupValuesDict = dict()
	self.processName = os.path.splitext(self.pathLeaf(eachZip))[0]
        self.outdir = os.path.join(self.dumpTo, self.processName)
        if os.path.exists(self.outdir):
	  shutil.rmtree(self.outdir)  
        os.makedirs(self.outdir)
        if not os.path.exists(self.extractTo):
	  os.makedirs(self.extractTo)
      	with zipfile.ZipFile(eachZip, "r") as z:
	  z.extractall(self.extractTo)  
	groups = self.getImmediateSubdirectories(self.extractTo)
	for eachGroup in groups:
	  if "mem-stores,instructions,cache-references,L1-dcache-prefetch-misses" in eachGroup:
	    continue
	  groupName = self.pathLeaf(eachGroup)
          listOfLists = []
	  eventFileList = sorted(os.listdir(eachGroup))
	  for eachFile in eventFileList:
            if 'raw' in eachFile:
              continue
	    fileAbsPath = os.path.abspath(os.path.join(eachGroup, eachFile))
	    with open(fileAbsPath) as f:
              listOfLists.append(map(int, f.read().splitlines()))
	  minLength = len(listOfLists[0])
	  for eachList in listOfLists:
	    if len(eachList) < minLength:
	      minLength = len(eachList)
	  for eachList in listOfLists:
	    if len(eachList) > minLength:
	      del eachList[minLength:len(eachList)]
	  self.dataFileGenerator(zip(*listOfLists), groupName)
	shutil.rmtree(self.extractTo)
  
  def arffGenerator(self, dataList, rawNamesList, group):
    namesList = []
    for name in rawNamesList:
      namesList.append((name,'REAL'))
    arffDict = {}
    arffDict['description'] = u''
    arffDict['relation'] = 'perfEvents'
    arffDict['attributes'] = namesList
    arffDict['data'] = dataList
    outFile = os.path.join(self.dumpTo, group + '.arff')
    with open(outFile, 'w') as f:
      f.write(arff.dumps(arffDict))

  def dataFileGenerator(self, dataList, group):
    outFile = os.path.join(self.outdir, group + '.txt')
    with open(outFile,'w') as f:
      for eachList in dataList:
        f.write("%s\n" %(','.join(map(str,eachList))))  

  def main(self,argv):
    try:
      opts, args = getopt.getopt(argv,"hi:",["ifile="])
    except getopt.GetoptError:
      print 'somdatagenerator.py -i <inDir>'
      sys.exit(2)
    if(len(opts) != 1):
      print 'somdatagenerator.py -i <inDir>'     
      exit()
    for opt, arg in opts:
      if opt == '-h':
        print 'somdatagenerator.py -i <inDir>'
        sys.exit()
      if opt in ("-i", "--ifile"):
        self.inDir = arg
    print 'Input Dir: ', self.inDir
    self.dataHandler()
 
if __name__ == "__main__":
   dataObject = SOMDataGeneration()
   dataObject.main(sys.argv[1:])  
