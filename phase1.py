import hashlib
from multiprocessing import Process, current_process
from multiprocessing.connection import Listener, Client


def employer_func():
    print('[Employer Process] starting...')
    # creating client socket
    server_address = ('localhost', 6000)
    conn = Client(address=server_address)
    for i in range(1, 52):
        if i == 51:
            conn.send('close')
        else:
            conn.send(f".\\TransactionFiles\\{i}.json")
    conn.close()
    print('[Employer Process] finished')


def server_func():
    print('[Server Process] starting...')
    # creating worker processes
    worker_processes = []
    for _ in range(5):
        p = Process(target=worker_func)
        worker_processes.append(p)
        p.start()
    employer_process = Process(target=employer_func)
    employer_process.start()
    
    # creating listener socket
    address = ('localhost', 6000)
    listener = Listener(address)
    conn = listener.accept()
    files_addresses = []
    while True:
        msg = conn.recv()
        if msg == 'close':
            conn.close()
            break
        else:
            files_addresses.append(msg)
    listener.close()

    is_done = False
    while True:
        for i, p in enumerate(worker_processes):
            if not p.is_alive():
                del worker_processes[i]
                p = Process(target=worker_func)
                worker_processes.append(p)
                p.start()
                print('[Server Process] one of the processes is not alive, a new woker process replaced')
        if not is_done:
            # creating client sockets to communicate with the worker processes
            # I
            port = int(worker_processes[0].name[-1]) * 100 + 6000
            address = ('localhost', port)
            conn = Client(address=address)
            for i in range(0, len(files_addresses), 5):
                conn.send(files_addresses[i])
            conn.send('close')
            conn.close()
            # II
            port = int(worker_processes[1].name[-1]) * 100 + 6000
            address = ('localhost', port)
            conn = Client(address=address)
            for i in range(1, len(files_addresses), 5):
                conn.send(files_addresses[i])
            conn.send('close')
            conn.close()
            # III
            port = int(worker_processes[2].name[-1]) * 100 + 6000
            address = ('localhost', port)
            conn = Client(address=address)
            for i in range(2, len(files_addresses), 5):
                conn.send(files_addresses[i])
            conn.send('close')
            conn.close()
            # IV
            port = int(worker_processes[3].name[-1]) * 100 + 6000
            address = ('localhost', port)
            conn = Client(address=address)
            for i in range(3, len(files_addresses), 5):
                conn.send(files_addresses[i])
            conn.send('close')
            conn.close()
            # V
            port = int(worker_processes[4].name[-1]) * 100 + 6000
            address = ('localhost', port)
            conn = Client(address=address)
            for i in range(4, len(files_addresses), 5):
                conn.send(files_addresses[i])
            conn.send('close')
            conn.close()
            is_done = True


def worker_func():
    print('[worker process] starting...')
    # creating listener socket
    port = 6000 + int(current_process().name[-1]) * 100
    address = ('localhost', port)
    listener = Listener(address)
    conn = listener.accept()
    
    while True:
        msg = conn.recv()
        if msg == 'close':
            conn.close()
            break
        else:
            file_address = msg
            with open(file_address, 'rb') as file:
                data = file.read()
                md5_returned = hashlib.md5(data).hexdigest()
                sol_file = open(file_address + '.md5', 'w')
                sol_file.truncate()
                sol_file.write(md5_returned)
                sol_file.close()
    print(f'[Worker Process {current_process().name}] job done')

if __name__ == '__main__': server_func()
