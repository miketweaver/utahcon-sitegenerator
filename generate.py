#!/usr/bin/env python
from __future__ import print_function
import yaml
import os
import json

main_path = os.getcwd()  
build_folder = 'build/'

file_path = []
from distutils.dir_util import copy_tree


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
	return index

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

def gen_footer():
	file = open(main_path + "/foot.html", "r") 
	item = file.read()
	file.close()
	return item

def gen_item(name, path, url, size, date, file_type):
	file = open(main_path + "/file_item.html", "r") 
	item = file.read()
	file.close()

	output = item % (name, path + name, url, name, file_type, name, size, date)
	return output

def loadLevel(input):
	global file_path

	if file_path == []:
		index_file = create_home();
	else:
		index_file = create_index(file_path);

	files = list()
	directories = list()

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
		for directory in directories:
			index_file += directory

	if files != [None, None]:
		# sort files, hopefully by date
		files = sorted(files)
		for file in files:
			file = generate_file(file[1],file[2], file_path)
			index_file += file

	index_file += gen_footer()

	file = open("index.html","w") 
	file.write(index_file)
	file.close()
	os.chdir('../')

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

## Copy Static Files

fromDirectory = main_path + "/static"
toDirectory = main_path + "/" + build_folder + "static"

print("Copying " + fromDirectory + " to " + toDirectory)
copy_tree(fromDirectory, toDirectory)

## PROFIT!!
