/*********************************************
 * OPL 12.5 Model
 * Author: Cedric Van Bockhaven, Mike Berkelaar
 * Creation Date: 7-mrt.-2014 at 18:05:20
 *********************************************/
 
tuple PhysMachine {
	key int id;
	int memory;
}   

tuple VirtMachine {
 	key int id;
	int memory; 
}

tuple HashTup {
	key int id;
	int num; 
}

// Read from data

{PhysMachine} Physicals = { <i,384*1024> | i in 1..5 };
{VirtMachine} Virtuals = { <i,64*1024> | i in 1..24 };
{HashTup} Hashes[Virtuals] = ...;
sorted {int} hashs = { h.id | v in Virtuals, h in Hashes[v] };

int M = 10000000;
int q = 3;

// Main

dvar boolean newLocation[Physicals,Virtuals];
dvar boolean shared[p in Physicals, h in hashs];

dexpr int sharedPages[p in Physicals] = sum (h in hashs) shared[p,h];
maximize sum(p in Physicals) sharedPages[p];

subject to {
  	// every VM has to be relocated somewhere
	forall (v in Virtuals) {
	  	sum (p in Physicals) newLocation[p,v] == 1;
 	}
 	
 	// memory limits per physical machine
 	forall (p in Physicals) {
 		(sum (v in Virtuals) newLocation[p,v]*v.memory)-4*q*sharedPages[p] <= p.memory; 		
 		
 		forall (hid in hashs) {
			shared[p,hid] == ((sum (v in Virtuals, <hid,num> in Hashes[v]) newLocation[p,v]) >= 2);
 		}		  
  	}
}
