#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" 
    This script produces closure compiled JS code, in args[1]/dist/compiled.

    Usage : ./closure.py <PATH_TO_PROJECT_ROOT> [--Recursive True|False] [--Mirror True|False]

    Author: h4n0sh1
    Created: 24/08/2023
    License: GPL
"""

import requests
import json, os
import shutil, re
import argparse

parser = argparse.ArgumentParser(description='Code minimizer - Google closure compiler')
parser.add_argument('path',type=str, default="./", help='Path of the app. root folder')
parser.add_argument('--recursive', type=bool, default=False, help='Search and compile any JS file under subfolders')
parser.add_argument('--mirror', type=bool, default=True, help='Miror root directory structure in the dist.')
args = parser.parse_args()

dirpath = args.path
recursive = args.recursive
mirror = args.mirror

def compile_js(js_code):
    url = "https://closure-compiler.appspot.com/compile"
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    body={
        "js_code": js_code,
        #"compilation_level": "WHITESPACE_ONLY",
        "output_format": "text",
        "output_info": "compiled_code"
    }
    x = requests.post(url, data=body, headers=headers)
    print(">>>> js_code")
    print(js_code)
    print(">>>> resp")
    print(x.text)
    return x.text

def check_path(path): 
    if not os.path.exists(path):
        os.makedirs(path,0o777)

def compile_files(file_list,src,dst):
    for f in file_list:
        print(f"Processing file: {f} ...")
        p = os.path.join(pre,f)
        #d = os.path.join(out,f)
        with open(os.path.join(src,f), "r") as r, open(p,"w") as o:
            for line in r:
                if not line.isspace():
                    o.write(line)
        with open(p,"r") as r:
            ret = compile_js(r.read())
            with open(os.path.join(dst,f),"w") as w:
                w.write(ret)

def get_suffix(subfolder):
    out = re.search(r'.*[\/|\\](.*)', dirpath).group(1)
    if subfolder != dirpath:
        out = os.path.join(out,re.search(r'' + re.escape(dirpath) + r'[\/|\\]?(.*)',subfolder).group(1))
    return out

def mirror_files(file_list,subfolder):
    #print(file_list)
    path_suffix = get_suffix(subfolder)
    for f in file_list:
        #print(f"{f}isdir?f{os.path.isdir(os.path.join(dirpath,f))}")
        #print(f"Leaf = {path_suffix}")
        src = os.path.join(subfolder,f)
        dst = os.path.join(out, path_suffix)
        check_path(dst)
        print(f"Copying {src} to {os.path.join(dst,f)}")
        shutil.copyfile(src,os.path.join(dst,f))

def mirror_folder(folder):
    file_list = [f for f in os.listdir(folder) if f.endswith('sjcl.js') or not (f.endswith('.js') or os.path.isdir(os.path.join(folder,f)))]
    mirror_files(file_list, folder)

subfolders = [ f.path for f in os.scandir(dirpath) if f.is_dir() ]
subfolders.remove(os.path.join(dirpath,'dist'))
pre = os.path.join(dirpath,'dist','closure','pre')
out = os.path.join(dirpath,'dist','closure', 'compiled')

check_path(pre)
check_path(out)

if mirror:
    mirror_folder(dirpath)
file_list = [f for f in os.listdir(dirpath) if f.endswith('.js')]
compile_files(file_list,dirpath,os.path.join(out, get_suffix(dirpath)))

while len(subfolders) != 0:
    for s in subfolders:
        if mirror:
            mirror_folder(s)
            subfolders += [ f.path for f in os.scandir(s) if f.is_dir()]
            file_list = [f for f in os.listdir(s) if f.endswith('.js')]
            if recursive:
                compile_files(file_list,s,os.path.join(out, get_suffix(s)))
            subfolders.remove(s)

# TO-DO : 
#   Add list of source dir for JS to compile
#   Add list of exception dir to exclude 
#   Add progress bar



    

