#!/usr/bin/python 

# programming goals# 
# find way to input dates
# check on last day in matrix vs last day in my table
# email if there's an error
# /home/mark/Documents/ReportAutomation/execengagementautomation.py

import sys
import os
import string as s
import json
from sqlalchemy import *
from datetime import *

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

fileset=json.loads(open('/home/mark/Documents/ReportAutomation/filelist.json').read())
s
# make db connection
# this is the string format you need:
db = create_engine("postgresql+psycopg2://YOURUSERNAME:YOURPASSWORD@10.211.26.100:5439/ancestry")
db_con=db.connect()

print "connection successful"

me = "yourname@emailaddress"  # you may wish to 
you = "yourname@emailaddress"

# Create message container - the correct MIME type is multipart/alternative.
msg = MIMEMultipart('alternative')
msg['Subject'] = "Automated Sql Error"
msg['From'] = fileset['emailto']
msg['To'] = fileset['emailfrom']


def send_message(msgtext):
	print 'in send message', msgtext
	msgtext=msgtext.replace('<','')
	msgtext=msgtext.replace('>','')
	try:
		# Record the MIME types of both parts - text/plain and text/html.
		part1 = MIMEText(msgtext, 'html')

		# Attach parts into message container.
		# According to RFC 2046, the last part of a multipart message, in this case
		# the HTML message, is best and preferred.
		msg.attach(part1)

		# Send the message via local SMTP server.
		s = smtplib.SMTP('smtprelay.myfamily.int',25)

		# sendmail function takes 3 arguments: sender's address, recipient's address
		# and message to send - here it is sent as one string.
		s.sendmail(me, you, msg.as_string())
		s.quit()
	except:	
		e = sys.exc_info()[0]
		el=sys.exc_traceback.tb_lineno

		print 'Error: %s' % e 
		print 'lineno: %s' % el	
		sys.exit()


def eval_substitutions(f1,query_type_flag,dateset):
	sqlstr1=''
	print f1,query_type_flag,dateset
	try:
		if query_type_flag=='default':
			pass
		elif query_type_flag=='sub':
			print 'sub section'
			input  	= open(f1,'r')
			filename=os.path.basename(f1)
			path=os.path.dirname(f1)
			base=filename.split('.')[0]
#			print 'base', base, 'path', path
			outputname=path+'/'+base+'clean.txt'
			output	= open(outputname, 'w')
			for line in input:			
# 				print line	
				templine=line
				for k in dateset.keys():
# 					#  microtest this
# 					print 'k',k,'replacement',dateset[k]
#					if k in line:
# 						print 'k in line'
					templine=templine.replace(k, str(dateset[k]))	
				output.write(templine)
# 			
			input.close()
			output.close()	
		elif query_type_flag=='update':
			print 'update section'
			checkscript=fileset["checkscript"]
			print 'checkscript',checkscript
			lastdate=execute_sql(checkscript,'return')
			lastdate=lastdate.fetchone()[0]
			print 'lastdate', lastdate, type(lastdate)
#			lastdate=datetime.strptime(lastdate.strftime('%Y-%m-%d'),"%Y-%m-%d")
			lastdate=lastdate+timedelta(days=1)
			print 'lastdate', lastdate, type(lastdate)

			#updatedate=datetime.strptime(str(datetime.now()).split('.')[0],"%Y-%m-%d") # %H:%M:%S
			updatedate=datetime.strptime(datetime.now().strftime("%Y-%m-%d"),"%Y-%m-%d")
			updatedate=updatedate+timedelta(days=-5)
			#strftime("%Y-%m-%d")
			print 'updatedate', updatedate, type(updatedate)
#http://stackoverflow.com/questions/25646200/python-convert-timedelta-to-int-in-a-dataframe
			t=(updatedate-lastdate).days
#			print 't',t, type(t)
			
			# now that we've compared datetimes, turn them into strings
			lastdate=lastdate.strftime('%Y-%m-%d')
			updatedate=updatedate.strftime('%Y-%m-%d')
			if t>=1:
				print 't>1'
				dateset={}
				dateset["lastdate"]="\'"+lastdate+"\'"
				dateset["updatedate"]="\'"+updatedate+"\'"
				print 'dateset', dateset
				print 'f1', f1
				input= open(f1,'r')
				filename=os.path.basename(f1)
				path=os.path.dirname(f1)
				base=filename.split('.')[0]
				outputname=path+'/'+base+'clean.txt'
				output	= open(path+'/'+base+'clean.txt', 'w')
				for line in input:			
					templine=line
					for k in dateset.keys():
						templine=templine.replace(k, str(dateset[k]))	
					output.write(templine)
			
				input.close()
				output.close()	
			elif t<1:	
				print 't', t, 'is less than 1 day, exiting...'
				sys.exit(0)
		
		return outputname
	except:
 		e= sys.exc_info()[0]
		el=sys.exc_traceback.tb_lineno
 		print 'Error: %s' % e 
		print 'lineno: %s' % el	
		
def execute_sql(sqlstr1,runorreturn='run'):
	print 'in execute_sql'
	try:
		if runorreturn=='run':
			
			db_con.execute(sqlstr1)
			db_con.execute("commit")
		elif runorreturn=='return':
			result=db_con.execute(sqlstr1)
			return result
		
	except:	
		e = sys.exc_info()[0]
		el=sys.exc_traceback.tb_lineno

		msgtext='python error is: %s' %e+ ' line no is: %s' %el +' sql statement was %s' %sqlstr1
		print 'msgtext', msgtext, type(msgtext), type(e)
		send_message(msgtext)

#		print 'Error: %s' % e 
#		print 'lineno: %s' % el	
		sys.exit()

		
def compile_execute_sql(f1):
	print 'compile_execute_sql'
	try:
		sqlstr1 = ""
		print 'f1',f1
		filename=os.path.basename(f1)
		path=os.path.dirname(f1)
		base=filename.split('.')[0]
		input	= open(f1, 'r')
		for line in input:
			line=line.strip().split('//')[0]
			line=line.strip().split('#')[0]
			line=line.strip()
			lineup=s.upper(line.strip())
			print 'line', line
			if len(line)>0:
				firstchar=line[0]
				if firstchar<>'//' and firstchar<>'#':
					if lineup<>'GO':
						sqlstr1=sqlstr1+" "+line
					elif lineup=='GO' and len(sqlstr1)>0:
						print 'sqlstr execution', sqlstr1
						print 'len', len(sqlstr1)
						if len(sqlstr1)>0:			
							execute_sql(sqlstr1)	
							sqlstr1 = ""
								
	except:
		e = sys.exc_info()[0]
		el=sys.exc_traceback.tb_lineno
		print 'Error: %s' % e 
		print 'lineno: %s' % el

def processfiles(fileset):
	dateset=fileset['dateset']
	fileorder=sorted(fileset['files'].keys())
# 	print dateset,fileorder
	
	for k in fileorder:
		f=fileset['files'][k][0]
		query_type_flag=fileset['files'][k][1]
		print 'doing substitutions.'
		f1=eval_substitutions(f,query_type_flag,dateset)
		print 'f1', f1
 		print 'trying to execute' 
		compile_execute_sql(f1)

processfiles(fileset)				
		
