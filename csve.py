#!/opt/exp/bin/python
# csve - csv (file) evolver
# Filename: csve.py
# May 14~18, 2012
# http://daveti.blog.com
# dave.tian@alcatel-lucent.com
# DEST: csve is used to evolve old csv files of H.248 simulator
# to be updated ones automatically when latest H.248 simulator
# binary is updated accordingly.
# NOTE: for Solaris machines, like lsslogin1 or ih6g2-lngsim2,
# python would locate as above; for Linux machines, like lssxlinux1
# or ATCA labs, python would be '/usr/bin/python'

import os
import sys
import time
import shutil

def printUsage():
	print '''Usuage:
csve srcDir dstDir:
evolve old csv files under dstDir based on new ones under srcDir.
Options:
-h: display help menu.
-q: work under quiet mode (without any warning info).
-d: work under debug mode.
Any comment please email:
	dave.tian@alcatel-lucent.com
'''

def printErrorUsageExit( s):
	print 'Error:', s
	printUsage()
	sys.exit()

def printError( s):
	print 'Error:', s

def printWarningIfNotQuiet( s):
	if not quietMode:
		print 'Warning:', s

def printDebuggingInfoIfEnabled( s, l):
	if debugMode:
		print 'Debugging:', s, l

def reverseMatrixList( l):
	printDebuggingInfoIfEnabled( 'Function:', 'reverseMatrixList')
	printDebuggingInfoIfEnabled( 'l =', l)
	isFieldHeader = False
	totalEleList = []
	rowEleNum = 0
	for row in l:
		rowEleList = row.split( ',')
		if isFieldHeader == False:
			# First row - field header
			isFieldHeader = True
			rowEleNum = len( rowEleList)
		else:
			# Non first row - data
			# Defensive checking
			if rowEleNum != len( rowEleList):
				printError( 'Bad formatted csv data!')
				return None

		totalEleList += rowEleList
	totalEleListLen = len( totalEleList)

	# Debugging info
	printDebuggingInfoIfEnabled( 'totalEleList:', totalEleList)
	printDebuggingInfoIfEnabled( 'rowEleNum:', rowEleNum)
	printDebuggingInfoIfEnabled( 'totalEleListLen:', totalEleListLen)

	# New list reversed constructing
	newListReversed = []
	for i in range( 0, rowEleNum):
		colEleList = totalEleList[ i:totalEleListLen:rowEleNum ]
		colEleStr = ','.join( colEleList)

		# Debugging info
		printDebuggingInfoIfEnabled( 'colEleList:', colEleList)
		printDebuggingInfoIfEnabled( 'colEleStr:', colEleStr)

		# Adding colEleStr into newListReversed
		newListReversed.append( colEleStr)
	return newListReversed

def evolveMatrixListReversed( new, old):
	printDebuggingInfoIfEnabled( 'Function:', 'evolveMatrixListReversed')
	printDebuggingInfoIfEnabled( 'new =', new)
	printDebuggingInfoIfEnabled( 'old =', old)
	# Defensive checking at first
	# Before doing any evolving, we take assumptions here:
	# 1. number of rows of new >= the ones of old
	# 2. number of rows of new/old > 0
	rowNumOfNew = len( new)
	rowNumOfOld = len( old)
	if rowNumOfNew < rowNumOfOld:
		printError( 'new csv file is older than original one!')
		return None
	elif rowNumOfNew <= 0 or rowNumOfOld <= 0:
		printError( 'invalid new/old parameters!')
		return None

	# Column preprocessing
	colNumOfNew = len( new[ 0].split( ','))
	colNumOfOld = len( old[ 0].split( ','))
	adjustNum = colNumOfNew - colNumOfOld

	# Debugging info
	printDebuggingInfoIfEnabled( 'rowNumOfNew:', rowNumOfNew)
	printDebuggingInfoIfEnabled( 'rowNumOfOld:', rowNumOfOld)
	printDebuggingInfoIfEnabled( 'colNumOfNew:', colNumOfNew)
	printDebuggingInfoIfEnabled( 'colNumOfOld:', colNumOfOld)
	printDebuggingInfoIfEnabled( 'adjustNum:', adjustNum)

	# Data evolving
	evoListReversed = []
	rowEle = []
	idxOfOld = 0
	for i in range( 0, rowNumOfNew):
		# Debugging info
		printDebuggingInfoIfEnabled( 'index for new, i:', i)
		printDebuggingInfoIfEnabled( 'index for old, idxOfOld:', idxOfOld)

		if new[ i].split( ',')[ 0] == old[ idxOfOld].split( ',')[ 0]:
			# Using old data
			rowEle = old[ idxOfOld]
			idxOfOld += 1
			printDebuggingInfoIfEnabled( 'using old data:', rowEle)
		else:
			# Using new data
			# Making sure new data line-up with old one
			if adjustNum == 0:
				# No change
				rowEle = new[ i]
				printDebuggingInfoIfEnabled( 'using new data - no change:', rowEle)
			elif adjustNum > 0:
				# Element truncating
				rowEle = ','.join( new[ i].split( ',')[ 0:( colNumOfNew - adjustNum)])
				printDebuggingInfoIfEnabled( 'using new data - truncating:', rowEle)
			else:
				# Element padding with last element
				splitedEle = new[ i].split( ',')
				lastEle = splitedEle[ -1]
				splitedEle.append( lastEle)
				rowEle = ','.join( splitedEle)
				printDebuggingInfoIfEnabled( 'using new data - padding:', rowEle)

		# Adding the rowEle into evoListReversed
		evoListReversed.append( rowEle)
	return evoListReversed

