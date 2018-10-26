#!/usr/bin/env python
from __future__ import print_function
import yaml
import os
import json
from ics import Calendar, Event
from datetime import datetime, timedelta

main_path = os.getcwd()  
build_folder = 'build/'

file_path = []
from distutils.dir_util import copy_tree

def generate_ical(events):
	# The \n X-WR-CALNAME is VERY VERY HACKY... But it works.
	c = Calendar(creator="Utahcon.org\nX-WR-CALNAME:Utah Conferences")

	for event in events:
		if events[event].get("alt-time"):
			print("No Date, passing: " + event)
			pass
		else:
			print(events[event])
			new_event = generate_event(event, events[event].get("begin"), events[event].get("end"), events[event].get("description", events[event].get("url")), events[event].get("uid"))
			c.events.add(new_event)

	with open(main_path + "/" + build_folder + 'conferences.ics','w') as f:
		f.writelines(c)
	
	

def generate_event(name, begin, end, description, uid):
	e = Event()
	e.name = name
	e.begin = datetime.strptime(begin, "%Y%m%d")
	e.end = datetime.strptime(end, "%Y%m%d") + timedelta(days=1)
	e.description = description
	e.uid = uid
	e.make_all_day()
	return e

def safe_make_folder(folder):
    '''Makes a folder if not present'''
    try:  
        os.mkdir(folder)
    except:
        pass

def create_index(file_path):
	file = open(main_path + "/head.html", "r") 
	head = file.read()
	file.close()

	title = "Utahcon"
	navbar = """                <p class="navbar-text">
                    <a href="http://utahcon.org/">Utahcon.org</a>
"""
	url = ""
	up_one = ""
	for folder in file_path:
		title += " - " + folder
		url += folder + "/"
		name = folder
		if file_path.index(folder) == len(file_path)-1:
			navbar += "                    <span class=\"divider\">/</span>\n                    %s\n" % name
		else:
			navbar += "                    <span class='divider'>/</span>\n                    <a href='http://utahcon.org/%s'>%s</a>\n" % (url, name)
			up_one += folder + "/"

	index = head % title
	index += navbar + "                </p>\n"

	file = open(main_path + "/head_2.html", "r")
	headtwo = file.read()
	index += headtwo % up_one
	file.close()
	return index

def create_home():

	## Make the first page different
	file = open(main_path + "/main_page_head.html", "r")
	index = file.read()
	file.close()

	## Load YAML for events
	with open(main_path + "/events.yaml", 'r') as stream:
		try:
			events = yaml.load(stream)
		except yaml.YAMLError as exc:
			print(exc)

	# sort events, hopefully by name
	sorted_events = sorted(events)
	for event in sorted_events:
		if events[event].get("alt-time"):
			index += gen_event(event, events[event].get("url"), events[event].get("alt-time"))
		else:
			begin = events[event].get("begin")
			begin = datetime.strptime(begin, "%Y%m%d")
			begin = datetime.strftime(begin, "%Y/%m/%d")
			end = events[event].get("end")
			end = datetime.strptime(end, "%Y%m%d")
			end = datetime.strftime(end, "%Y/%m/%d")
			date = begin + " - " + end
			index += gen_event(event, events[event].get("url"), date)

	file = open(main_path + "/main_page_head_2.html", "r") 
	index += file.read()
	file.close()

	return index

def gen_event(name, url, date):
	file = open(main_path + "/event_item.html", "r") 
	item = file.read()
	file.close()

	output = item % (name, name, url, name, name, date)
	return output

def generate_file(file_name, file_object, file_path):
	url = file_object.get("url")
	date = file_object.get("date")
	size = file_object.get("size")
	file_extension = os.path.splitext(file_name)[1]
	file_type = get_file_format(file_object.get("type", file_extension))
	path = ""
	for folder in file_path:
		path += folder + "/"
	return gen_item(file_name, path, url, size, date, file_type)

def generate_folder(folder_name, file_path):
	date = ""
	size = ""
	file_type = "fa-folder"
	path = ""
	for folder in file_path:
		path += folder + "/"
	return gen_item(folder_name, path, folder_name+"/", size, date, file_type)

def get_file_format(file_extension):
	file = open(main_path + "/formats.json", "r") 
	formats = file.read()
	file.close()
	formats = json.loads(formats)
	return formats.get(file_extension[1:], "fa-file")

