import hashlib
from os import path, walk
from random import random
from multiprocessing import Process, current_process
from multiprocessing.connection import Listener, Client
from threading import Thread, current_thread
from queue import Queue


def check_md5_content(fa):
    with open(fa, 'rb') as file:
        data = file.read()
        md5_returned = hashlib.md5(data).hexdigest()
        with open(fa + '.md5', 'rb') as md5file:
            file_data = str(md5file.read())
            if file_data[2:-1] != md5_returned:
                print(f'[Employer Process - side thread:{current_thread().name}] MD5 file calculated incorrectly:\n"{fa}.md5"\n')

def employer_side_threads(files_addresses: list, start_index, q: Queue):
    print(f'[Employer Process - {current_thread().name}] Started\n')
    check_again = []
    for i in range(start_index, len(files_addresses), 5):
            if not path.exists(files_addresses[i] + '.md5'):
                print(f'[Employer Process - {current_thread().name}] MD5 file missing:\n{files_addresses[i]}.md5\n')
                q.put(f'1:{files_addresses[i]}')
                check_again.append(files_addresses[i])
            else:
                check_md5_content(files_addresses[i])

    for file_ad in check_again:
        while True:
            if path.exists(file_ad + '.md5'):
                check_md5_content(file_ad)
                break
            print(file_ad)

    q.put('done')
    print(f'[Employer Process - {current_thread().name}] Finished\n')

def employer_func():
    print('[Employer Process - main thread] Started\n')
    # getting addresses recursively:
    folder_path = "C:\\Users\\Kourosh Yousefian\\Desktop\\OS-Project1\\TransactionFiles2"
    files_addresses = []
    for root, dirs, files in walk(folder_path):
        for file in files:
            if file.endswith(".json"):
                files_addresses.append(path.join(root, file))

    # creating client socket to send addresses to server process
    conn = Client(address=('localhost', 6000))
    for i in range(0, len(files_addresses)+1):
        if i == len(files_addresses):
            conn.send('done')
        else:
            conn.send(files_addresses[i])

    conn2 = Listener(address=('localhost', 5000))
    listener = conn2.accept()
    listener.recv()
    
    
    # creating threads and passing list of addresses to them
    q = Queue()
    for i in range(5):
        Thread(target=employer_side_threads, args=(files_addresses, i, q)).start()

    conn = Client(address=('localhost', 6000))
    while True:
        if not q.empty():
            tmsg = q.get()
            if tmsg[0] == '1':
                conn.send(f'again {tmsg[2:]}')
            if tmsg == 'done':
                conn.send('done')
                conn.close()
                break
    print('[Employer Process - main thread] Finished\n')
    
def server_side_thread(worker_processes):
        for i, p in enumerate(worker_processes):
            if not p.is_alive():
                del worker_processes[i]
                p = Process(target=worker_func)
                worker_processes.append(p)
                p.start()
                print('[Server Process] one process is not alive, a new worker process replaced')

def server_func():
    # creating worker processes
    worker_processes = []
    for _ in range(5):
        p = Process(target=worker_func)
        worker_processes.append(p)
        p.start()
    # creating second thread for server process to keep worker processes alive
    Thread(target=server_side_thread, args=(worker_processes,)).start()

    employer_process = Process(target=employer_func)
    employer_process.start()
    
    # creating listener socket
    listener = Listener(address=('localhost', 6000))
    listener_conn = listener.accept()
    
    files_addresses = []
    while True:
        msg = listener_conn.recv()
        if msg == 'done': break
        else: files_addresses.append(msg)

    # creating client sockets to communicate with the worker processes
    # I
    port = int(worker_processes[0].name[-1]) * 100 + 6000
    conn0 = Client(address=('localhost', port))
    for i in range(0, len(files_addresses), 5):
        conn0.send(files_addresses[i])
    conn0.send('end')
    conn0.close()
    # II
    port = int(worker_processes[1].name[-1]) * 100 + 6000
    conn1 = Client(address=('localhost', port))
    for i in range(1, len(files_addresses), 5):
        conn1.send(files_addresses[i])
    conn1.send('end')
    conn1.close()
    # III
    port = int(worker_processes[2].name[-1]) * 100 + 6000
    conn2 = Client(address=('localhost', port))
    for i in range(2, len(files_addresses), 5):
        conn2.send(files_addresses[i])
    conn2.send('end')
    conn2.close()
    # IV
    port = int(worker_processes[3].name[-1]) * 100 + 6000
    conn3 = Client(address=('localhost', port))
    for i in range(3, len(files_addresses), 5):
        conn3.send(files_addresses[i])
    conn3.send('end')
    conn3.close()
    # V
    port = int(worker_processes[4].name[-1]) * 100 + 6000
    conn4 = Client(address=('localhost', port))
    for i in range(4, len(files_addresses), 5):
        conn4.send(files_addresses[i])
    conn4.send('end')
    conn4.close()

    conn5 = Client(address=('localhost', 5000))
    conn5.send('start')

    
    while True:
        listener_conn = listener.accept()
        finished = False
        conn6 = Client(address=('localhost', 6100))
        while not finished:
            msg = listener_conn.recv()
            if msg[0:5] == 'again':
                conn6.send(msg[6:])
            if msg == 'done':
                conn6.send('end')
                finished = True
            
            

def worker_func():
    # creating listener socket
    address = ('localhost', 6000 + int(current_process().name[-1]) * 100)
    listener = Listener(address)
    
    a = 0
    while True:
        a += 1
        finished = False
        conn = listener.accept()
        while not finished:
            msg = conn.recv()
            rand_num = random()
            if msg == 'end': finished = True
            elif rand_num <= 0.33:
                file_address = msg
                sol_file = open(file_address + '.md5', 'w')
                sol_file.truncate()
                sol_file.write("")
                sol_file.close()
            elif rand_num <= 0.33 and a == 1:
                pass
            else:
                file_address = msg
                with open(file_address, 'rb') as file:
                    data = file.read()
                    md5_returned = hashlib.md5(data).hexdigest()
                    sol_file = open(file_address + '.md5', 'w')
                    sol_file.truncate()
                    sol_file.write(md5_returned)
                    sol_file.close()
            
    
if __name__ == '__main__': server_func()