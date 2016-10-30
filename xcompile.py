#!/usr/bin/env python3

#######################################################
# SDVCrosscompile version 1.1.0.1
#######################################################

import os
import os.path
import glob
import shutil
import sys
import subprocess
import zipfile
import tkinter
from tkinter import messagebox
from tkinter import simpledialog
import re
import getpass
import json

#######################################################
# User settings
#######################################################
PROGRAMS = {
	"xbuild" : {
		"windows" : "C:/Program Files (x86)/Mono/bin/xbuild.bat",
		"linux" : "/usr/bin/xbuild",
		"mac" : "/usr/bin/xbuild"
	}
}
PLATFORMS = {
	"windows" : { "libs" : "lib-windows", "buildargs" : ["/p:DefineConstants=XCOMPILE", "/p:Configuration=Release"], "targetdir" : "bin/Release" },
	"linux" : { "libs" : "lib-linux", "buildargs" : ["/p:DefineConstants=XCOMPILE","/p:Configuration=Release"], "targetdir" : "bin/Release" },
	"mac" : { "libs" : "lib-mac", "buildargs" : ["/p:DefineConstants=XCOMPILE","/p:Configuration=Release"], "targetdir" : "bin/Release" }
}

#######################################################
# Internal variables
#######################################################
TITLE_UNDERLINE_CHARS = 50
TKINTER_ROOT_WINDOW = None
CLI_PARSED_ARGUMENTS = None
PROGRAM_NAME = "SDVCrosscompile version 1.1.0.1"
SKIP_ALL_ASKING = False

def parse_cli():
	
	modes = [ "--no-silverplum", "--auto-silverplum", "--no-graphics", "--no-zip", "--keep-dependencies", "--output", "--sln", "--xbuild-executable", "--override-calling-platform"] 
	modes += [ "--lib-%s" % x for x in PLATFORMS.keys() ]
	modes += [ "--build-args-%s" % x for x in PLATFORMS.keys() ]
	modes += [ "--build-targetdir-%s" % x for x in PLATFORMS.keys() ]
	
	mode = ""
	result = {}
	
	for arg in sys.argv[1:]:
		
		if arg in modes:
			mode = arg
			
			if not mode in result:
				result[mode] = []
				
		elif mode:
				
			result[mode].append(arg)
			
		else:
			print("Error while parsing arguments: Before setting a value, you need to provide its purpose!")
			
	return result
			

def cli_single(cli, entry, default = []):
	
	if not entry in cli:
		
		if default:
			return default[0]
		else:
			print("You did not provide a value for " + entry)
			
	elif len(cli[entry]) > 1:
		
		print("You provided more than one value for " + entry)
		exit(1)
		
	else:
		
		return cli[entry][0]
		

def cli_list(cli, entry, default = []):
	
	if not entry in cli:
		
		if default:
			return default
		else:
			print("You did not provide a value for " + entry)
	
	else:
		
		return cli[entry]
		

def cli_flag(cli, entry):
	
	return entry in cli


def ask_input( message, defaultVal = "" ):
	
	if SKIP_ALL_ASKING:
		return defaultVal

	if TKINTER_ROOT_WINDOW:
		return simpledialog.askstring("Crosscompiler", message, initialvalue = defaultVal)

	else:

		if defaultVal:
			return input( "%s [%s]:" % (message,defaultVal) ) or defaultVal
		else:
			return input( "%s " % (message) )

def ask_question( message ):
	
	if SKIP_ALL_ASKING:
		return False

	if TKINTER_ROOT_WINDOW:
		return messagebox.askquestion("Crosscompiler", message) == "yes"

	else:
		return input( "%s [y/n]" % (message) ).lower() == "y"
		
		
def ask_list(message, defaultVal = []):
	
	if SKIP_ALL_ASKING:
		return defaultVal
	
	string = ask_input(message + " (separate with ',')", ",".join(defaultVal))
	
	return [ x.strip() for x in string.split(",") if x.strip() ]

def get_current_platform_string():

	autodetect = ""

	if sys.platform == "linux":
		autodetect = "linux"
	elif sys.platform == "win32":
		autodetect = "windows"
	elif sys.platform == "darwin":
		autodetect = "mac"
	
	return cli_single(CLI_PARSED_ARGUMENTS, "--override-calling-platform", [autodetect])
			
def filename_without_extension(path):
	
	return os.path.splitext(os.path.basename(path))[0]

def print_title(text, underline_char):

	print()
	print(text)
	print(underline_char * TITLE_UNDERLINE_CHARS)
	print()

def create_path_if_not_exists(path):

	if not os.path.exists(path):
		os.makedirs(path)

def delete_if_exists(path):

	if os.path.isdir(path):
		shutil.rmtree(path)
	elif os.path.isfile(path):
		os.remove(path)
		
def get_program_xbuild():
	
	return cli_single(CLI_PARSED_ARGUMENTS, "--xbuild-executable", [PROGRAMS["xbuild"][get_current_platform_string()]])
	
def get_output_path(solutionname):
	
	return cli_single(CLI_PARSED_ARGUMENTS, "--output", ["xbuild_result_%s" % solutionname]).replace("%solution%", solutionname)
	
