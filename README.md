# Bad disks in Gokhu
## Step One:
The contents of some files on the servers of Ghokho (Ghorob Khokho) are apparently changed unintentionally.
We want to design a system to validate the files and confirm that the files have not been changed unintentionally.
Implement three categories of processes: server, client and worker processes.

- At the beginning, create a server process and five workers.
- If one of these workers terminates due to an error, the server creates a new worker.
- The server process waits for employers and workers to connect
- After connecting to the server, the client processes transfer the number of file addresses to the server.
- Worker processes connect to the server and receive the addresses of some of these files.
- In each request, the address of a maximum of five files is given to the worker.
- If the file address is not available on the server, the worker must wait.
- Make sure that each file address must be sent to exactly one user.
- Each worker reads the files it receives, then calculates the MD5 value of its contents and stores it in
  a file with the same file address but with the suffix ".md5". For
  example, if the input file is `/var/dat.iso`, the output is saved in the address `/var/dat.iso.md5`
- The MD5 value is written as a hexadecimal string with 32 digits.
- After processing the received files, the worker again requests the address of a number of files from the server
- For communication between the server process, employers and workers, you can use pipe, network socket, shared memory
  `shm_open()` or use the REST programming interface.
- To calculate MD5, you can use libraries or code snippets available on the Internet.
- To test, gradually transfer a large number of files to the server with the help of a number of client processes.

## Step Two:
In this step, you expand the employer's program in the first step.

- The employer's program has six threads that run concurrently.
- One of these threads recursively extracts the list of system files.
- The other five threads are responsible for checking each of the collected files.
- Note that each file should be checked by only one thread, as well as the list of files
  it is extracted by the first thread, other threads check the collected files.
 - Each of the checking threads repeats one address from the collected addresses
  receives (if the list is empty, it waits for an address to be added). For example, for
  checking the "iso.dat/var" file first checks if the "md5.iso.dat/var" file exists or
  no If it is not available, it sends the address of this file to the server to calculate the value of "md5.iso.dat/var".
  and adds this address to the list of addresses to check again in the future. If the file
  if »md5.iso.dat/var »/ exists, the MD5 thread will recalculate the file »iso.dat/var »/ and
  compares the contents of the file »md5.iso.dat/var »/. If they are not equal, it prints a message that shows
  indicates that the MD5 value has changed
