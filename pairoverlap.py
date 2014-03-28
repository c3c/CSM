from pprint import pprint
import cPickle
import glob
import sys
from itertools import *
import os.path
import pyhashxx
from UserDict import UserDict
import random
import operator
from gurobipy import *

nulhash = int(pyhashxx.hashxx('\0' * 4096)/10)

freq = {}
tables = []
fi = 0
frqc = 0

if os.path.isfile("dumps/dumps.cache"):
	print "Loading hashlist... (cached)"
	(frqc, tables) = cPickle.load(open("dumps/dumps.cache", "rb"))
else:
	print "Loading hashes and purging sole occurences"
	for file in sorted(glob.glob("dumps/*.dump")):
		tp = cPickle.load(open(file, "rb"))
		table = UserDict(tp)
		table.filename = os.path.basename(file).replace(".dump","")
		table.idx = fi
		fi += 1
		table.memory = (768,1024)[random.randint(0,1)]
		tables.append(table)
		for k,v in table.items():
			freq[k] = freq.get(k, 0) + v
		print("Length of table %s: %d" % (file, len(table)))

	print("Length of freqtable: %s" % len(freq))

	for k,v in freq.items():
		if v == 1 or k == nulhash:
			del freq[k]
			for table in tables:
				if k in table:
					del table[k]
		else:
			frqc+=v

	print("Length of freqtable after purging of non-shareable pages: %s" % len(freq))

	cPickle.dump((frqc, tables), open("dumps/dumps.cache", "wb"))

#for table in tables:
#	print("Length of table %s: %d" % (table.filename, len(table)))

#sv = tables[0]

def calc_overlap(t1, t2):
	lap = 0
	lap2 = 0
	for k,v in t1.items():
		ct2 = t2.get(k, None)
		if ct2 != None:
			lap += v + ct2
			lap2 += 1
	return [lap, lap2]


## MIP problem

physicals = [1024*6,1024*4,1024*4,1024*4] # We have 10 physical machines with 6GB RAM each

solver = Model("cfg")
#solver.setParam('OutputFlag', False)

combos = []
overlap = {}
x = {}
y = {}

# Initialize (decision) variables

print "Calculating overlap between tuples..."

for t1,t2 in combinations(tables, 2):
	#(lap, lap2) = calc_overlap(t1, t2)
	lap2 = len(t1.data.viewkeys() & t2.data.viewkeys())
	combos.append((t1.idx, t2.idx))
	overlap[(t1.idx, t2.idx)] = lap2	
	
	for phid in range(len(physicals)):
		# dvar: pair of VMs are placed together on the same physical machine
		x[(phid, t1.idx, t2.idx)] = solver.addVar(vtype=GRB.BINARY, name='x[%i,%i,%i]' % (phid, t1.idx, t2.idx))
		
for t in tables:
	# dvar: a VM is placed on a certain physical machine
	for phid in range(len(physicals)):
		y[(phid, t.idx)] = solver.addVar(vtype=GRB.BINARY, name='y[%i,%i]' % (phid, t.idx))


#for phid in range(len(physicals)):
#	sharing[phid] = solver.IntVar(0, frqc, 'sharing[%i]' % phid)

# Objective

solver.update()
solver.setObjective(quicksum(x[(phid, t1, t2)] * overlap[(t1, t2)]
		for t1,t2 in combos
		for phid in range(len(physicals))), GRB.MAXIMIZE)

# Constraints

for t in tables:
	# VM can only be on one physical host
	solver.addConstr(quicksum([y[(phid, t.idx)] for phid in range(len(physicals))]) == 1)

for phid,pmem in enumerate(physicals):
	# Memory constraints
	solver.addConstr(quicksum([y[(phid, t.idx)] * t.memory for t in tables]) <= pmem)

	for t1,t2 in combos:
		# Logical AND
		solver.addConstr(y[(phid,t1)] >= x[(phid,t1,t2)])
		solver.addConstr(y[(phid,t2)] >= x[(phid,t1,t2)])
		solver.addConstr(y[(phid,t1)]+y[(phid,t2)] <= x[(phid,t1,t2)]+1)

# Gogogo

print "Running MIP optimization..."

solver.optimize()

print "Objective: ", solver.objVal

for phid,pmem in enumerate(physicals):
	located = [t.filename for t in tables if y[(phid,t.idx)].x==1]
	if len(located) > 0:
	        sys.stdout.write("Phys #%d (%dM): " % (phid, pmem))
		sys.stdout.write(", ".join(located))
		print