def get_lib_path(platform):
		
	return cli_single(CLI_PARSED_ARGUMENTS, "--lib-" + platform, [PLATFORMS[platform]["libs"]])
	
def get_build_arguments(platform):
	
	return cli_single(CLI_PARSED_ARGUMENTS, "--build-args-" + platform, [PLATFORMS[platform]["buildargs"]])
	
def get_build_targetdir(platform):
	
	return cli_single(CLI_PARSED_ARGUMENTS, "--build-targetdir-" + platform, [PLATFORMS[platform]["targetdir"]])

def find_solutions():
		
	return [ os.path.abspath(x) for x in cli_list(CLI_PARSED_ARGUMENTS, "--sln", [ os.path.abspath(x) for x in glob.glob("*.sln")])]
	
def create_silverplum_mod_json(projectname, projectpath):

	if not cli_flag(CLI_PARSED_ARGUMENTS, "--auto-silverplum"):
		if not ask_question("No SilVerPLuM config found. Do you want to create it now?"):
			return True
			
	global SKIP_ALL_ASKING
	SKIP_ALL_ASKING = cli_flag(CLI_PARSED_ARGUMENTS, "--auto-silverplum")

	name = ask_input("Modification name", projectname)
	if not name:
		return False
		
	description = ask_input("Description", "")
	
	categories = [x for x in ask_list("Categories") if x]

	id = create_silverplum_id(name)

	author = ask_input("Author", getpass.getuser())
	if not author:
		return False
		
	license = ask_input("License", "MIT")
	if not license:
		return False
		
	url = ask_input("Website", "https://stardewvalley.net/")
	if not url:
		return False
		
	version = ask_input("Version", "1.0")
	if not version:
		return False
		
	requirements = [create_silverplum_version(x) for x in ask_list("Required mods", [ "stardewvalley", "smapi" ]) if create_silverplum_version(x)]
	
	SKIP_ALL_ASKING = False
	
	json_string = json.dumps({
	
		"id" : id,
		"name" : name,
		"author" : author,
		"license" : license,
		"url" : url,
		"version" : version,
		"requires" : requirements,
		"categories" : categories,
		"content" : {
		
			"windows" : {
				"name" : "Windows build",
				"description" : "Contains the mod built for Windows",
				"default" : True,
				"platforms" : ["windows"],
				"pipeline" : "file",
				"installables" : { "" : "stardewvalley://Mods/" + projectname }
				},
			"linux" : {
				"name" : "Linux build",
				"description" : "Contains the mod built for Linux",
				"default" : True,
				"platforms" : ["linux"],
				"pipeline" : "file",
				"installables" : { "" : "stardewvalley://Mods/" + projectname }
				},
			"mac" : {
				"name" : "Windows build",
				"description" : "Contains the mod built for Mac",
				"default" : True,
				"platforms" : ["mac"],
				"pipeline" : "file",
				"installables" : { "" : "stardewvalley://Mods/" + projectname }
				}
		
		}
	
	}, sort_keys=False, indent=4, separators=(',', ' : '))
	
	
	
	f = open(projectpath + "/mod.json", "w")
	f.write(json_string)
	f.close()
	
	if not os.path.isfile(projectpath + "/mod-description.md"):
		f = open(projectpath + "/mod-description.md", "w")
		f.write("## " + name + "\n")
		f.write(description)
		f.close()

	return True

def build_silverplum(projectname, projectpath, destinationdir):

	print_title("SilVerPLuM packaging", ".")

	if not os.path.isfile(projectpath + "/mod.json"):
		if not create_silverplum_mod_json(projectname, projectpath):
			return False
	
	print("SilVerPLuM package for " + projectname)
	
	projectdestinationdir = destinationdir + "/" + projectname + "_Silverplum"
	create_path_if_not_exists(projectdestinationdir)
	
	shutil.copy(projectpath + "/mod.json", projectdestinationdir + "/mod.json")
	
	if os.path.isfile(projectpath + "/mod-description.md"):
		shutil.copy(projectpath + "/mod-description.md", projectdestinationdir + "/mod-description.md")
		
	for platform in PLATFORMS:
		
		platform_src_dir = destinationdir + "/" + projectname + "_" + platform.capitalize() + "/" + projectname
		platform_dst_dir = projectdestinationdir + "/" + platform
		
		shutil.copytree(platform_src_dir, platform_dst_dir)
		
		
	# Zip it
	if not cli_flag(CLI_PARSED_ARGUMENTS, "--no-zip"):
		shutil.make_archive(projectdestinationdir, "zip", projectdestinationdir)

	return True

def copy_compiled_binaries(platform, projectname, projectdir, destinationdir):
	
	print("Copying binaries to result directory")
	binarydir = projectdir + "/" + get_build_targetdir(platform)

	if not os.path.isdir(binarydir):
		print("No binaries found. Cancelling.")
		return False

	projectdestinationdir = destinationdir + "/" + projectname + "_" + platform.capitalize() + "/" + projectname
	
	shutil.copytree(binarydir, projectdestinationdir)

	# Zip it
	if not cli_flag(CLI_PARSED_ARGUMENTS, "--no-zip"):
		zipdir = destinationdir + "/" + projectname + "_" + platform.capitalize()
		shutil.make_archive(zipdir, "zip", zipdir)

	return True
	

