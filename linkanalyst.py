## Link Analysis

from time import *
import re, math, copy, string
## Page Rank algorithm
class LinkAnalyst(object):
	def __init__(self):
		self.N=0; #number of pages/nodes/ids
		self.incoming=dict() #for every email address, there's a list of all emails that point to it/have sent it emails
		self.outgoing=dict() #for every email, there's a list of all emails to which this email has sent
		self.nodes=[]#all nodes/people/email addresses in the company
		self.ranks=dict()#dicr of current ranks for PR
		self.old_ranks=dict()#ranks from the previous iteration in PR
		self.sinks=[]#list of sink nodes(no outgoing links)
		self.sinks_rank=dict()#their ranks
		self.hubs=dict()#hubs dictionary
		self.auths=dict()#authorities dictionary
		self.important=[]#list of important people in the company, by PR
		self.relations=[]# all pairs of connected people with duplicates, no pairs of the same person sending to himself though
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
			self.relations.append((key,v))
			if key!=v:#check if the email is not sent to the person him/herself
				self.relations.append((key,v))#add to the list of all pairs of addresses
				#separate in incoming and outgoing
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
		self.sinks=set(l2)-set(l1)#sink nodes are all in incoming that are not in outgoing, a.k.a not out emails
		self.nodes=list(set(l1+l2))#get all nodes no duplicates
		self.N=len(self.nodes)#num of nodes
	# calculation of the page rank of each page/email/node
	def pagerank(self):
		l=0.80 # lambda as in the assignment sheet
		# assign initial values=all are equal at first iteration
		for k2 in self.nodes:
			self.old_ranks[k2]=1.0/float(self.N)
		# run the algorithm for the first 10 iterations only
		sortedRanks=dict()
		for steps in range(10):
			steps+1
			print "Progress", steps
			sinkSum=0
			for s in self.sinks:
				sinkSum+=self.old_ranks[s]   
			for k in self.nodes:
				theSum=0
				if k in self.incoming:
					ins=self.incoming[k]				
				# calculate the sum of Pageranks of the page pointing to the current node(page)
				# over the number of outgoing links from that node(page)
					for i in ins:
						outs=self.outgoing[i]
						numOfOuts=len(outs)
						theSum+=float(self.old_ranks[i]/numOfOuts)				
				self.ranks[k]=((1-l)+(l*sinkSum))/float(self.N)+l*(theSum)
				
			self.old_ranks=copy.copy(self.ranks)
		sortedRanks=sorted(self.old_ranks.iteritems(), key=lambda (kk,v): (v,kk))
		c= len(sortedRanks)-10
		output=''
		for c in reversed(range(c,len(sortedRanks))):
			if sortedRanks[c][0] not in self.important:
				self.important.append(sortedRanks[c][0])
			output+=str(round(sortedRanks[c][1],8))+' ' + sortedRanks[c][0]+ '\n'
		print output
		return output
# calculate the hubs and authorities scores
	def hits(self):
		# initialize hubs and authorities to
		powerN=float(math.pow(self.N, -0.5))
		for node in self.nodes:
			self.hubs[node]=powerN
			self.auths[node]=powerN
		# run the algorithm for 10 steps
		for steps in range(10):
			steps+1
			print "Progress", steps
			normA,normH=0,0
			#for each node/email calculate the authority and the hub scores
			for n in self.nodes:
				sumAuths=0
				if n in self.outgoing:
				#hub score of X equals the sum of all authority scores of links X points to
					for outs in self.outgoing[n]:
						sumAuths+=self.auths[outs] 
					self.hubs[n]=sumAuths#add the sum of auth scores to the hub of the current node n
					normH+=math.pow(sumAuths,2)#get the square of the sum of the new hub score and add it to the normalizing factor
			
			#normalize result s.t. the sum of squares of hub scores==1
			normH = math.sqrt(normH)	
			for n in self.outgoing:
				self.hubs[n]=self.hubs[n]/float(normH)	
			for n in self.incoming:
				sumHubs=0
				if n in self.incoming:	
				#authority score of X == the sum of all hub scores of links pointing to X
					for ins in self.incoming[n]:
						sumHubs+=self.hubs[ins]
					normA+=math.pow(sumHubs,2)
					self.auths[n]=sumHubs
			normA = math.sqrt(normA)	
			for n in self.incoming:
				self.auths[n]=self.auths[n]/float(normA)
				
		#sort the ranks dictionary by value
		sortedRanks=sorted(self.auths.iteritems(), key=lambda (kk,v): (v,kk))
		c= len(sortedRanks)-10
		outputA, outputH ='',''
		for c in reversed(range(c,len(sortedRanks))):
			if sortedRanks[c][0] not in self.important:
				self.important.append(sortedRanks[c][0])
			outputA+=str(round(sortedRanks[c][1],8))+' ' + sortedRanks[c][0]+ '\n'
		print outputA		
		sortedRanks=sorted(self.hubs.iteritems(), key=lambda (kk,v): (v,kk))
		c= len(sortedRanks)-10
		for c in reversed(range(c,len(sortedRanks))):
			outputH+=str(round(sortedRanks[c][1],8))+' ' + sortedRanks[c][0]+ '\n'
		print outputH
		print "Hubs score for jeff.dasovich@enron.com: ", round(self.hubs['jeff.dasovich@enron.com'],8)
		print "Auth score for jeff.dasovich@enron.com: ", round(self.auths['jeff.dasovich@enron.com'],8)
		return (outputA,outputH)
	
	def graphIt(self):
		rels=[]# to store pairs of importnat people/nodes connected between each other
		numberEmails=[]#number of emails between the same pair of people
		for relation in self.relations:
			node1,node2=relation
			if (node1 in self.important):
				if (node2 in self.important) and node1!=node2:
					rels.append((node1, node2))
	  	relsNoDup = list(set(rels))#no duplicate connections
	  	for rel in relsNoDup: 
	  		numberEmails.append(rels.count(rel))
		f = open('graph.dot','w')
		f.write("digraph G { \n")
		for i in range(len(relsNoDup)):
			(fst,snd) = relsNoDup[i]
			headfst, s,t= fst.partition('@')
			headsnd, s,t= snd.partition('@')
			output = "  \""+headfst+"\" -> \""+headsnd+"\" [label = \""+str(numberEmails[i]/2)+"\"]; "+"\n"
			f.write(output)
		f.write("}")
		f.close()
	#write the output in a file with file name 'name'
	def wr(self,output,name):
		outfile = open(name,"w")
		outfile.write(output)
		outfile.close()
	
def main():
	start=time()
	la=LinkAnalyst()	
	la.process('graph.txt')
	output=la.pagerank()
	la.wr(output,'pr.txt')
	outputA,outputH=la.hits()
	la.wr(outputA,'auth.txt')
	la.wr(outputH,'hubs.txt')
	la.graphIt()
	end=time()
	t=end-start
	print t
if __name__=="__main__":
	main()