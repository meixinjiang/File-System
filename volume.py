import os
import math
import drive
import entry


"""
Creates a volume object
"""
class Volume:

	def __init__(self, name):
		self.name = name
		self.vdrive = drive.Drive(name)
		self.block_length = []	#amount of space used in each block

		#dictionary of directories, key is the directory path, value is a list of associated
		#directories and the block number they are located in the drive
		self.directories = {} 



	"""
	Formats the volume info block entries to their default value
	"""
	def format(self):
		self.vdrive.format()
		root_entries = entry.VolumeInfo()
		root_entries.create_entries()

		for i in range(128):	#initiates all the block lengths to 0
			self.block_length.append(0)

		self.block_length[0] =	512
		self.directories[""] = [[0, root_entries]]	#store in the dictionary
		self.write_entries(0, root_entries)



	"""
	Creates a file if it doesn't exist. Creates a block directory info block if the directory 
	to make the file in does not have one.
	Parameters - full path of the file
	"""
	def mkfile(self, file_path):
		#index 0 is directory path, index 1 is file name
		file_path_list = file_path.rsplit("/", 1)


		"""
		Creates new block directory information
		"""
		def create_new_block_info():
				entries = entry.BlockDirectory()
				entries.create_entries()

				#index 0 = parent path, index 1 = current directory name
				parent_dir = file_path_list[0].rsplit("/", 1)	
				count = 0

				if block[1] == None:
					self.directories[file_path_list[0]].pop(0)	#removes empty directory

				#finds empty block to write block directory info to
				for i in range(len(self.block_length)):
					if self.block_length[i] == 0:	

						#modify first directory entry with file name
						entries.modify(0, name=file_path_list[1])
						self.write_entries(i, entries)
						self.block_length[i] = 512

						#modify parent directory's info block to show block info creation
						for parent_block in self.directories[parent_dir[0]]:
							parent_dict = parent_block[1].get_dict()

							#find the parent directory entry of the current directory
							#and update it to reflect creation of block info
							for dir_entry in parent_dict:	
								if parent_dict[dir_entry][1] == parent_dir[1].ljust(9):
									for j in range(3,15):
										if parent_dict[dir_entry][j] == "000 ":
											parent_block[1].modify(dir_entry, addSize=512, block=[j, i])
											self.write_entries(parent_block[0], parent_block[1])
											break

						#append block info to the current directory's list
						self.directories[file_path_list[0]].append([i , entries])
						#refresh volume info block
						self.write_entries(0, self.directories[""][0][1])
						break
					else:
						count += 1

				if count == 128:
					print("Drive is full. Cannot create a new file.")

		if file_path_list[0] not in self.directories:
			print("Directory you wish to make file in does not exist or is an invalid path.")
		elif file_path[-1] == "/":
			print("Please enter a valid file name.")
		elif len(file_path_list[1]) > 8:
			print("File name is too long.")

		#directory to make file in has all 12 blocks allocated
		elif len(self.directories[file_path_list[0]]) == 12:
			count = 0

			#finds empty directory entry in all 12 blocks
			for block in self.directories[file_path_list[0]]:
				entries_dict = block[1].get_dict()
				for dir_entry in entries_dict:

					#empty directory entry exists
					if entries_dict[dir_entry][1] == "".ljust(9):	
						block[1].modify(dir_entry, name=file_path_list[1])
						self.write_entries(block[0], block[1])
						break
					else:
						count += 1

			if count == 96:
				print("Cannot make new directory. The maximum number of files/directories that can be created in this directory has been reached.")	
		
		else:	#directory does not have all blocks allocated

			#last block info that was created for the current directory
			block = self.directories[file_path_list[0]][-1]

			#directory has no block directory info created
			if block[1] == None:
				create_new_block_info()

			else:	#directory has block info
				entries_dict = block[1].get_dict()
				count = 0

				#finds first empty directory entry and modifies it with new file
				for dir_entry in entries_dict:
					if entries_dict[dir_entry][1] == file_path_list[1].ljust(9):
						print("File or directory with this name already exists.")
						break
					elif entries_dict[dir_entry][1] == "".ljust(9):	#empty directory entry
						block[1].modify(dir_entry, name=file_path_list[1])
						self.write_entries(block[0], block[1])
						break
					else:
						count += 1

				if isinstance(block[1], entry.VolumeInfo) and count == 6:
					print("Cannot make new directory. The maximum number of files/directories that can be created in this directory has been reached.")
				
				#current block is full, create new block info if the current directory
				#has less than 12 blocks allocated
				elif isinstance(block[1], entry.BlockDirectory) and count == 8:
					if len(self.directories[file_path_list[0]]) < 12:
						create_new_block_info()



	"""
	Creates a directory if it doesn't exist. Creates a block directory info block if the directory 
	to make the directory in does not have one.
	Parameters - full path of the directory
	"""
	def mkdir(self, dir_path):
		#index 0 is directory path, index 1 is directory name
		dir_path_list = dir_path.rsplit("/", 1)


		"""
		Creates new block directory information
		"""
		def create_new_block_info():
			entries = entry.BlockDirectory()
			entries.create_entries()

			#index 0 = parent path, index 1 = current directory name
			parent_dir = dir_path_list[0].rsplit("/", 1)
			count = 0

			if block[1] == None:
				self.directories[dir_path_list[0]].pop(0)	#removes empty directory

			#finds empty block to write block directory info to
			for i in range(len(self.block_length)):
				if self.block_length[i] == 0:

					#modify first directory entry with file name and change type
					entries.modify(0, name=dir_path_list[1], type="d:")
					self.write_entries(i, entries)
					self.block_length[i] = 512

					#modify parent directory's info block to show block info creation
					for parent_block in self.directories[parent_dir[0]]:
						parent_dict = parent_block[1].get_dict()

						#find the parent directory entry of the current directory
						#and update it to reflect creation of block info
						for dir_entry in parent_dict:
							if parent_dict[dir_entry][1] == parent_dir[1].ljust(9):	#find second to last dir
								for j in range(3, 15):
									if parent_dict[dir_entry][j] == "000 ":
										parent_block[1].modify(dir_entry, addSize=512, block=[j, i])
										self.write_entries(parent_block[0], parent_block[1])
										break
					
					#append block info to the current directory's list
					self.directories[dir_path_list[0]].append([i , entries])
					#store new directory path in dictionary
					self.directories[dir_path] = [[None, None]]
					#refresh volume info block
					self.write_entries(0, self.directories[""][0][1])
					break
				else:
					count += 1

			if count == 128:
				print("Drive is full. Cannot create a new directory.")

		if dir_path_list[0] not in self.directories:
			print("Directory you wish to make new directory in does not exist or is an invalid path.")
		elif dir_path[-1] == "/":
			print("Please enter a valid directory name.")
		elif len(dir_path_list[1]) > 8:
			print("Directory name is too long.")

		#parent directory has all 12 blocks allocated
		elif len(self.directories[dir_path_list[0]]) == 12:
			count = 0

			#finds empty directory entry in all 12 blocks
			for block in self.directories[dir_path_list[0]]:
				entries_dict = block[1].get_dict()
				for dir_entry in entries_dict:

					#empty directory entry exists
					if entries_dict[dir_entry][1] == "".ljust(9):
						block[1].modify(dir_entry, name=dir_path_list[1], type="d:")
						self.write_entries(block[0], block[1])
						break
					else:
						count += 1
			if count == 96:
				print("Cannot make new directory. The maximum number of files/directories that can be created in this directory has been reached.")
		
		else:	#directory does not have all blocks allocated

			#last block info that was created for the current directory
			block = self.directories[dir_path_list[0]][-1]

			#directory has no block directory info created
			if block[1] == None:
				create_new_block_info()

			else:	#directory has block info
				entries_dict = block[1].get_dict()
				count = 0

				#finds first empty directory entry and modifies it with new file
				for dir_entry in entries_dict:
					if entries_dict[dir_entry][1] == dir_path_list[1].ljust(9):
						print("File or directory with this name already exists.")
						break
					elif entries_dict[dir_entry][1] == "".ljust(9): #finds first empty file type
						block[1].modify(dir_entry, type="d:", name=dir_path_list[1])	#modify volume info
						self.directories[dir_path] = [[None, None]]
						self.write_entries(block[0], block[1])
						break
					else:
						count += 1

				if isinstance(block[1], entry.VolumeInfo) and count == 6:
					print("Cannot make new directory. The maximum number of files/directories that can be created in this directory has been reached.")
				
				#current block is full, create new block info if the current directory
				#has less than 12 blocks allocated
				elif isinstance(block[1], entry.BlockDirectory) and count == 8:
					if len(self.directories[dir_path_list[0]]) < 12:
						create_new_block_info()



	"""
	Appends data to an existing file.
	Parameters - full file path, data
	"""
	def append_data(self, file_path, data):

		#index 0 is directory path, index 1 is file name
		file_path_list = file_path.rsplit("/", 1)

		if file_path[-1] == "/":
			print("Please enter a valid file name.")
		elif file_path_list[0] not in self.directories:
			print("Directory path does not exist or is not a valid directory path.")
		elif file_path in self.directories:	#test
			print("File name given is a directory name.")

		else:
			count1 = 0

			#finds file from the given path if it exists
			for block in self.directories[file_path_list[0]]:
				entries_dict = block[1].get_dict()
				for dir_entry in entries_dict:

					if int(entries_dict[dir_entry][2].replace(":", "")) >= 6144:
						print("File is full.")
						break

					elif entries_dict[dir_entry][1] == file_path_list[1].ljust(9) :	#file exists
						data_remaining = data

						#removes quotation marks around data
						if data[-1] == '"' and data[0] == '"':	
							data_remaining = data[1:-1]
						elif data[0] == '"':
							data_remaining = data[1:]
						else:
							data_remaining = data[:-1]

						for i in range(3, 15):

							#block does not have data and there is data to append
							if entries_dict[dir_entry][i] == "000 " and len(data_remaining) > 0:	
								count2 = 0

								#find empty block in drive
								for j in range(len(self.block_length)):
									if self.block_length[j] == 0:

										self.block_length[j] += len(data_remaining[:512])	#update block length
										self.vdrive.write_block(j, data_remaining[:512].ljust(512))	#write data to empty block
										block[1].modify(dir_entry, addSize=len(data_remaining[:512]), block=[i, j])	#modify entry
										self.write_entries(block[0], block[1])	#refresh entry
										self.write_entries(0, self.directories[""][0][1])	#refresh volume info
										data_remaining = data_remaining[512:]	#removes already written data
										break
									else:
										count2 += 1

								if count2 == 128:
									print("Drive is full. Some data may not have been written.")
									break

							#block has data and there is data to append
							elif entries_dict[dir_entry][i] != "000 " and len(data_remaining) > 0:
								block_space_remaining = 512 - self.block_length[int(entries_dict[dir_entry][i])]
								
								#empty space in block
								if block_space_remaining != 0:
									block_index = int(entries_dict[dir_entry][i])	
									block_data = self.vdrive.read_block(block_index)[:self.block_length[block_index]]	#get data in block
									self.block_length[block_index] += len(data_remaining[:block_space_remaining])	#update block length
									data_write = block_data + data_remaining[:block_space_remaining]	#append old data with new data
									self.vdrive.write_block(block_index, data_write.ljust(512))	#write data to block
									block[1].modify(dir_entry, addSize=len(data_remaining[:block_space_remaining]))	#modify entry				
									self.write_entries(block[0], block[1])	#refresh entry
									self.write_entries(0, self.directories[""][0][1])	#refresh volume info
									data_remaining = data_remaining[block_space_remaining:]	#remove already written data

							else:
								break

						if int(entries_dict[dir_entry][2].replace(":", "")) == 6144 and len(data_remaining) > 0:
							print("File is full and some data has not been written to the drive.")
							break

						break
							
					else:
						count1 += 1

			if isinstance(block[1], entry.VolumeInfo) and count1 == 6:
				print("File does not exist.")
			elif isinstance(block[1], entry.BlockDirectory) and count1 == 96:
				print("File does not exist.")


	"""
	Prints data from an existing file.
	Parameters - full file path
	Returns - string of data
	"""
	def print_data(self, file_path):
		file_path_list = file_path.rsplit("/", 1)

		if file_path[-1] == "/":
			print("Please enter a valid file name.")
		elif file_path_list[0] not in self.directories:
			print("Directory path does not exist or is not a valid directory path.")
		elif file_path in self.directories:
			print("File name given is a directory name.")
		
		else:
			count = 0

			#finds file from the given path if it exists
			for block in self.directories[file_path_list[0]]:
				entries_dict = block[1].get_dict()
				for dir_entry in entries_dict:
					if entries_dict[dir_entry][1] == file_path_list[1].ljust(9):	#file exists
						file_data = ""

						#gets data from all the associated blocks
						for i in range(3, 15):	
							if entries_dict[dir_entry][i] != "000 ":
								block_index = int(entries_dict[dir_entry][i])
								block_data = self.vdrive.read_block(block_index)
								file_data += block_data[:self.block_length[block_index]]
							else:
								break

						if file_data == "":
							print("No data in this file.")
							break
						else:
							print(file_data)
							break

					else:
						count += 1

			if isinstance(block[1], entry.VolumeInfo) and count == 6:
				print("File does not exist.")
			elif isinstance(block[1], entry.BlockDirectory) and count == 96:
				print("File does not exist.")


	"""
	Lists all the files and directories in given directory
	Parameters - full directory path
	Returns - string representation of the directory info
	"""
	def ls(self, dir_path):
		if dir_path == "/":
			dir_path = ""
		
		if dir_path not in self.directories:
			print("Directory path does not exist or is not a valid directory path.")

		else:

			if dir_path == "":	
				print("Directory: /")
			else:
				print("Directory: " + dir_path)

			content1 = "Name".ljust(11) + "Type".ljust(5) + "Size".ljust(5) + "Allocated Blocks"
			content2 = "-" * 10 + " " + "-" * 4 + " " + "-" * 4 + " " + "-" * 48
			print(content1)			#prints header
			print(content2)			#prints border


			for block in self.directories[dir_path]:
				#directory just created, does not have block info
				if block[1] == None:
					print("")

				#directory block info
				else:
					entries_dict = block[1].get_dict()

					#finds all the files and directories
					for dir_entry in entries_dict:
						if entries_dict[dir_entry][1] != "".ljust(9):

							#gets the type 
							file_info = entries_dict[dir_entry][1].ljust(11) + "  "

							#the file/directory name 
							file_info += entries_dict[dir_entry][0] + " "
							
							#gets the size
							file_info += str(int(entries_dict[dir_entry][2].replace(":", ""))).rjust(4) + " "
							
							#gets the allocated blocks
							for i in range(3, 15):
								file_info += str(int(entries_dict[dir_entry][i])).rjust(3) + " "
							
							print(file_info)
		
	"""
	Deletes all the data in a file and the file itself.
	Parameters - full file path
	"""
	def del_file(self, file_path):

		#index 0 is directory path, index 1 is file name
		file_path_list = file_path.rsplit("/", 1)

		if file_path[-1] == "/":
			print("Please enter a valid file name.")
		elif file_path_list[0] not in self.directories:
			print("Directory path does not exist or is not a valid directory path.")
		elif file_path in self.directories:
			print("File name given is a directory name.")

		else:
			count = 0

			#finds file to delete from the given file path
			for block in self.directories[file_path_list[0]]:
				entries_dict = block[1].get_dict()
				
				for dir_entry in entries_dict:
					if entries_dict[dir_entry][1] == file_path_list[1].ljust(9):	#file exists

						#file is not empty
						if entries_dict[dir_entry][2] != "0000:":	

							#clears data from all allocated blocks
							for i in range(3, 15):	
								block_index = int(entries_dict[dir_entry][i])
								if block_index == 0:
									break
								else:
									self.vdrive.write_block(block_index, "".ljust(512))	#clears data from block
									self.block_length[block_index] = 0	#sets block length to default

							block[1].modify(dir_entry, **self.default_entry())	#set entry to default
							
							self.write_entries(block[0], block[1])
							self.write_entries(0, self.directories[""][0][1])	#refresh volume info
							break

						else:
							block[1].modify(dir_entry, **self.default_entry())	#set file info to default
							self.write_entries(block[0], block[1])
							break
					else:
						count += 1

			if isinstance(block[1], entry.VolumeInfo) and count == 6:
				print("File does not exist.")
			elif isinstance(block[1], entry.BlockDirectory) and count == 8:
				print("File does not exist.")



	"""
	Deletes an empty directory
	Parameters - full directory path
	"""
	def del_dir(self, dir_path):
		#index 0 is the parent path, index 1 is directory name
		dir_path_list = dir_path.rsplit("/", 1)

		if dir_path not in self.directories:
			print("Directory path does not exist or is not a valid directory path.")
		elif dir_path == "/":
			print("Root directory cannot be deleted.")

		else:
			#dir has no block info allocated
			if self.directories[dir_path][-1][1] == None:

				#finds current directory in the parent directory	
				for block in self.directories[dir_path_list[0]]:
					entries_dict = block[1].get_dict()
					for dir_entry in entries_dict:
						if entries_dict[dir_entry][1] == dir_path_list[1].ljust(9):	#directory found
							block[1].modify(dir_entry, **self.default_entry())	#modify parent block info
							self.write_entries(block[0], block[1])	#refresh parent block info
							del self.directories[dir_path]	#delete current directory
							break

			else:	#dir has entry blocks allocated
				count1 = 0

				#checks whether directory is empty
				for block1 in self.directories[dir_path]:
					entries_dict = block1[1].get_dict()
					for dir_entry in entries_dict:
						if entries_dict[dir_entry][1] != "".ljust(9):
							print("Directory you wish to delete is not empty.")
							count1 += 1
							break
					break

				if count1 == 0:	#dir to delete is empty

					#remove all block info
					for block2 in self.directories[dir_path]:
						self.vdrive.write_block(block2[0], "".ljust(512))	
						self.block_length[block2[0]] = 0

					#finds current directory in the parent directory
					for block3 in self.directories[dir_path_list[0]]:
						entries_dict = block3[1].get_dict()
						for dir_entry in entries_dict:
							if entries_dict[dir_entry][1] == dir_path_list[1].ljust(9):	#directory found
								block3[1].modify(dir_entry, **self.default_entry())	#modify parent block info
								self.write_entries(block3[0], block3[1])	#refresh parent block info
								del self.directories[dir_path]	#delete directory
								self.write_entries(0, self.directories[""][0][1])	#refresh volume info

								break

	"""
	Reconnects to an existing volume
	Parameters - name of volume
	"""
	def reconnect(self, volumeName):
		self.vdrive = drive.Drive(volumeName)
		self.vdrive.reconnect()
		volume_info = self.vdrive.read_block(0)[128:]
		entries_list = []

		index = 0
		while index != 384:	#gets all data
			entries_list.append(volume_info[index:index + 64])
			index += 64

		for i in range(128):	#initiates all the block lengths to 0
			self.block_length.append(0)

		vol_info = entry.VolumeInfo()	#initiates volume info block
		vol_info.create_entries()

		self.load_entries(vol_info, entries_list)
		self.directories[""] = [[0, vol_info]]

		self.dir_recursion(vol_info, "/")
		self.block_length[0] = 512



	"""
	Generates a bitmap of available blocks
	"""
	def available_blocks(self):
		available = ""
		for i in range(0, 128):	
			if self.block_length[i] != 0:
				available += "+"
			else:
				available += "-"
		return available



	"""
	Disconnects from current volume
	"""
	def disconnect(self):
		self.vdrive.disconnect()



	"""
	Creates a dictionary representation of a default entry
	Returns - dictionary of default entries
	"""
	def default_entry(self):
		entry_dict = {}

		entry_dict["type"] = "f:"
		entry_dict["name"] = "".ljust(9)
		entry_dict["resetSize"] = "0000:"
		entry_dict["blockList"] = []
		for i in range(12):
			entry_dict["blockList"].append("000 ")

		return entry_dict



	"""
	Writes entries to the given block index
	Parameters - block index, 
	"""
	def write_entries(self, block_index, entries):
		if isinstance(entries, entry.VolumeInfo):
			self.vdrive.write_block(block_index, self.available_blocks() + entries.get_string())	#write to volume entry
		else:
			self.vdrive.write_block(block_index, entries.get_string())	#write to block entry



	"""
	Loads entries from block info
	Parameters - 
	"""
	def load_entries(self, entries, entries_list):
		for i in range(len(entries_list)):	#modify volume entry
			if entries_list[i][2:10] != "".ljust(9):	#get name
				entries.modify(i, name=entries_list[i][2:10])

			if entries_list[i][:2] == "d:":	#get type
				entries.modify(i, type=entries_list[i][:2])

			if entries_list[i][11:15] != "0000":	#get size
				entries.modify(i, addSize=int(entries_list[i][11:15]))

			index = 16
			block_list = []
			while index != 64:	#gets all allocated blocks
				block_list.append(entries_list[i][index:index+4])
				index += 4

			#gets the allocated block lengths
			total_size = int(entries_list[i][11:15])	
			for block in block_list:
				if (total_size - 512) >= 0:
					self.block_length[int(block)] = 512
					total_size -= 512
				else:
					self.block_length[int(block)] = total_size

			entries.modify(i, blockList=block_list)



	"""
	Recursively gets the block info of directories
	"""
	def dir_recursion(self, entries, path):
		entries_dict = entries.get_dict()
		
		for dir_entry in entries_dict:
			if entries_dict[dir_entry][0] == "d:":

				new_path = path + entries_dict[dir_entry][1].rstrip()

				#empty directory
				if entries_dict[dir_entry][2] == "0000:":	
					self.directories[new_path] = [[None, None]]

				else:	#dir has blocks allocated

					for i in range(3, 15):
						block_index = int(entries_dict[dir_entry][i])
						if block_index != 0:	
							#create new block info		
							block_entries = entry.BlockDirectory()
							block_entries.create_entries()

							#get block info
							dir_entries = self.vdrive.read_block(block_index)

							entries_list = []
							index = 0
							while index != 512:	#gets all data
								entries_list.append(dir_entries[index:index+64])
								index += 64

							self.load_entries(block_entries, entries_list)

							if new_path not in self.directories:	#check if directory path exists 
								self.directories[new_path] = [[block_index, block_entries]]
							else:
								self.directories[new_path].append([block_index, block_entries])

							self.dir_recursion(block_entries, new_path + "/")








	

	
	
	
	
	
	
	
	
	
	
	
	
	

	