# Global var
srcDir = ''
dstDir = ''
quietMode = False
debugMode = False
csvFileList = [ 'atmRsrc.csv',
		'callLoad.csv',
		'codecRsrc.csv',
		'gateways.csv',
		'gui.csv',
		'h248msg.csv',
		'h248pkg.csv',
		'ipRsrc.csv',
		'localRsrc.csv',
		'msiCodecRsrc.csv',
		'msiRsrc.csv',
		'sctpProfile.csv',
		'signalsEventsNotify.csv',
		'statistics.csv',
		'streamIpRsrc.csv',
		'system.csv',
		'tdmRsrc.csv',
		'termId.csv',
		'trans.csv' ]

# Arguments processing
for i in range( 1, len( sys.argv)):
	if sys.argv[ i] == '-h':
		printUsage()
		sys.exit()
	elif sys.argv[ i] == '-q':
		quietMode = True
	elif sys.argv[ i] == '-d':
		debugMode = True
	elif srcDir == '':
		srcDir = sys.argv[ i]
	elif dstDir == '':
		dstDir = sys.argv[ i]
	else:
		printErrorUsageExit( 'too many arguments!')

# Arugments validation
if srcDir == '' or dstDir == '':
	printErrorUsageExit( 'too few arguments!')
elif not os.path.exists( srcDir):
	printErrorUsageExit( 'srcDir does not exist!')
elif not os.path.exists( dstDir):
	printErrorUsageExit( 'dstDir does not exist!')
elif not quietMode:
	# System logging
	print 'Src dir:', srcDir
	print 'Dst dir:', dstDir
	print 'Quiet Mode:', quietMode
	print 'Debug Mode:', debugMode

# Original csv file backup
backupDir = dstDir + os.sep + time.strftime( '%Y%m%d%H%M%S') + '_bk'
os.mkdir( backupDir)
if not quietMode:
        print 'Backup dir:', backupDir
for c in csvFileList:
	backupFile = dstDir + os.sep + c
	if os.path.exists( backupFile):
		shutil.move( backupFile, backupDir)
		# Debugging info
		printDebuggingInfoIfEnabled( backupFile, 'is moved')
	else:
		printWarningIfNotQuiet( 'file does not exist - ' + backupFile)

