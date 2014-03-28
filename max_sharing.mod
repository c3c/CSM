/*********************************************
 * OPL 12.5 Model
 * Author: Cedric Van Bockhaven, Mike Berkelaar
 * Creation Date: 7-mrt.-2014 at 19:03:18
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

// Main

dvar boolean newLocation[Physicals,Virtuals];
dvar int+ freq[p in Physicals,h in hashs];
dvar boolean shared[p in Physicals, h in hashs];
dvar int+ sharing[p in Physicals, h in hashs];

dexpr int sharingPages[p in Physicals] = sum (h in hashs) sharing[p,h];
maximize sum(p in Physicals) sharingPages[p];

subject to {
  	// every VM has to be relocated somewhere
	forall (v in Virtuals) {
	  	sum (p in Physicals) newLocation[p,v] == 1;
 	}
 	
 	// memory limits per physical machine
 	forall (p in Physicals) {
 		(sum (v in Virtuals) newLocation[p,v]*v.memory)-4*sharingPages[p] <= p.memory; 		
 		
 		forall (hid in hashs) {
 			// profit of set slicing
			freq[p,hid] == sum (v in Virtuals, <hid,num> in Hashes[v]) (newLocation[p,v] * num);
			
			freq[p,hid] >= 2*shared[p,hid];
			freq[p,hid] <= 1+M*shared[p,hid];
			freq[p,hid]-1 <= sharing[p,hid];
			sharing[p,hid] <= freq[p,hid]-shared[p,hid];
			sharing[p,hid] <= M*shared[p,hid];
 		}		  
  	}
}
