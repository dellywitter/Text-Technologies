
## Link Analysis

from time import *
import re, math

## Page Rank algorithm
class PageRank(object):
	
	def __init__(self):
		self.N=0; #number of pages/nodes/ids
		self.incoming=dict() #for every email address, there's a list of all emails that point to it/have sent it emails
		self.outgoing=dict() #for every email, there's a list of all emails to which this email has sent
		self.nodes=[]
		self.ranks=dict()
		self.sinks=[]
		self.sinks_rank=dict()
		self.hubs=dict()
		self.auths=dict()
		
	# open a text file
	def open_file(self,file_name):
		f = open(file_name, 'r')
		try:
		    text = f.readlines()
		finally:
			f.close()
		return text
		
	# preprocess the text file and feed the 2 dictionaries with the emails' links		
	def process(self,file_name):
		text=self.open_file(file_name)
		for line in text:
			line=re.split('[\\s]+',line)#remove the /r and /n
			key=line[1]
			v=line[2]
			
			if key!=v:#check if the email is not sent to the person him/herself
				if key in self.outgoing:
					self.outgoing[key].append(v)
				else:
					self.outgoing[key]=[v]
				if v in self.incoming:
					self.incoming[v].append(key)
				else:
					self.incoming[v]=[key]

		l1=self.outgoing.keys()
		l2=self.incoming.keys()
		self.sinks=set(l2)-set(l1)
		self.nodes=list(set(l1+l2))
		
		self.N=len(self.nodes)
		print self.N
		print len(self.outgoing)
		print len(self.incoming)
			
	# calculation of the page rank of each page/email/node
	def calc_pr(self):
		l=0.80 # lambda as in the assignment sheet
		# assign initial values=all are equal at first iteration
		for k2 in self.nodes:
			self.ranks[k2]=1.0/float(self.N)
		# run the algorithm for the first 10 iterations only
		somedict=dict()
		for steps in range(10):
			steps+1
			print "Progress", steps
			sinkSum=0
			for s in self.sinks:
				sinkSum+=self.ranks[s]   
			for k in self.nodes:
				theSum=0
				if k in self.incoming:
					ins=self.incoming[k]				
				# calculate the sum of Pageranks of the page pointing to the current node(page)
				# over the number of outgoing links from that node(page)
					for i in ins:
						outs=self.outgoing[i]
						numOfOuts=len(outs)
						theSum+=float(self.ranks[i]/numOfOuts)				
				self.ranks[k]=((1-l)+(l*sinkSum))/float(self.N)+l*(theSum)
		somedict=sorted(self.ranks.iteritems(), key=lambda (kk,v): (v,kk))
		c= len(somedict)-10
		output=''
		for c in range(c,len(somedict)):
			output+=str(round(somedict[c][1],8))+' ' + somedict[c][0]+ '\n'
		print output
		return output

# calculate the hubs and authorities scores
	def hits(self):
		# initialize hubs and authorities to
		powerN=math.pow(self.N, -0.5)
		for node in self.nodes:
			self.hubs[node]=powerN
			self.auths[node]=powerN
		
		for steps in range(10):
			steps+1
			print "Progress", steps
			normH=0
			normA=0
			for n in self.nodes:
				sumAuths=0
				if n in self.outgoing:	
					for auths in self.outgoing[n]:
						sumAuths+=self.auths[auths]
				normA+=sumAuths*sumAuths
				self.hubs[n]=sumAuths
			normA = math.sqrt(normA)		
			for n in self.nodes:
				self.auths[n]=self.auths[n]/float(normA)
			
			for n in self.nodes:
				sumHubs=0
				if n in self.incoming:
					for hubs in self.incoming[n]:
						sumHubs+=self.hubs[hubs]
				self.auths[n]=sumHubs
				normH+=sumHubs*sumHubs
			normH = math.sqrt(normH)	

			for n in self.nodes:
				self.hubs[n]=self.hubs[n]/float(normH)
			
			
		
		somedict=sorted(self.auths.iteritems(), key=lambda (kk,v): (v,kk))
		c= len(somedict)-10
		output=''
		for c in range(c,len(somedict)):
			output+=str(round(somedict[c][1],8))+' ' + somedict[c][0]+ '\n'
		print output
		
		print "Hubs score for jeff.dasovich@enron.com: ", round(self.hubs['jeff.dasovich@enron.com'],8)
		print "Auth score for jeff.dasovich@enron.com: ", round(self.auths['jeff.dasovich@enron.com'],8)
		
		return output

def main():
	start=time()
	pr=PageRank()
	pr.process('graph.txt')
	#output=pr.calc_pr()
	
	pr.hits()
	#outfile = open("pr.txt","w")
	#outfile.write(output)
	#outfile.close()
	end=time()
	t=end-start
	print t
if __name__=="__main__":
	main()