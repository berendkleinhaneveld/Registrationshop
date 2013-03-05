"""
Elastix

Wrapper around the command-line tool Elastix.
Inspired by pyelastix by Almar Klein. His project can be found
at https://code.google.com/p/pirt/

@author: Berend Klein Haneveld
"""

import os, sys, time
import platform
import thread
import subprocess

class Elastix(object):
	"""
	Main class that talks with the command-line version of 
	Elastix.
	"""
	def __init__(self, queue, fixed, moving, parameters, outputDir):
		"""
		@param queue
		@type queue = multiprocessing.Queue
		@param fixed: File name of the fixed data set
		@type fixed: unicode
		@param moving: File name of the moving data set
		@type moving: unicode
		@param parameters: Parameters that the registrations should run with
		@type parameters: File name of parameter file
		@param outputDir: path of output directory for the files
		"""
		super(Elastix, self).__init__()

		self.queue = queue
		self.fixedDataSet = fixed
		self.movingDataSet = moving
		self.parameters = parameters
		self.outputDir = outputDir

	def register(self):
		"""
		This method starts the registration by calling
		Elastix with the specified data sets and parameters.
		During execution of the command-line tool, it will parse
		the standard output in order to provide feedback about
		the status and progress of Elastix.
		"""

		# Register
		if True:
			# Compile command to execute
			command = ELASTIX_EXE
			command += ' -m %s -f %s -out %s -p %s' % (
				self.fixedDataSet, self.movingDataSet, self.outputDir, self.parameters)
			
			# Execute command
			print "Calling Elastix to register images ..."

			systemCall(command, True)
			
			# Try and load result
			try:
				registrationResult = self._read_image_data('result.0.mhd')
			except IOError, why:
				tmp = "An error occured during registration: " + str(why)
				raise RuntimeError(tmp)

		# Find deformation field
		if True:
			# Get path of trafo param file
			transParameters = os.path.join(self.outputDir, 'TransformParameters.0.txt')

			# Compile command to execute
			command = TRANSFORMIX_EXE
			command += ' -def all -out %s -tp %s' % (
				self.outputDir, transParameters)
			
			# Execute command
			systemCall(command, True)
			
			# Try and load result
			try:
				transformation = self._read_image_data('deformationField.mhd')
			except IOError, why:
				tmp = "An error occured during transformation: " + str(why)
				raise RuntimeError(tmp)

		# fields = [b]
		field = transformation
		if field.ndim == 2:
			field = [field[:,d] for d in range(1)]
		elif field.ndim == 3:
			field = [field[:,:,d] for d in range(2)]
		elif field.ndim == 4:
			field = [field[:,:,:,d] for d in range(3)]
		elif field.ndim == 5:
			field = [field[:,:,:,:,d] for d in range(4)]
		
		self.queue.transformation = tuple(field)
		self.queue.result = registrationResult

# - Helper functions

class Progress:
	""" Progress()
	
	To show progress during the registration.
	
	"""
	
	def __init__(self):
		self._level = 0
		self.reset()
	
	def update(self, s):
		
		# Detect resolution
		if s.startswith('Resolution:'):
			self._level = self.get_int( s.split(':')[1] )
		
		# Check if nr
		if '\t' in s:
			iter = self.get_int( s.split('\t',1)[0] )
			if iter:
				self.show_progress(iter)
	
	def get_int(self, s):
		nr = 0
		try:
			nr = int(s)
		except Exception:
			pass
		return nr
	
	def reset(self):
		self._message = ''
		print ''
	
	def show_progress(self, iter):
		
		# Remove previous message
		rem = '\b' * (len(self._message)+1)
		
		# Create message, and print
		self._message = 'resolution %i, iter %i' % (self._level, iter)
		print rem + self._message

def systemCall(cmd, verbose=False):
	""" systemCall(cmd, verbose=False)
	
	Execute the given command in a subprocess and wait for it to finish.
	A thread is run that prints output of the process if verbose is True.
	"""
	
	# Init flag
	interrupted = False
	
	# Create progress
	if verbose > 0:
		progress = Progress()
	
	def poll_process(p):
		# Keep reading stdout
		while not interrupted:
			msg = p.stdout.readline()
			if msg:
				if 'error' in msg.lower():
					print(msg.rstrip())
					if verbose==1:
						progress.reset()
				elif verbose>1:
					print(msg.rstrip())
				elif verbose==1:
					progress.update(msg)
			else:
				break
			time.sleep(0.01)
		
		#print("thread exit")
	
	# Start process that runs the command
	p = subprocess.Popen(cmd, shell=True, 
			stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	
	# Keep reading stdout from it
	thread.start_new_thread(poll_process, (p,))
	
	# Wait here
	try:
		while p.poll() is None:
			time.sleep(0.01)
	except KeyboardInterrupt:
		# Set flag
		interrupted = True
		# Kill subprocess
		pid = p.pid
		if hasattr(os,'kill'):
			import signal
			os.kill(pid, signal.SIGKILL)
		elif sys.platform.startswith('win'):
			import ctypes
			kernel32 = ctypes.windll.kernel32
			handle = kernel32.OpenProcess(1, 0, pid)
			kernel32.TerminateProcess(handle, 0)
			#os.system("TASKKILL /PID " + str(pid) + " /F")
	
	# All good?
	if interrupted:
		raise RuntimeError('Registration process interrupted by the user.')
	if p.returncode:
		print(p.stdout.read())
		raise RuntimeError('An error occured during the registration.')

def _find_executables():
	"""
	Tries to find the elastix and transformix executables.
	"""
	
	# Get list of possible locations
	if sys.platform.startswith('win'):
		possible_locations = [  'c:\\program files\\elastix', 
								'c:\\program files (x86)\\elastix']
		for s in ['PROGRAMFILES', 'PROGRAMFILES(x86)']:
			tmp = os.environ.get(s)
			if tmp:
				possible_locations.append(os.path.join(tmp, 'elastix'))
		elastix_name = 'elastix.exe'
		transformix_name = 'transformix.exe'
	else:
		# TODO: use whereis to find elastix on the path
		possible_locations = [  '/usr/bin','/usr/local/bin','/opt/local/bin',
								'/usr/elastix', '/usr/local/elastix',
								'/usr/bin/elastix', '/usr/local/bin/elastix']
		elastix_name = 'elastix'
		transformix_name = 'transformix'
	
	# Possible location might also be the location of this file ...
	possible_locations.append( os.path.dirname(os.path.abspath(__file__)) )
	
	# Set default (for if we could not find the absolute location)
	elastix_exe = elastix_name
	transformix_exe = transformix_name
	
	# Test
	for p in possible_locations:
		p1 = os.path.join(p, elastix_name)
		p2 = os.path.join(p, transformix_name)
		if os.path.isfile(p1):
			elastix_exe = p1
		if os.path.isfile(p2):
			transformix_exe = p2
	
	# Post process
	if ' ' in elastix_exe:
		elastix_exe = '"%s"' % elastix_exe
	if ' ' in transformix_exe:
		transformix_exe = '"%s"' % transformix_exe
	
	# Done
	return elastix_exe, transformix_exe

# Paths to executables
ELASTIX_EXE, TRANSFORMIX_EXE = _find_executables()
