
import os, sys, shlex
from termcolor import *
from pathlib import Path

clear = lambda: os.system("clear")

toptext = "Welcome to VDesk!"
topcolor = "green"

HELP = """
Welcome to VDesk - Virtual Command-Line Desktop
-----------------------------------------------
exampledir1/
exampledir2/
examplefile1.txt
examplefile2.py
examplefile3.log
-----------------------------------------------
To open a file:
	~ examplefile1.txt
To open a directory:
	~ exampledir1.txt
To go back 1 directory:
	~ ..


To create an empty file:
	~ mkfile myfile.txt
To create an empty directory:
	~ mkdir mydir


To open the first object, that starts with "abc":
	~ abc*

Get current path:
	~ :path

Count all objects in current directory:
	~ :c
	or
	~ :count

Get all objects that starts with "abc":
	~ list abc
Get all objects that have "abc" in its name:
	~ in abc

Print help:
	~ :?
	or
	~ :help

"""


config = {
	"filecolor": "magenta",
	"foldercolor": "yellow",
	"rmconfirm": True,
	"cddiraftercreation": True,
	"toplength": 50,
	"printemptyfile": True,
	"printemptyfolder": True,
	"basicfileviewercolors": True
}
try:
	with open("/etc/vdesk.conf") as conffile:
		for line in conffile.read().split("\n"):
			if line == "" or line[0] == "#":
				continue
			var, value = line.split()
			if value == "true":
				value = True
			elif value == "false":
				value = False
			if value.isdigit():
				config[var] = int(value)
			else:
				config[var] = value
except FileNotFoundError:
	cprint("/etc/vdesk.conf not found, using defaults.","red","on_white")
	input("*enter*")

toplen = config["toplength"]
filecolor = config["filecolor"]
foldercolor = config["foldercolor"]

def top():
	global toptext, topcolor
	cprint("-"*toplen, "grey", "on_white")
	cprint(toptext+(" "*toplen)[len(toptext):], topcolor, "on_white")
	cprint("-"*toplen, "grey", "on_white")

def enter():
	cprint("\nPress ENTER to continue","red","on_yellow",end="")
	input()

def showfile(filename):
	global toptext, topcolor
	clear()
	toptext = filename
	topcolor = "magenta"
	top()
	with open(os.path.abspath(filename), encoding="utf-8") as file:
		fr = file.read()
		if fr == "" or fr == "\n":
			cprint("Empty","red")
		else:
			for line in fr.split("\n"):
				if line == "":
					continue
				if line[0] == "#":
					cprint(line, "red")
				else:
					rcolors = {"\"":"green","'":"green","true":"green","false":"red","True":"green","False":"red","None":"yellow","while":"yellow"} # Replacecolors
					for what in rcolors:
						color = rcolors[what]
						line = line.replace(what,colored(what,color))
					print(line)
	enter()

while True:
	clear()
	top()
	items = os.listdir(path=os.getcwd())
	if len(items) == 0 and config["printemptydir"]:
		cprint("Nothing in here","red")
	folders = []
	files = []

	for item in items:
		fullitem = os.path.abspath(item)
		if item[0] == ".":
			continue
		if os.path.isfile(item):
			files.append(item)
		else:
			folders.append(item)

	files = sorted(files)
	folders = sorted(folders)

	for folder in folders:
		cprint(folder+"/",foldercolor)
	for file in files:
		cprint(file,"white")

	print()
	cprint("~","white","on_green",end="")
	x = input(" ").strip()

	if x == "":
		toptext = os.getcwd().split("/")[-1]+"/"
		topcolor = foldercolor
		continue

	if x in folders:
		toptext = str(x)+"/"
		topcolor = foldercolor
		os.chdir(x)
		continue

	elif x in files:
		showfile(x)
		toptext = os.getcwd().split("/")[-1]+"/"
		topcolor = filecolor
		continue

	elif x == "..":
		os.chdir("/".join(os.getcwd().split("/")[:-1]))
		toptext = os.getcwd().split("/")[-1]+"/"
		topcolor = foldercolor
		continue

	elif x == ".":
		continue

	elif x == "*":
		continue

	elif x[-1] == "*":
		for folder in folders:
			if folder[:len(x)-1] == x[:-1]:
				toptext = str(folder)+"/"
				topcolor = foldercolor
				os.chdir(folder)
				break

		for file in files:
			if file[:len(x)-1] == x[:-1]:
				showfile(file)
				break

		topcolor = foldercolor
		toptext = os.getcwd().split("/")[-1]+"/"

		if not topcolor == filecolor and not topcolor == foldercolor:
			toptext = "Nothing found"
			topcolor = "red"
		continue
	else:
		if len(x.split()) == 1 and x[0] != ":":
			toptext = "File/Folder not found"
			topcolor = "red"
			continue

	if x.split()[0] == "mkfile":
		try:
			os.system("touch "+os.getcwd()+"/"+x.split()[1])
		except IndexError:
			toptext = "Usage: mkfile filename"
			topcolor = "red"
	elif x.split()[0] == "mkdir":
		try:
			os.system("mkdir "+os.getcwd()+"/"+x.split()[1])
		except IndexError:
			toptext = "Usage: mkdir dirname"
			topcolor = "red"

	elif x.split()[0] == "list" or x.split()[0] == "in":
		y = shlex.split(x)[1]
		L = []
		for folder in folders:
			try:
				if folder[:len(y)] == y and x.split()[0] == "list":
					L.append(folder+"/")
				elif y in folder and x.split()[0] == "in":
					L.append(folder+"/")
			except:
				pass
		for file in files:
			try:
				if file[:len(y)] == y and x.split()[0] == "list":
					L.append(file)
				elif y in file and x.split()[0] == "in":
					L.append(file)
			except:
				pass
		if len(L) == 1:
			toptext = str(len(L)) + " result"
		else:
			toptext = str(len(L)) + " results"
		if len(L) == 0:
			topcolor = "red"
		else:
			topcolor = "green"
		clear()
		top()
		for item in L:
			if item[-1] == "/":
				cprint(item, "yellow")
			else:
				cprint(item, "white")
		enter()
	elif x.split()[0] == "rm":
		if x.split()[1] == "*":
			cprint("Do you really want to remove all files? [y/*]","red",end=" ")
		else:
			cprint("Do you really want to remove this file? ("+str(x.split()[1])+") [y/*]","red",end=" ")
		yn = input().lower()
		if yn == "y":
			os.system("sudo rm "+str(x.split()[1]))

	elif x[0] == ":":
		if x[1:] == "path":
			toptext = os.getcwd()
			topcolor = "magenta"
			continue

		elif x[1:] == "count" or x[1:] == "c":
			count = len(folders)+len(files)
			if count == 1:
				toptext = str(count) + " item"
			else:
				toptext = str(count) + " items"
		elif x[1:] == "?" or x[1:] == "help":
			clear()
			toptext = "Help"
			topcolor = "green"
			top()
			print(HELP)
			enter()
			toptext = os.getcwd().split("/")[-1]+"/"
			topcolor = "yellow"
			continue

		elif x[1:] == "exit" or x[1:] == "quit" or x[1:] == "q":
			break

	else:
		toptext = "Invalid command"
		topcolor = "red"

clear()
