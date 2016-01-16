#!/usr/bin/env python 
# -*- coding: utf-8 -*-
import subprocess,sys,os,getpass,copy,random,math,time,json
def sub_doc(doc,sub,pw,pw_num,edq):#generate substituted doc based on sub list
	if sub == 's2':
		pw_num = sorted(pw_num)
	sub = [x for x in ''.join([str(pw_num[i]**pw_num[i+1]) for i in range(len(pw)-1)])]	#generate long digit list from password
	sub = sub_zero(sub)	#reduce number of zeros and obfuscate
	sub = [int(sub[i:i+3]) for i in range(len(sub)) if len(sub[i:i+3])==3]	#generate list of 3-digit numbers by slicing sub11	
	doc = ''.join([unichr(ord(doc[i])^sub[i%len(sub)]) for i in range(len(doc))])
	return doc
def perm_doc(doc,perm,pw,pw_num,edq):		#generate permuted doc based on perm list
	if perm == 'p1':
		set_size = len(doc)/100; num_set_sizes = 1; bs = 100
	elif perm == 'p2':
		set_size = 100; num_set_sizes = len(doc)/set_size; bs = 1
	iter = float(sum(pw_num[:len(pw)/2]))/sum(pw_num[len(pw)/2:]) 	#generate iterator
	if iter < 1: iter = 1/iter			#make iter > 1
	iter = int(iter*100)/100.			#round to two decimal places
	n = iter; map = []; new_doc = ''
	while len(map) < set_size:
		digit = int(set_size/2.*(1.+math.sin(n)))	#generate map values until map is filled
		if digit not in map:						#add unique values to map
			map.append(digit)
		n+=iter
	if edq == 'e':
		for i in range(num_set_sizes):		
			for j in range(len(map)):
				new_doc += doc[i*set_size+map[j]*bs:i*set_size+map[j]*bs+bs]
	elif edq == 'd':
		new_set = ['']*set_size			
		for i in range(num_set_sizes):
			for j in range(len(map)):
				new_set[map[j]] = doc[i*set_size+j*bs:i*set_size+j*bs+bs]
			new_doc += ''.join(new_set)
	return new_doc
def sub_zero(sub_num):
	sub_zero = list('0123456789')	
	for i in range(len(sub_num)):	#iteratively substitute zeroes for values in sub_zero to prevent large numbers of zeroes appearing together
		if sub_num[i] == '0':
			sub_num[i] = sub_zero[i%len(sub_zero)]
	return ''.join(sub_num)
def sub_perm(actions,doc,pw,pw_num,edq):
	for i in actions:
		if i[0] == 's':
			doc = sub_doc(doc,i,pw,pw_num,edq)
		elif i[0] == 'p':
			doc = perm_doc(doc,i,pw,pw_num,edq)
		print 'next iteration:';print doc[:100];print
	return doc
def open_file(action,file):
	if action == 'e':
		if os.path.isdir(file):	#check for directory
			print '   \"'+file+'\" is a directory'
			serialize = ''
			while serialize not in list('ynq'):
				serialize = raw_input('   Serialize and encrypt the directory? (y n q): ').lower()
			if serialize in list('qn'): quit()
			files = subprocess.Popen(['ls '+file],stdout=subprocess.PIPE,shell=True).communicate()[0].split()
			serial_files = {'folder':file}
			#sf = ''
			for each_file in files:
				with open(file+'/'+each_file,'r') as f: 
					doc = f.read()
				serial_files[each_file] = doc#.encode('utf-16')
			return json.dumps(serial_files,encoding='latin1')####################
		else:	#open file (not a directory)
			with open(file,'r') as f:
				doc = f.read()
			return json.dumps({file:doc},encoding='latin1')
	elif action == 'd':
		if os.path.isdir(file):
			print 'File is a directory. Cannot decrypt';quit()
		with open(file,'r') as f:
			return f.read().decode('utf8')	
def ask_remove_file(file):
	remove = ''
	while remove not in list('ynq'):
		remove = raw_input('Remove \''+file+'\'? (y n q): ').lower()
	if remove == 'q': quit()		
	elif remove == 'y':
		subprocess.Popen(['rm -r '+file],shell=True)
		quit()
def quit():
	print;print '  Exiting...';print;sys.exit()	
'''main()'''
def main():	
	print;print '*** enc2.py ***';print '*** encrypt and decrypt files and folders ***'
	print 'Files and folders available in this directory: '
	subprocess.Popen(['ls'],shell=True)
	time.sleep(.5)
	which_file = ''
	while not os.path.exists(which_file):
		which_file = raw_input('select file/folder for processing: ')	
	edq = ''
	while edq not in list('edq'):
		edq = raw_input('Encrypt, decrypt or quit? (e d q): ').lower()
	if edq == 'q': quit()
	pw = ''
	while len(pw) < 2:
		pw = getpass.getpass('Enter password (min. 2 char): ')
	pw_num = [ord(i) for i in pw]	#store numerical equivalents of pw as list	
	if edq	== 'e':
		doc = open_file('e',which_file)	#open file, *or* open and serialize folder contents
		doc += ''.join([unichr(int(random.random()*100)) for x in range(100-(len(doc)%100))])	#make doc length divisible by 100
		print;print '## original document: ##';print doc[:100];print
		doc = sub_perm(['s1','p1','s2','p2'],doc,pw,pw_num,edq)	
		enc_file = raw_input('Enter file name for encrypted document: ')
		with open(enc_file,'w') as f:
			f.write(doc.encode('utf8'))
		ask_remove_file(which_file)
	elif edq == 'd':
		doc = open_file('d',which_file)
		print;print '## original document: ##';print doc[:100];print
		doc = sub_perm(['p2','s2','p1','s1'],doc,pw,pw_num,edq)
		for i in range(len(doc)-1,-1,-1):
			if doc[i] == '}':
				doc = doc[0:i+1]
				break
		try:
			file_dict = json.loads(doc)
		except:
			print 'Data cannot be processed. Wrong password?';quit()
		if 'folder' in file_dict:
			folder = file_dict['folder']
			if os.path.exists(folder):
				overwrite = ''
				while overwrite not in list('ynq'):
					overwrite = raw_input('Folder \''+folder+'\' already exists. Replace? (y n q): ')
				if overwrite in list('qn'): quit()
				elif overwrite == 'y':
					subprocess.Popen(['rm -r '+folder],shell=True)				
			subprocess.Popen(['mkdir '+folder],shell=True)
			time.sleep(.5)	#ensure enough time to write new folder before writing files to it
			for key in file_dict:
				if key != 'folder':
					with open('./'+str(folder)+'/'+str(key),'wb') as f:
						f.write(file_dict[key].encode('latin1'))
		else:	#no folder; single file 
			filename = [str(x) for x in file_dict.keys()][0]
			with open(filename,'w') as f:
				f.write(file_dict[filename])	
		ask_remove_file(which_file)
		quit()

if __name__ == '__main__':
	main()