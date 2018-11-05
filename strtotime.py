import os

def strtotime(timestr):
	path = os.path.dirname(os.path.realpath(__file__))
	ps = os.popen('php {}/strtotime.php "{}"'.format(path, timestr))
	time = ps.readline()
	time = int(time)
	ps.close()
	return time
