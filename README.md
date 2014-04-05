Cluster Samepage Merging
========================

Cluster Samepage Merging (CSM) is the optimization of VM placement in larger clusters in order to maximize memory density. 

CSM is inspired by Kernel Samepage Merging (KSM), which is a technique used to determine duplicate memory blocks. This is especially of interest on hypervisors where multiple virtual machines may be able to share a large number of memory segments. The current use of KSM limits itself to improving the memory use on a per host base. In large environments it may be interesting to find a more optimal deployment of virtual machines, consolidating virtual machines with duplicate memory segments onto the same host.

The specifics of the proposed algorithms can be found in the [research paper](csm.pdf?raw=true).

  * __max_sharing.mod__: a CPLEX model that aims to maximize the number of _sharing_ pages.
  * __max_shared.mod__: a simplified CPLEX model that aims to maximize the number of _shared_ pages.
  * __greedy.py__: a Python implementation for the greedy fat-first approach.
  * __pairoverlap.py__: a Python implementation of the VM pair overlap model, which interfaces to the Gurobi solver.

All models read in data files that are in fact dumps of data structures that hold hashed memory pages of virtual machines.

```
$ python greedy.py
Load memdumps from file...
Hashtables are loaded...

Elected server:  server1 . Testing pair:  ('shuttleworth8', 'shuttleworth7')
 Total:  1572864
 Duplicates in pair:  94594

Elected server:  server2 . Testing pair:  ('randomserver1gb', 'randomserver2gb')
 Total:  3145728
 Duplicates in pair:  9770

Error, no pair was found for:
   Lonely soul:  win
    win  was deployed at:  server3
Done 2

'Optimal' deployment of VMs:

{'server1': ['shuttleworth8',
             'shuttleworth7',
             'shuttleworth6',
             'shuttleworth2',
             'shuttleworth1',
             'shuttleworth5',
             'shuttleworth4',
             'shuttleworth3'],
 'server2': ['randomserver1gb', 'randomserver2gb'],
 'server3': ['win']}

Total savings with deployment:  1021040  ( 997.0 MB)

This is  7.5 % improved.
```

```
n$ python pairoverlap.py
Loading hashlist... (cached)
Calculating overlap between tuples...
Running MIP optimization...
Optimize a model with 953 rows, 364 columns and 2288 nonzeros
Found heuristic solution: objective 50839
Presolve time: 0.02s
Presolved: 953 rows, 364 columns, 3224 nonzeros
Variable types: 0 continuous, 364 integer (364 binary)

Root relaxation: objective 5.032360e+05, 542 iterations, 0.01 seconds

    Nodes    |    Current Node    |     Objective Bounds      |     Work
 Expl Unexpl |  Obj  Depth IntInf | Incumbent    BestBd   Gap | It/Node Time

     0     0 503236.000    0  273 50839.0000 503236.000   890%     -    0s
H    0     0                    72370.000000 503236.000   595%     -    0s
H    0     0                    287318.00000 503236.000  75.1%     -    0s
     0     0 503185.324    0  362 287318.000 503185.324  75.1%     -    0s
H    0     0                    343436.00000 503185.324  46.5%     -    0s
     0     0 502704.641    0  352 343436.000 502704.641  46.4%     -    0s
H    0     0                    345739.00000 502704.641  45.4%     -    0s
     0     0 502676.808    0  353 345739.000 502676.808  45.4%     -    0s
     0     0 502660.859    0  354 345739.000 502660.859  45.4%     -    0s
     0     0 502639.118    0  353 345739.000 502639.118  45.4%     -    0s
     0     0 502631.120    0  355 345739.000 502631.120  45.4%     -    0s
     0     0 502630.520    0  357 345739.000 502630.520  45.4%     -    0s
     0     0 502630.520    0  357 345739.000 502630.520  45.4%     -    0s
H    0     0                    414832.00000 502630.520  21.2%     -    0s
     0     3 502630.520    0  357 414832.000 502630.520  21.2%     -    0s
*   10     2               8    441172.00000 502599.934  13.9%  68.2    0s
H   12     2                    454686.00000 502599.934  10.5%  57.0    0s

Cutting planes:
  Gomory: 15
  Cover: 2
  Zero half: 6
  Mod-K: 22

Explored 31 nodes (2193 simplex iterations) in 0.59 seconds
Thread count was 4 (of 4 available processors)

Optimal solution found (tolerance 1.00e-04)
Best objective 4.546860000000e+05, best bound 4.546860000000e+05, gap 0.0%
Objective:  454686.0
Phys #0 (6144M): 3, 4, 6, 7, 8, 9, a
Phys #2 (4096M): b, d
Phys #3 (4096M): 1, 2, 5, c
```