def install_build_libraries(platform, projectdir):
	
	lib_path = os.path.abspath(get_lib_path(platform))
	targetdir = projectdir + "/" + get_build_targetdir(platform)
	
	shutil.copytree(lib_path, targetdir)

def uninstall_build_libraries(platform, projectdir):
	
	lib_path = os.path.abspath(get_lib_path(platform))
	targetdir = projectdir + "/" + get_build_targetdir(platform)
	
	for e in os.listdir(lib_path):
		delete_if_exists(targetdir + "/" + e)
	
def build_for(platform, solutionfile, projects):
	
	print_title("Building for " + platform.capitalize(), ".")

	xbuild = get_program_xbuild()
	lib_path = os.path.abspath(get_lib_path(platform))
	
	command = [xbuild, solutionfile] + get_build_arguments(platform)
	env = os.environ.copy()
	
	env["STARDEWVALLEY_DIR"] = lib_path
	env["GamePlatform"] = platform.capitalize()
		
	for projectdir in projects.values():
		install_build_libraries(platform, projectdir)

	print("Starting build ...")
	print("STARDEWVALLEY_DIR set to " + env["STARDEWVALLEY_DIR"])

	process = subprocess.Popen(command, env=env, stderr=subprocess.STDOUT)
	process.wait()
	
	if not cli_flag(CLI_PARSED_ARGUMENTS, "--keep-dependencies"):
		for projectdir in projects.values():
			uninstall_build_libraries(platform, projectdir)

	return process.returncode == 0

def create_silverplum_id(string):

	return re.sub("[^a-z0-9_.\\-]+", "-", string.lower())
	
def create_silverplum_version(string):
	
	string = string.strip().lower()
	
	if not string:
		return ""
	
	cell = [x for x in re.split("(<|>|=)", string) if x]
	
	if len(cell) == 2:
		return string
	elif len(cell) == 1:
		return string + ">0"
	else:
		return ""

def get_projects(solutionfile):

	result = { }

	f = open(solutionfile, "r")
	solutiondir = os.path.dirname(solutionfile)

	for line in f:

		if line.startswith("Project("):

			cell = line.strip().split(",")
			projectname = cell[0].split("=")[1].strip(" \"")
			
			for w in cell[1:]:
				projectfile = solutiondir + "/" + w.strip(" \"").replace("\\", "/")
				
				if os.path.isfile(projectfile):
					result[projectname] = os.path.abspath(os.path.dirname(projectfile))

	f.close()
	
	return result

def build_solution(solutionfile):
	
	print("Solution file is " + solutionfile)
	projects = get_projects(solutionfile)
	
	if not projects:
		print("No projects detected! Skipping solution!")
		return False
	
	print("Found following projects: " + ", ".join(projects))
	
	success = True
	
	destinationdir = get_output_path(filename_without_extension(solutionfile))
	delete_if_exists(destinationdir)
	
	for platform in PLATFORMS:
		
		# First clear all project results
		for projectdir in projects.values():
			
			print("Deleting bin and obj in " + projectdir)
			delete_if_exists(projectdir + "/bin")
			delete_if_exists(projectdir + "/obj")
		
		if success:
			success &= build_for(platform, solutionfile, projects)
		
		if success:			
			for projectname in projects:				
				success &= copy_compiled_binaries(platform, projectname, projects[projectname], destinationdir)
				
	for projectdir in projects.values():
		
		if success and not cli_flag(CLI_PARSED_ARGUMENTS, "--no-silverplum"):
			success &= build_silverplum(projectname, projects[projectname], destinationdir)
	
	return success
	

			
		
		
def main():
	
	global CLI_PARSED_ARGUMENTS
	CLI_PARSED_ARGUMENTS = parse_cli()

	if not cli_flag(CLI_PARSED_ARGUMENTS, "--no-graphics"):
		global TKINTER_ROOT_WINDOW
		TKINTER_ROOT_WINDOW = tkinter.Tk()
		TKINTER_ROOT_WINDOW.withdraw()

	if not get_current_platform_string():

		print("Cannot determine current platform! sys.platform is " + sys.platform)
		exit(1)
		
	for platform in PLATFORMS:
		
		if not os.path.isdir(get_lib_path(platform)):
			
			print("Cannot find library path for %s. %s is not a folder." % (platform.capitalize(), get_lib_path(platform)))
			exit(1)

	print_title(PROGRAM_NAME, "=")
	print("Called on " + get_current_platform_string())

	solutions = find_solutions()

	if not solutions:
		print("No solutions found! Put all files next to the project's *.sln file!")
		exit(1)
		
	success = True

	for solution in solutions:		
		print_title("Building solution %s of %d" % (solutions.index(solution) + 1, len(solutions)), "*")
		success &= build_solution(solution)
		
	if success:
		
		print_title("All operations successful.", "=")
		
	else:
		
		print_title("Not successful.", "=")
		exit(1)

main()