# Evolving csv file
for f in csvFileList:
	# Checking file existence at first
	dstFile = backupDir + os.sep + f
	srcFile = srcDir + os.sep + f
	newFile = dstDir + os.sep + f
	
	# Debugging info
	printDebuggingInfoIfEnabled( 'dstFile:', dstFile)
	printDebuggingInfoIfEnabled( 'srcFile:', srcFile)
	printDebuggingInfoIfEnabled( 'newFile:', newFile)
	
	if not os.path.exists( dstFile) and not os.path.exists( srcFile):
		printWarningIfNotQuiet( 'neither dstFile nor srcFile exists!')
		printWarningIfNotQuiet( 'dstFile: ' + dstFile)
		printWarningIfNotQuiet( 'srcFile: ' + srcFile)
		# Just moving on
	elif not os.path.exists( dstFile) and os.path.exists( srcFile):
		printWarningIfNotQuiet( 'dstFile dose not exists!')
		printWarningIfNotQuiet( 'dstFile: ' + dstFile)
		# Just copying the srcFile
		shutil.copy( srcFile, dstDir)
		print 'copied:', srcFile
	elif os.path.exists( dstFile) and not os.path.exists( srcFile):
		printWarningIfNotQuiet( 'srcFile dose not exists!')
		printWarningIfNotQuiet( 'srcFile: ' + srcFile)
		# Just copying the dstFile
		shutil.copy( dstFile, dstDir)
		print 'copied:', dstFile
	else:
		try:
			# The most complicated case here...
			# File opening
			dstFileObj = open( dstFile)
			srcFileObj = open( srcFile)
			newFileObj = open( newFile, 'w')

			# NOTE: always assume the first non comment line is header!
			# Comments within data lines are NOT supported by csve!

			# srcFile processing
			srcCommentList = []
			srcDataList = []
			isDataLine = False
			while True:
				line = srcFileObj.readline()
				# Deleting the suffix '\n'
				line = line.rstrip()

				if len(line) == 0:
					break
				else:
					# Debugging info
					printDebuggingInfoIfEnabled( 'line:', line)

					if line.startswith('#') and isDataLine == False:
						# Comment line - copy the comment to srcCommentList
						srcCommentList.append( line)
					else:
						# Data line - copy the data to srcDataList
						srcDataList.append( line)
						isDataLine = True

                        # Matrix list reversing
                        srcDataListReversed = reverseMatrixList( srcDataList)
			if srcDataListReversed == None:
				printError( 'srcDataListReversed generation failure!')
				# Just moving on to the next csv file
				continue

			# Debugging info
			printDebuggingInfoIfEnabled( 'srcCommentList:', srcCommentList)
			printDebuggingInfoIfEnabled( 'srcDataList:', srcDataList)
			printDebuggingInfoIfEnabled( 'srcDataListReversed:', srcDataListReversed)

			# dstFile processing
			dstDataList = []
			isDataLine = False
			while True:
				line = dstFileObj.readline()
				# Deleting the suffix '\n'
				line = line.rstrip()

				if len(line) == 0:
					break
				else:
                                        # Debugging info
                                        printDebuggingInfoIfEnabled( 'line:', line)

					if line.startswith('#') and isDataLine == False:
						# Comment line - ignore
						continue
					else:
						# Data line - copy the data to dstDataList
						dstDataList.append( line)
						isDataLine = True

			# Matrix list reversing
			dstDataListReversed = reverseMatrixList( dstDataList)
			if dstDataListReversed == None:
				printError( 'dstDataListReversed generation failure!')
				# Just moving on to the next csv file
				continue

                        # Debugging info
                        printDebuggingInfoIfEnabled( 'dstDataList:', dstDataList)
                        printDebuggingInfoIfEnabled( 'dstDataListReversed:', dstDataListReversed)

			# Evolving csv data
			newDataListReversed = evolveMatrixListReversed( srcDataListReversed, dstDataListReversed)
			if newDataListReversed == None:
				printError( 'newDataListReversed generation failure!')
				# Just moving on to the next csv file
				continue 
			newDataList = reverseMatrixList( newDataListReversed)
			if newDataList == None:
				printError( 'newDataList generation failure!')
				# Just moving on to the next csv file
				continue

			# Debuggging info
			printDebuggingInfoIfEnabled( 'newDataListReversed:', newDataListReversed)
			printDebuggingInfoIfEnabled( 'newDataList:', newDataList)

			# newFile constructing
			newFileList = [ (line+'\n') for line in (srcCommentList+newDataList)]
			printDebuggingInfoIfEnabled( 'newFileList:', newFileList)
			newFileObj.writelines( newFileList)
			print 'evolved:', newFile

		finally:
			# File closing
			dstFileObj.close()
			srcFileObj.close()
			newFileObj.close()

print 'Thank you for using csve - done:)'
