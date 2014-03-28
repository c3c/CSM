#!/usr/bin/python

#from sets import Set
#import re
#import sys
import os
#from pyhashxx import hashxx
from pprint import pprint
import itertools
#from ast import literal_eval
import time


memdumps = []

hashdict = {}
freq_table = {}
working_dict = {}

physical_hosts = {"server1": 5391456, "server2": 4291455, "server3": 4200000}
physical_hosts_working = physical_hosts.keys()

## {VM: {MEM: INT (KB)}}
virtual_machines = {'win': {'mem': 4145152}, 'randomserver1gb': {'mem': 1048576}, 'randomserver2gb':{'mem': 2097152},
                    'shuttleworth1': {'mem': 786432}, 'shuttleworth2': {'mem': 786432},
                    'shuttleworth3': {'mem': 786432}, 'shuttleworth4': {'mem': 786432},
                    'shuttleworth5': {'mem': 786432}, 'shuttleworth6': {'mem': 786432},
                    'shuttleworth7': {'mem': 786432}, 'shuttleworth8': {'mem': 786432}}


## "119677106" == null pages

## dict of placed vms on physical servers: {"server1": [VM1, VM2, VM3]}
deployed = {}   
deployed_bla = []

overprovision = 125

result_temp = []

dedupe_result_kb = 0



def max_group(pair_dict, pair, pair_duplicates, server):
    #print pair, " - ", server
    global best_vm
    total_mem = 0
    total_deduplicated_mem = 0
    for item in pair:
        total_mem += virtual_machines[item]['mem']

    print " Total: ",total_mem
    print " Duplicates in pair: ",pair_duplicates,"\n"

    total_deduplicated_mem = total_mem - pair_duplicates * 4

    result_dict = {}
    #result_list.append(pair[0])
    #result_list.append(pair[1])

    deployed[server] = [pair[0], pair[1]]

    duplicate_count = 0
    while True:
    #while total_mem < physical_hosts[server]:

        result_dict = {}
        intersect = {}
        for vm in virtual_machines:
            if vm not in deployed_bla:
                if virtual_machines[vm]['mem'] + total_mem < (
                            overprovision * physical_hosts[server] / 100): # If the vm doesnt break the OP, test it:
                    intersect[vm] = hashdict[vm].viewkeys() & pair_dict.viewkeys()
                    for duplicate in intersect[vm]:
                        duplicate_count += hashdict[vm][duplicate]
                    #if (total_mem + virtual_machines[vm]['mem'] - duplicate_count * 4) < physical_hosts[server]:
                    if (total_deduplicated_mem + virtual_machines[vm]['mem'] - duplicate_count * 4) < physical_hosts[server]:
                        result_dict[vm] = duplicate_count
                    duplicate_count = 0
        max_pair_count = 0
        for x in result_dict:
            if result_dict[x] > max_pair_count:
                max_pair_count = result_dict[x]
                best_vm = x
        #print max_pair_count
        if not best_vm:
            break
        else:
            #print best_vm
            #del virtual_machines[best_vm]
            deployed_bla.append(best_vm)
            deployed[server].append(best_vm)
            total_mem += virtual_machines[best_vm]['mem']
            for hasj in hashdict[best_vm]:
                if hasj in freq_table:
                    if hasj in pair_dict:
                        pair_dict[hasj] += hashdict[best_vm][hasj]
                    else:
                        pair_dict[hasj] = hashdict[best_vm][hasj]

            total_deduplicated_mem += virtual_machines[best_vm]['mem'] - (max_pair_count * 4)
            best_vm = None
    deduped = [total_mem, total_deduplicated_mem]
    #print deduped
    return deployed[server], deduped



print("Load memdumps from file...")

for dirname, dirnames, filenames in os.walk('./dumps/'):
    for file in filenames:
        if file.endswith('.dat'):
            memdumps.append(os.path.join(dirname, file))


## First create a global frequency table to determine which pages are certainly not duplicate.
for dmp in memdumps:
    memdump = open(dmp, "r")
    for line in memdump.readlines():
        try:
            hashvalue = line.split(" ")[0][1:]
            hashcount = int(line.split(" ")[1].split(">")[0])
            if hashvalue != "ashes" and hashvalue != "}]" and hashvalue != "119677106": # Also leave out Null pages
                if hashvalue in freq_table:
                    freq_table[hashvalue] += hashcount
                else:
                    freq_table[hashvalue] = hashcount
        except:
            pass
    memdump.close()

## We only want the (globally) duplicate pages
for key in freq_table.keys():
    if freq_table[key] == 1:
        del freq_table[key]

