#!/usr/bin/python
import zipfile
import os
import collections
import arff
import sys, getopt
import csv
import numpy as np

class ArffGeneration:

  def __init__(self):
    self.inZip = ''
    self.outArff = ''
    self.featureValuesDict = collections.OrderedDict()

  def zipfileHandler(self):
    zipObject = zipfile.ZipFile(self.inZip)  
    zipObject.printdir()
    for each_file in zipObject.namelist():
      listOfValues = zipObject.read(each_file).split('\n')
      del listOfValues[-1] 
      self.featureValuesDict[os.path.splitext(each_file)[0]] =  map(int, listOfValues)
    zipObject.close()

  def statsGenerator(self):
    for key in self.featureValuesDict.keys():
      dataToWrite = []
      csvfileName = key+'.csv'
      if not os.path.isfile(csvfileName):
        with open(csvfileName, 'a') as csvfile:
          wr = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
          wr.writerow(['PROCESS', 'MIN', 'MAX', 'MEAN', 'VARIANCE'])
      with open(csvfileName, 'a') as csvfile:
        wr = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
        dataToWrite.append(os.path.splitext(self.inZip)[0])
        valueList = self.featureValuesDict[key]
        dataToWrite.append(np.amin(valueList))
        dataToWrite.append(np.amax(valueList))
        dataToWrite.append(round(np.mean(valueList),2))
        dataToWrite.append(round(np.std(valueList),2)) 
        wr.writerow(dataToWrite)

  def arffGenerator(self):
    dataList = []
    namesList = []
    for key in self.featureValuesDict.keys():
      namesList.append((key,'REAL'))
      dataList.append(self.featureValuesDict[key])
    arffDict = {}
    arffDict['description'] = u''
    arffDict['relation'] = 'perfEvents'
    arffDict['attributes'] = namesList
    arffDict['data'] = zip(*dataList)
    with open(self.outArff, 'w') as f:
      f.write(arff.dumps(arffDict))

  def main(self, argv):
    try:
      opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
    except getopt.GetoptError:
      print 'dataExtractor.py -i <inZip> -o <outArrf>'
      sys.exit(2)
    if(len(opts) != 2):
      print 'dataExtractor.py -i <inZip> -o <outArrf>'     
      exit()
    for opt, arg in opts:
      if opt == '-h':
        print 'dataExtractor.py -i <inZip> -o <outArrf>'
        sys.exit()
      if opt in ("-i", "--ifile"):
        self.inZip = arg
      if opt in ("-o", "--ofile"):
        self.outArff = arg
    print 'Input Zip: ', self.inZip
    print 'Output Arrf: ', self.outArff
    self.zipfileHandler()
    self.statsGenerator()
    self.arffGenerator()
 
if __name__ == "__main__":
   arffObject = ArffGeneration()
   arffObject.main(sys.argv[1:])  