def gen_footer(file_path):
	message = "For questions, contact <a href='https://twitter.com/_bashNinja' target='_blank'>@_bashNinja</a>"
	file = open(main_path + "/foot.html", "r") 
	item = file.read()
	file.close()

	path = ""
	for folder in file_path:
		path += folder + "/"

	downloads = "Want to download all the files in the current directory?<br><code>wget -x -nH -i https://utahcon.org/%sdirectory.txt</code>\n<br>What about current directory & subfolders?\n<br><code>wget -x -nH -i https://utahcon.org/%sallfiles.txt</code>" % (path, path)
	item = item % (downloads, message) 
	return item

def gen_item(name, path, url, size, date, file_type):
	file = open(main_path + "/file_item.html", "r") 
	item = file.read()
	file.close()

	output = item % (name, path + name, url, name, name.replace("_"," "), file_type, name.replace("_"," "), size, date)
	return output

def get_subdirs(dir):
    "Get a list of immediate subdirectories"
    return next(os.walk(dir))[1]

def make_allfiles(dir):
	subdirs = sorted(get_subdirs(dir))
	for directory in subdirs:
		# For each directory, recurse in, and build its' stuff first
		# Should return with the full list of files below it
		text = make_allfiles(dir + directory + "/")

		# Write that full list to the allfiles.txt file
		file = open(dir + "/allfiles.txt","a") 
		file.write(text)
		file.close()

	# ADD current directory to the top of the list to return
	file = open(dir + "directory.txt", "r") 
	item = file.read()
	file.close()

	if subdirs == []:
		# If there ARE no subdirs, just copy /directory to allfiles.txt
		# (end of recursion)
		file = open(dir + "/allfiles.txt","w") 
		file.write(item)
		file.close()
	else:
		# If there are subdirs, ADD all files (sub folder files) to the list
		file = open(dir + "/allfiles.txt", "r") 
		item += file.read()
		file.close()

	# Should return a list of the current dir files & then the list of all subfiles.
	return item

def loadLevel(input):
	global file_path

	if file_path == []:
		index_file = create_home();
	else:
		index_file = create_index(file_path);

	files = list()
	directories = list()
	textfiles = ""
	textfiles_files = list()

	for x in input.keys():
		if isinstance(input[x], dict):
			if input[x].get('url'):
				files.append([input[x].get("date"),x,input[x]])
			else:
				directories.append(generate_folder(x, file_path))
				safe_make_folder(x)
				os.chdir(x)
				file_path.append(x)
				loadLevel(input[x])
		else:
			print("Empty Folder: " + x + ". Ignoring.")

	## This is done to ensure directories are first
	if directories != [None, None]:
		# sort directories, hopefully by name
		directories = sorted(directories)
		for directory in directories:
			index_file += directory

	if files != [None, None]:
		# sort files, hopefully by date
		files = sorted(files)
		for file in files:
			textfiles_files.append(file[2].get("url"))
			file = generate_file(file[1],file[2], file_path)
			index_file += file

	if textfiles_files != [None, None]:
		for url in textfiles_files:
			textfiles += url + "\n"

	file = open("directory.txt","w") 
	file.write(textfiles)
	file.close()

	index_file += gen_footer(file_path)

	file = open("index.html","w") 
	file.write(index_file)
	file.close()
	os.chdir('../')
	if file_path != []:
		file_path.pop(-1)

## Load YAML
with open("utahcon.yaml", 'r') as stream:
    try:
        utahcon = yaml.load(stream)
    except yaml.YAMLError as exc:
        print(exc)

## Make build folder
safe_make_folder(main_path + "/" + build_folder)
os.chdir(build_folder)

## Create initial index and then recursion!
loadLevel(utahcon)

## Create allfiles.txt
make_allfiles(build_folder)

#with os.scandir(path) as it:
#    for entry in it:
#		file = open("dir.txt","w") 
#		file.write(entry.name)
#		file.close()

## Load YAML for iCal
with open("events.yaml", 'r') as stream:
	try:
	    events = yaml.load(stream)
	except yaml.YAMLError as exc:
	    print(exc)

generate_ical(events)

## Copy Static Files

fromDirectory = main_path + "/static"
toDirectory = main_path + "/" + build_folder + "static"

print("Copying " + fromDirectory + " to " + toDirectory)
copy_tree(fromDirectory, toDirectory)

## PROFIT!!
