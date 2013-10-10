# written in Python 2.7.1
from __future__ import with_statement
from nltk.corpus import stopwords
from nltk.tokenize import *
import re,zlib,os,difflib,itertools
import glob,string,hashlib
from time import *

files = glob.glob('./train/*.txt')

class Detector(object):

	def __init__(self):
		self.speech_dict=dict()#to store the text files with preprocessed text
		self.code_dict=dict()#to store the adler32 codes against each text file name
		self.inverted_dict=dict()#code_dict but inverted,i.e speeches with the same adler32 code are values of the code now(which is the key)
		self.hashed_words=dict()# name of file as key and list of integers in binary representing each word
		self.fingerprints=dict()
		self.buckets=dict()
		self.buckets2=dict()
		self.hashed_words2=dict()# name of file as key and list of integers in binary representing each word
		self.fingerprints2=dict()
		self.tokens=dict()
		self.tags=dict()
		self.plateaus=dict()
	def writeToFile(self,list_to_write,name):
		try:
			f = open(name, "w")
			try:
				f.write(list_to_write)
			finally:
				f.close()
		except IOError:
			pass
	# invert a dictionary and put duplicate values' keys in a list
	def invertdict(self,d):
		inv=dict()
		for k,v in d.iteritems():
			keys=inv.setdefault(v,[])
			keys.append(k)
		return inv

	def preprocess(self,text_file):
		text_file=open(text_file,'r')
		text=text_file.readlines()[1:]
		speech=''
		for line in text:
			line=line.translate(string.maketrans("",""),string.punctuation)
			#strip punctuation
			line=re.split('[\\s]+',line)#remove the /r and /n
			while '' in line:#remove empty strings
				line.remove('')
			if len(line)!=0:
				line=' '.join(line)
				speech+=' '+line
		speech=speech.lower()
		#return a preprocessed string with the text
		return speech
	
	def getHashes(self, tokens):
		#here tokens is a list of words,no stopwords
		hashes=[]
		weights=[]
		for t in tokens:
			#ha=(map(int,list(('{:b}'.format(hash(t))).strip('-').zfill(64))))#remove '-0b' from front of binary num and pad with zeroes in the beginning
			m=hashlib.md5()
			m.update(t)
			ha=(bin(int(m.hexdigest(), 16))[2:]).strip('-').zfill(256)
			ha=map(int,ha)
			w=tokens.count(t)#get weight of word=number of occurrences in a doc
			ha=map(lambda x:x if x!=0 else -1,ha)#replace all occurrences of 0 with -1
			hashes.append(map(lambda x:(x*w),ha))#multiply every component by the weight of the word(weight is number of occurrences)
			weights.append(tokens.count(t))# get the frequencies of the word in the speech document		
		return hashes
		
	def getFingerprint(self, hashes):
		#hashes are a list of lists, only needs column summing
		v = [ sum(x) for x in zip(*hashes) ]# sum the columns
		v=map(lambda x:0 if x<0 else 1,v)
		return v # binary fingerprint of 64 bit vector
		
	def fillInDataDicts(self, files):
		for f in files:
			#get the name of the file without the extension
			f_name=os.path.basename(os.path.splitext(f)[0])
			speech=self.preprocess(f)#get the clean preprocessed text from the file
			self.speech_dict[f_name]=speech#feed it to the dict of speeches
			adCode=zlib.adler32(speech)
			self.code_dict[f_name]=adCode
			#use following processing for nears
			ws=regexp_tokenize(speech, pattern=r'\w+([.,]\w+)*|\S+')
			toks = filter(lambda x: x not in stopwords.words('english'), ws)
			self.tokens[f_name]=toks
			hashes=self.getHashes(toks)
			self.hashed_words[f_name]=hashes#feed the n=binary hashes into the dictionary with the name of the file as key
			self.fingerprints[f_name]= "".join(str(a) for a in self.getFingerprint(hashes))

	#write the file with exact duplicates
	def findExacts(self):
		self.inverted_dict= self.invertdict(self.code_dict)
		dups=''
		for k in self.inverted_dict.iterkeys():
			l=self.inverted_dict[k]
			if len(l)>1:
				duplicate='-'.join( self.inverted_dict[k])
				dups+=duplicate+'\n'
		self.writeToFile(dups,'exact.txt')
	
	# to split the 64 bits long list l into  groups of n elements
	def chunks(self,l, n):
		return [l[i:i+n] for i in range(0, len(l), n)]

	def hamming1(self,str1, str2):
		return sum(itertools.imap(str.__ne__, str1, str2))
		
	#calculate and write the near duplicates
	def findNears(self):
		#L=4
		#k=32
		nears=''
		for s1 in self.fingerprints.iterkeys():
			for s2 in self.fingerprints.iterkeys():						
				if s1!=s2:
					score=self.hamming1(str(self.fingerprints[s1]),str(self.fingerprints[s2]))
					if score<2:
						row='-'.join([s1,s2])
						nears+=row+'\n'	
		self.writeToFile(nears,'near.txt')
		
		
	#check if a token is a number or not
	def is_number(self,s):
		try:
			float(s)
			return True
		except ValueError:
			return False
		
	def finn(self):
		for k,v in self.tokens.iteritems():
			newv=[]
			for i in v:
				if self.is_number(i):
					newv.append(0)
				else:
					newv.append(1)
			self.tags[k]=newv
		for k,v in self.tags.iteritems():
			L=0
			best_a=0
			best_b=0
			current_best=0
			for a in range(2,len(v)-1):	
				L+=v[a]
				b=a+1
				M=0
				R=sum(v[b:])
				for b in range(b,len(v)):
					M+=1-v[b]
					R-=v[b]
					cur=L+100*M+R
					if cur>current_best:
						best_a=a
						best_b=b
						current_best=cur
			
			if (best_b-best_a)>1:
				#self.buckets2[k]=self.tokens[k][best_a:best_b]	
				hashes=self.getHashes(self.tokens[k][best_a:best_b])
				self.hashed_words2[k]=hashes#feed the n=binary hashes into the dictionary with the name of the file as key
				self.fingerprints2[k]= "".join(str(a) for a in self.getFingerprint(hashes))

		finns=''
		for s1 in self.fingerprints2.iterkeys():
			for s2 in self.fingerprints2.iterkeys():						
				if s1!=s2:
					score=self.hamming1(str(self.fingerprints2[s1]),str(self.fingerprints2[s2]))
					if score<10:
						row='-'.join([s1,s2])
						finns+=row+'\n'	
		self.writeToFile(finns,'finn.txt')
		
def main():
	start=time()
	detector=Detector()
	detector.fillInDataDicts(files)
	detector.findExacts()
	detector.findNears()
	detector.finn()
	end=time()
	runtime= end-start
	print 'Done'
	print runtime
if __name__ == "__main__":
	main()