#initialize MPI enviroment and import need module
import time
from mpi4py import MPI
import numpy as np
comm = MPI.COMM_WORLD
comm_rank = comm.Get_rank()
comm_size = comm.Get_size()


def generate_local_arrays(comm_rank):#function to generate original array
    if comm_rank == 0: #for root node, fenereate original array
        original_data = np.random.randint(1, 50000, (n,), dtype='i')
        if True:
            print('original data:',end=' ')#output the original array
            for j in range(len(original_data)-1):
                print(original_data[j],end=' ')#output the original array
            print(original_data[len(original_data)-1])
    else:
        original_data = None
    local_data = np.empty((int(n / comm_size),), dtype='i')#use scatter to distribute subarrays to each process
    comm.Scatter(original_data, local_data, root=0)
    return local_data

def ite_of_phase(local_data,partner):
    partner_data = np.empty(local_data.size, dtype='i')
    comm.Sendrecv(local_data, dest=partner, recvbuf=partner_data, source=partner)
    data=np.concatenate([local_data, partner_data])
    #print(data,comm_rank,partner)
    data=odd_even_sort(data)
    if comm_rank < partner:
        return data[:local_data.size]
    else:
        return data[local_data.size:]
def odd_even_sort(num_array):
    flag=True
    for i in range(len(num_array)-1):
        if flag:
            flag=False
            for j in range(1,len(num_array)-1,2):
                if num_array[j]>num_array[j+1]:
                    flag=True
                    num_array[j],num_array[j+1]=num_array[j+1],num_array[j]
            for j in range(0,len(num_array)-1,2):
                if num_array[j]>num_array[j+1]:
                    flag=True
                    num_array[j],num_array[j+1]=num_array[j+1],num_array[j]
    return(num_array)
def check_partner(p):#make sure the partner's rank is in the range 
    if p < 0 or p>=comm_size:
        return None
    else:
        return p
def get_partners(a):#get the partner rank for even phase and odd pahse
    if comm_rank%2 == 0:
        even_partner=check_partner(comm_rank+1)
        odd_partner=check_partner(comm_rank-1)
    else:
        even_partner=check_partner(comm_rank-1)
        odd_partner=check_partner(comm_rank+1)
    if a==0:
        return even_partner
    else:
        return odd_partner

def parallel_sort(local_data):
    for phase in range(comm_size):
        partners=get_partners(phase%2)
        if partners != None:
            data=ite_of_phase(local_data, partners)
            local_data=data
            #print(local_data,comm_rank,partners)
    return local_data

def gather_to_root_node(local_data):# get the sorted subarray to the root node for output
    sorted_data=None
    if comm_rank==0:
        sorted_data=np.empty(n, dtype='i')
        comm.gather(local_data,root=0)
    return sorted_data



def accessible_solution():
    if comm_rank == 0:
        sorted_data = np.empty((n,), dtype='i')
    else:
        sorted_data = None
    comm.Gather(local_data, sorted_data, root=0)
    return sorted_data

n=50  #length of arrays to generate#
local_data=generate_local_arrays(comm_rank)
print('rank',comm_rank,'assigned with',local_data)
start_time=time.time()#start timing
local_data=odd_even_sort(local_data)
local_data=parallel_sort(local_data)
local_data=accessible_solution()
end_time=time.time()
if local_data is not None:
    print('Name: CUHK')
    print('ID: 111111111')
    print('sorted data:',end=' ')
    for j in range(len(local_data)-1):
        print(local_data[j],end=' ')
    print(local_data[len(local_data)-1])
#print(end_time-start_time)
