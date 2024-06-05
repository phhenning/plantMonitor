
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
	print("Provide a name for dataset and optional pass/fail and profile template") 
	print("eg -name=test1 --fail=false ") 

parser = argparse.ArgumentParser()
parser.add_argument( "--name", help="name of dataset")
parser.add_argument( "--fail", help="set to true if  profile should produce bad data", default = False)
parser.add_argument( "--file", help="file name of profile to use", default = "template.csv")
parser.add_argument( "--port", help="http port to which to publish", default = 8765)
parser.add_argument( "--loop", help="keep looping", default = True)
parser.add_argument( "--period", help="period in seconds, at witch to update sample value", default = 60*15)

args = parser.parse_args()

if args.name == "None":
	printHelp()
	quit()


name = args.name.replace(" ", "_")

print( "DataSet name {} pass {} template {} publishing to {}:{}" .format(
	args.name,
	not args.fail,
	args.file,
	socket.gethostbyname(socket.gethostname()) ,
	args.port
))


class samplePoint:
	def __init__(self, n, t, gp, bp):
			self.n = n    	# time
			self.t = t		# temperature
			self.gp = gp	# good pH	
			self.bp = bp    # bad pH

# read csv file into data array 
data = []
with open(args.file, newline='') as csvfile:
	reader = csv.DictReader(csvfile)
	for row in reader:
		tmp = samplePoint(row['time'], row['Temp'], row['good_pH'], row['bad_pH'])
		data.append(tmp)



gaugeTemp = Gauge(name+'_temp', 'sample temperature measurement' )
gaugePh = Gauge(name+'_ph', 'sample ph measurement')


if __name__ == '__main__':
	# Start up the server to expose the metrics.
	start_http_server(8000)

	doLoop = True
	while doLoop: 					# do for loop at least once
		for d in data:
			temp =  float(d.t)  + 	random.randrange(-3,3) * random.random() # add random nes around template value

			# publish good or bad pH
			if args.fail :
				ph =  float(d.gp)  + 	random.randrange(-1,1) * random.random() # add random nes around template value
			else :
				ph =  float(d.bp)  - 	random.randrange(-1,1) * random.random() # add random nes around template value

			gaugeTemp.set(temp)
			gaugePh.set(ph)
			print(temp , "   ", ph ) 
			time.sleep(args.period)
		doLoop = args.loop		# load loop instruction from command line

