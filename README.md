# File-System

Simulates a simple file system by creating a file that acts as a drive being written to. 

Pathnames are in the format /dir1/dir2/file3 and "/" represents the root.

Using the Terminal in the Linux OS, enter the following command after navigating to the folder containing this repository:

    python3 TinyDOS.py
          
The following commands can be used in the simulated file system:
    
    format driveName -- creates a drive
    
    reconnect driveName -- reconnects to an existing drive
    
    ls /dirPath -- lists the files and directories in the specified path
    
    mkfile /fileName -- creates a file with the specified path
    
    mkdir /dirName -- creates a directory with the specified path
    
    append /fileName data -- writes data to an existing file
    
    print /fileName -- prints data in the specified file
    
    delfile /fileName -- deletes file
    
    deldir /dirName -- deletes directory
    
    quit -- disconnects from the drive

To run the test files, use the following command:

    python3 TinyDOS.py < fullPathOfTestFile
          
Note: To view the drive in real time as it is being modified, use the following command after the "format" command has been
called:

    watch head driveName
