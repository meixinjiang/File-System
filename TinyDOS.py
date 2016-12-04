import sys
import volume

volume_obj = None

for line in sys.stdin:
	command = line.rstrip('\n').split(" ", 2)

	if command[0] == "quit":
		volume_obj.disconnect()
		sys.exit(0)

	elif command[0] == "format":
		volume_obj = volume.Volume(command[1])
		volume_obj.format()

	elif command[0] == "reconnect":
		volume_obj = volume.Volume(command[1])
		volume_obj.reconnect(command[1])

	elif command[0] == "ls":
		volume_obj.ls(command[1])

	elif command[0] == "mkfile":
		volume_obj.mkfile(command[1])

	elif command[0] == "mkdir":
		volume_obj.mkdir(command[1])
		
	elif command[0] == "append":
		if len(command) == 3:
			volume_obj.append_data(command[1], command[2])
		else:
			print("Please enter some data.")
		
	elif command[0] == "print":
		volume_obj.print_data(command[1])

	elif command[0] == "delfile":
		volume_obj.del_file(command[1])

	elif command[0] == "deldir":
		volume_obj.del_dir(command[1])

	elif command[0] == "":
		print("")

	else:
		print("Illegal command.")
