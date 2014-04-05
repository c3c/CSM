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
$ python gurobi.py
Loading hashlist... (cached)
Calculating overlap between tuples...
Running MIP optimization...
...
Objective:  454686.0
Phys #0 (6144M): 3, 4, 6, 7, 8, 9, a
Phys #2 (4096M): b, d
Phys #3 (4096M): 1, 2, 5, c

```
