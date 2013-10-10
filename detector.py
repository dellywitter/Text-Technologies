
import re,zlib
from time import *
import glob,string


#list_of_files = glob.glob('./****/*.txt')
codes=[]
def open_file(file_name):
	f = open(file_name, 'r')
	try:
	    text = f.read()
	finally:
	    f.close()
	return text
	
def write_top(list_to_write,name):
	try:
		f = open(name, "w")
		try:
			f.write(list_to_write)
		finally:
			f.close()
	except IOError:
		pass

def split_uppercase(s):
    return re.sub(r'([a-z]*)([A-Z])',r'\1 \2',s)
    
def getAdlers(list_of_files):
	f=open(list_of_files, 'r')
	print f
'''
	for f in list_of_files:
		speech=open(f,'r')
		list_of_lines=speech.readlines()[1:]# remove first line since it's
		for n,l in list_of_lines:
			p=l.strip()
			list_of_lines[n]=p
		
		print list_of_lines
		#list_of_lines=re.split('[\\s]+',list_of_lines)
		#re.split([\\s+],text
		#different for every speech

		print list_of_lines									# return every
		for l in list_of_lines:
			#l=l.translate(string.maketrans("",""),string.punctuation)
			for punct in string.punctuation:
				l=l.replace(punct,' ')
			l=l.split(' ')
			while '' in l:
				l.remove('')
			for ind,w in enumerate(l):
				pos = [i for i,e in enumerate(w) if e.isupper()]
				if len(pos)>1:
					l[ind]=split_uppercase(w)
			l=" ".join(l)
		#adCode=zlib.adler32(list_of_lines)
		#codes.append(adCode)
	#print len(codes)
	#print len(set(codes))
	#return codes
'''
#getAdlers(list_of_files)
getAdlers('./0946868/182206.txt')