## Load individual VMs into hashtables now
for dmp in memdumps:
    memdump = open(dmp, "r")
    dumpname = dmp.split("/")
    dumpname.reverse()
    dumpname = dumpname[0].split(".")[0]

    hashdict[dumpname] = {}
    for line in memdump.readlines():
        try:
            hashvalue = line.split(" ")[0][1:]
            hashcount = int(line.split(" ")[1].split(">")[0])
        except:
            pass

        if hashvalue not in freq_table:
            pass
        else:
            hashdict[dumpname][hashvalue] = hashcount
    memdump.close()

print("Hashtables are loaded... \n")


## Time to free up some memory:
#freq_table = None

i = 1
#while len(hashdict) > 0:
while i == 1:
    ## Start to place the optimal pair on the biggest available server in physical_servers{}: ( We wont look into a scenario where ultimately a single VM may be too big for a single server...?
    ## Determine biggest available server.
    biggest_mem = 0
    #print physical_hosts_working
    for server in physical_hosts_working:
        if physical_hosts[server] > biggest_mem and server not in deployed:
            #print server
            #print physical_hosts[server]
            biggest_mem = physical_hosts[server]
            #print biggest_mem
            biggest = server
            ## Determine pair of VMs with most # overlapping pages
    working_dict = {}
    duplicate_count = 0
    max_duplicates = 0
    best_pair = None
    for item in itertools.combinations(hashdict.keys(), 2):
    #print itertools.combinations(hashdict.keys(), 2)
    #print item[0], item[1]
        #max_duplicates = 0
        duplicate_count = 0
        if item[0] not in deployed_bla and item[1] not in deployed_bla:
        #print item
        #print literal_eval(str(item)) ## convert string (key) back to tuple ######################################
            working_dict[str(item)] = {}
            intersect = hashdict[item[1]].viewkeys() & hashdict[item[0]].viewkeys()
            #print intersect
            for duplicate in intersect:
                #temp_duplicate = 0
                working_dict[str(item)][duplicate] = temp_duplicate = hashdict[item[1]][duplicate] + \
                                                                      hashdict[item[0]][duplicate] - 1
                duplicate_count += temp_duplicate
            pair_mem = virtual_machines[item[0]]['mem'] + virtual_machines[item[1]]['mem']

            if pair_mem < physical_hosts[biggest] and (pair_mem - (duplicate_count * 4)) < physical_hosts[biggest] * overprovision / 100:
                #print "BLA"
                if duplicate_count > max_duplicates:
                    #pair_dict = {}
                    pair_dict = working_dict[str(item)]
                    max_duplicates = duplicate_count
                    best_pair = item
            else:
                #print "Won't fit"
                pass
    working_dict = None
    if not best_pair:
        print "Error, no pair was found for:"
        if len(virtual_machines) - len(deployed_bla) == 1:
            lonely_soul = list(set(virtual_machines.keys()) - set(deployed_bla))[0]
            print "   Lonely soul: ", lonely_soul
            if len(physical_hosts_working) > 0:
                # We still  have an unassigned machine. We couldn't pair the lonely_soul with any other VMs any way.
                biggest_mem_left = 0
                #print physical_hosts_working
                for server_lonely in physical_hosts_working:
                    if physical_hosts[server_lonely] > biggest_mem_left and server_lonely not in deployed:
                        biggest_mem_left = physical_hosts[server_lonely]
                        biggest_left = server_lonely
                    #print biggest_left
                if virtual_machines[lonely_soul]['mem'] < physical_hosts[biggest_left]:
                    deployed[biggest_left] = [lonely_soul]
                    print "   ", lonely_soul, " was deployed at: ", biggest_left
                #dedupe_result_kb -= virtual_machines[lonely_soul]['mem'] # .......
        print "Done 2"
        i = 0
    else:
        print "Elected server: ", biggest, ". Testing pair: ", best_pair
        deployed_bla.append(best_pair[1])
        deployed_bla.append(best_pair[0])
        resultaat, deduped = max_group(pair_dict, best_pair, max_duplicates,biggest)
        dedupe_result_kb += (deduped[0] - deduped[1])
        #print dedupe_result_kb
        physical_hosts_working.remove(biggest)

        if len(deployed_bla) == len(virtual_machines):
            print "Done"
            i = 0
        #break

print "\n'Optimal' deployment of VMs:\n"
pprint(deployed)

print "\nTotal savings with deployment: ",dedupe_result_kb, " (", float(dedupe_result_kb / 1024) , "MB)"

non_deduped_mem = 0
for key in virtual_machines:
    non_deduped_mem += virtual_machines[key]['mem']

print"\nThis is ", round(float(dedupe_result_kb) / float(non_deduped_mem) * 100, 1), "% improved."
