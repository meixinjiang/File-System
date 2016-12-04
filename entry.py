"""
Creates a volume info object
"""
class VolumeInfo:


	def __init__(self):
		self.entries_dict = {}
	

	"""
	Creates the default volume info by filling the dictionary with the default values.
	The key is the directory entry number (0-6) and the value is a list of the default values

	"""
	def create_entries(self):
		for i in range(6):
			self.entries_dict[i] = []
			self.entries_dict[i].append("f:")	#0
			self.entries_dict[i].append("".ljust(9))	#1	
			self.entries_dict[i].append("0000:")	#2
			for k in range(12):	#3-14
				self.entries_dict[i].append("000 ")
			
	"""
	Modifies the volume info
	Parameters - the directory entry number (0-6) in the block, one or more keyword arguments
	"""
	def modify(self, entry_num, **kwargs):
		for key in kwargs:
			if key == "type":
				self.entries_dict[entry_num][0] = kwargs[key]
			elif key == "name":	
				self.entries_dict[entry_num][1] = kwargs[key].ljust(9)
			elif key == "addSize":
				total_size = int(self.entries_dict[entry_num][2].replace(":", "")) + kwargs[key]
				self.entries_dict[entry_num][2] = str(total_size).zfill(4) + ":"
			elif key == "block":	#takes a list of 2 parameters 1st: 3-14 2nd: 0-127
				self.entries_dict[entry_num][kwargs[key][0]] = str(kwargs[key][1]).zfill(3).ljust(4)
			elif key == "resetSize":
				self.entries_dict[entry_num][2] = kwargs[key]
			elif key == "blockList":
				for i in range(3, 15):
					self.entries_dict[entry_num][i] = kwargs[key].pop(0)
					

			else:
				continue
	
	"""
	Returns a string representation of the volume info directory entries
	"""
	def get_string(self):
		directory = ""
		for key in self.entries_dict:
			for item in self.entries_dict[key]:
				directory += item
		return directory

	"""
	Returns the dictionary representation of the volume info directory entries
	"""
	def get_dict(self):
		return self.entries_dict
		


"""
Creates a block directory info object
"""
class BlockDirectory:


	def __init__(self):
		self.entries_dict = {}

	"""
	Creates the default directory info by filling the dictionary with the default values.
	The key is the directory entry number (0-8) and the value is a list of the default values
	"""
	def create_entries(self):
		for i in range(8):
			self.entries_dict[i] = []
			self.entries_dict[i].append("f:")
			self.entries_dict[i].append("".ljust(9))
			self.entries_dict[i].append("0000:")
			for k in range(12):
				self.entries_dict[i].append("000 ")


	"""
	Modifies the directory info
	Parameters - the directory entry number (0-6) in the block, one or more keyword arguments
	"""	
	def modify(self, entry_num, **kwargs):
		for key in kwargs:
			if key == "type":
				self.entries_dict[entry_num][0] = kwargs[key]
			elif key == "name":	#change to elif
				self.entries_dict[entry_num][1] = kwargs[key].ljust(9)
			elif key == "addSize":
				total_size = int(self.entries_dict[entry_num][2].replace(":", "")) + kwargs[key]
				self.entries_dict[entry_num][2] = str(total_size).zfill(4) + ":"
			elif key == "block":	#takes a list of 2 parameters 1st: 3-14 2nd: 0-127
				self.entries_dict[entry_num][kwargs[key][0]] = str(kwargs[key][1]).zfill(3).ljust(4)
			elif key == "resetSize":
				self.entries_dict[entry_num][2] = kwargs[key]
			elif key == "blockList":
				for i in range(3, 15):
					self.entries_dict[entry_num][i] = kwargs[key].pop(0)


	"""
	Returns a string representation of the directory entries
	"""
	def get_string(self):
		directory = ""
		for key in self.entries_dict:
			for item in self.entries_dict[key]:
				directory += item
		return directory


	"""
	Returns the dictionary representation of the volume info directory entries
	"""
	def get_dict(self):
		return self.entries_dict
	
