#!/usr/bin/python3 -u

# build_sc.py

# A 2020 script by Jacob Burley <j@jc0b.computer>

# bits and pieces lifted from munki_rebrand.py (https://github.com/ox-it/munki_rebrand.git)


from subprocess import Popen, PIPE
from pathlib import Path

import json
import os
import sys
import shutil
import plistlib
import requests
import glob

API_BASE_URL = "https://api.github.com/"
API_ACCEPT_TYPE = "application/vnd.github/v3+json"
BUNDLE_ID = 'com.googlecode.munki'
DEV_APP = ''
DEV_INSTALLER = ''

GIT = '/usr/bin/git'

MUNKI_REPO = 'munki/munki'
GITHUB_BASE_URL = 'https://github.com/'

verbose = True

munki_src_dir = 'munki'

def run_cmd(cmd, ret=None):
	"""Runs a command passed in as a list. Can also be provided with a regex
	to search for in the output, returning the result"""
	proc = Popen(cmd, stdout=PIPE, stderr=PIPE)
	out, err = proc.communicate()
	if verbose and out != "":
		print(out.rstrip().decode('utf-8'))
	if proc.returncode != 0:
		print(err.decode('utf-8'))
		sys.exit(1)
	else:			
		return out.rstrip().decode('utf-8')


def build_munki_tools():
	munki_path = os.path.join(root_dir, munki_src_dir)
	lux_script = os.path.join(root_dir, "build_munki.sh")

	shutil.copy(lux_script, f'{munki_path}/build_munki.sh')
	munki_path = os.path.join(root_dir, munki_src_dir)
	# build_script = os.path.join(munki_path, 'code/tools/make_munki_mpkg.sh')

	# build_cmd = [build_script, '-i', BUNDLE_ID]
	lux_cmd = ['./build_munki.sh']
	print("Compiling Munki...")
	run_cmd(lux_cmd)

def get_munki_source():
	munki_path = os.path.join(root_dir, munki_src_dir)
	print("Cloning Munki from Github...")
	git_pull = [GIT, 'clone' , GITHUB_BASE_URL+MUNKI_REPO]
	run_cmd(git_pull)
	os.chdir(munki_path)

	latest_release = get_latest_release()
	print(f"Checking out latest public release of Munki: {latest_release}")
	git_checkout = [GIT, 'checkout', latest_release]
	run_cmd(git_checkout, True)

# def build_python_framework():
# 	munki_path = os.path.join(root_dir, munki_src_dir)
# 	build_python_framework_exec = 'code/tools/build_python_framework.sh'

# 	framework_script = os.path.join(munki_path, build_python_framework_exec)
# 	build_python_framework = [framework_script]
# 	print("Building Python framework...")
# 	run_cmd(build_python_framework)

def rebrand_munki():
	rebrand_dir = 'rebrand/'
	rebrand_path = os.path.join(root_dir, rebrand_dir)
	rebrand_binary = os.path.join(rebrand_path, 'munki_rebrand.py')
	assets_path = os.path.join(rebrand_path, 'assets/')
	app_icon = os.path.join(assets_path, 'AppIcon.png')
	postinstall_script = os.path.join(assets_path, 'postinstall_script')

	munkitools_pkg = glob.glob('munkitools-[0-9]*')[0]

	rebrand_cmd = [
		'python3', rebrand_binary, 
		'--pkg', munkitools_pkg, 
		'--appname', 'Software Center', 
		'--icon-file', app_icon, 
		'--postinstall', postinstall_script, 
		'--output-file', 'software_center', 
		'--sign-package', DEV_INSTALLER, 
		'--sign-binaries', DEV_APP
	]
	print("Rebranding and signing Munki...")
	run_cmd(rebrand_cmd)

# def sign_python_framework():
	# munki_path = os.path.join(root_dir, munki_src_dir)
	# python_lib_path = os.path.join(munki_path, 'Python.framework/Versions/3.8/lib/')
	# python_bin_path = os.path.join(munki_path, 'Python.framework/Versions/3.8/bin/')
	
	# sign_libraries = ['find', python_lib_path, '-type', 'f', '-perm', '-u=x', '-exec', 'codesign', '--force', '--deep', '--verbose', '-s', DEV_APP, '{}', ';']
	# sign_binaries = ['find', python_bin_path, '-type', 'f', '-perm', '-u=x', '-exec', 'codesign', '--force', '--deep', '--verbose', '-s', DEV_APP, '{}', ';']
	# sign_dylib = ['find', python_lib_path, '-type', 'f', '-name', '\"*dylib\"', '-exec', 'codesign', '--force', '--deep', '--verbose', '-s', DEV_APP, '{}', ';']
	# sign_shared_objects = ['find', python_lib_path, '-type', 'f', '-name', '\"*so\"', '-exec', 'codesign', '--force', '--deep', '--verbose', '-s', DEV_APP, '{}', ';']

	# run_cmd(sign_libraries)
	# run_cmd(sign_binaries)
	# run_cmd(sign_dylib)
	# run_cmd(sign_shared_objects)

	# entitlements_file = os.path.join(munki_path, 'entitlements.plist')
	
	# pl = {
	# 	'com.apple.security.cs.allow-unsigned-executable-memory' : True
	# 	}
	# with open(entitlements_file, 'wb') as entitlements_fp:
	# 	plistlib.dump(pl, entitlements_fp)

	# python_app_path = os.path.join(munki_path, 'Python.framework/Versions/3.8/Resources/Python.app/')
	# python_38_path = os.path.join(munki_path, 'Python.framework/Versions/3.8/bin/python3.8')

	# sign_python_app = ['codesign', '--force', '--options', 'runtime', '--entitlements', entitlements_file, '--deep', '--verbose', '-s', DEV_APP, python_app_path]
	# sign_python_runtime = ['codesign', '--force', '--options', 'runtime', '--entitlements', entitlements_file, '--deep', '--verbose', '-s', DEV_APP, python_38_path]
	
	# print("Signing Munki's included Python with your provided Developer Account...")
	# run_cmd(sign_python_app)
	# run_cmd(sign_python_runtime)

def cleanup():
	cleanup_dir = os.path.join(root_dir, munki_src_dir)
	sc_pkg = glob.glob('software_center-[0-9]*')[0]
	sc_pkg_path = os.path.join(cleanup_dir, sc_pkg)
	shutil.move(sc_pkg_path, f'../{sc_pkg}')
	print(f"{sc_pkg} has been placed in the same directory as this script ({root_dir}). It can now be imported into Munki.")
	print("Cleaning up working directory...")
	shutil.rmtree(cleanup_dir)

def get_latest_release():
	headers = {"Accept": API_ACCEPT_TYPE}
	response = requests.get(API_BASE_URL + 'repos/' + MUNKI_REPO + '/releases', headers=headers)
	for release in response.json():
		if release["prerelease"]:
			continue
		elif not release["prerelease"]:
			return release["tag_name"]


def main():
	if os.geteuid() != 0:
		print('You must run this as root (with sudo)!', file=sys.stderr)
		exit(1)

	global root_dir
	root_dir = os.getcwd()
	get_munki_source()
	# build_python_framework()
	# sign_python_framework()
	build_munki_tools()
	rebrand_munki()
	#cleanup()

if __name__ == '__main__':
	main()
