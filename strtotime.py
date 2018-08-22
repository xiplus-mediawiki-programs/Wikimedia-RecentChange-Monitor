import os

def strtotime(timestr):
	path = os.path.dirname(os.path.realpath(__file__))
	time = os.popen('php {}/strtotime.php "{}"'.format(path, timestr)).readline()
	time = int(time)
	return time
