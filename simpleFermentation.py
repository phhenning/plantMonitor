
import argparse
import csv
import random
import time
import socket

from prometheus_client import start_http_server, Summary, Gauge

# script will publish  temp and ph for a process
# sample name is require - by default teh  successful profile is generated
# optional fail parameter can be used to  generate a failed process 
# the process curve template can is defined in csv file 
#     template.csv is used as default
#     you can pass a 


def printHelp():
	print("Number of datasets must be larger or equal to number of failed sets ") 
	print("eg --count=10 --fail=2 ") 

parser = argparse.ArgumentParser()
parser.add_argument( "--count", help="number of datasets", default = 10)
parser.add_argument( "--fail", help="set to number of failed profiles", default = 2)
parser.add_argument( "--file", help="file name of profile to use", default = "template.csv")
parser.add_argument( "--port", help="http port to which to publish", default = 8765)
parser.add_argument( "--loop", help="keep looping", default = True)
parser.add_argument( "--period", help="period in seconds, at witch to update sample value", default = 60*15)

args = parser.parse_args()

if int(args.count) < int (args.fail):
	printHelp()
	quit()



address = socket.getaddrinfo(socket.gethostname(), None) 
print( "DataSet count {}, fail {} template {} publishing to {}:{}" .format(
	args.count,
	args.fail,
	args.file,
	(address[0][4][0]),
	args.port
))


class samplePoint():
	def __init__(self, n, t, gp, bp):
			self.n = n    	# time
			self.t = t		# temperature
			self.gp = gp	# good pH	
			self.bp = bp    # bad pH

# read csv file into data array 
csvData = []
with open(args.file, newline='') as csvfile:
	reader = csv.DictReader(csvfile)
	for row in reader:
		tmp = samplePoint(row['time'], row['Temp'], row['good_pH'], row['bad_pH'])
		csvData.append(tmp)


class sampleGauges():
	def __init__(self, t, p):
		self.temp = t
		self.ph = p

gaugeSets = []
failIndex = [] 	# index if datasets with failed values
while len(failIndex) < int(args.fail):
	x = random.randint(1,int(args.count))
	if x not in failIndex:
		failIndex.append(x)

#make all gauges
for i in range(int(args.count)):
	tg = Gauge('sample_'+ str(i) +'_temp', 'sample ' +  str(i) + ' temperature measurement' ,['measurement'] )
	pg = Gauge('sample_'+ str(i) +'_ph', 'sample ' + str(i) + ' ph measurement',['measurement'] )
#	tg.labels(measurement='temperature')
#	pg.labels(measurement='ph').inc()
	gaugeSets.append(sampleGauges(tg,pg))


if __name__ == '__main__':
	# Start up the server to expose the metrics.
	start_http_server(int(args.port))

	doLoop = True
	while doLoop: 					# do for loop at least once
		for d in csvData:			#use next value in csv data set
			for i in range (int(args.count)):
				temp =  float(d.t)  + 	random.randrange(-3,3) * random.random() # add random nes around template value
				if i in failIndex:
					ph =  float(d.bp)  - 	random.randrange(-1,1) * random.random() # add random nes around template value
				else:	
					ph =  float(d.gp)  + 	random.randrange(-1,1) * random.random() # add random nes around template value
				gaugeSets[i].temp.labels(measurement='temperature').set(temp)
				gaugeSets[i].ph.labels(measurement='ph').set(ph)
				print(temp , "   ", ph ) 
			time.sleep(int(args.period))
			
	doLoop = args.loop		# load loop instruction from command line
print("done")
