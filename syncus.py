import os
import argparse
import shutil
import threading
import json
import logging
log = logging.getLogger(__name__)

# Set terminal ANSI code colors
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAILRED = '\033[91m'
ENDC = '\033[0m'

def modTime(file_path):
    '''Get the file modification time'''
    return os.path.getmtime(file_path)

def load_config():
    '''Load config from json file'''
    try:
        json_config_file = open("./config.json")
        conf_content = json_config_file.read()
        json_config_file.close()
    except:
        new_content = {
            "os": os.name,
            "sync": 60,
            "paths": []
        }
        write_config(new_content)
        conf_content = new_content
    config = json.loads(conf_content)
    if conf_content["name"] != os.name:
        log.error("this config is not for this os")
        exit(1)
    return config

def write_config(content):
    '''write config to json file'''
    json_config_file = open("./config.json", "w")
    json_config_file.write(json.dumps(content))
    json_config_file.close()

def add_paths(orig_path, copy_path, config):
    paths = config["paths"]
    paths.append([orig_path, copy_path])
    config["paths"] = paths
    write_config(config)

def del_paths(orig_path, copy_path, config):
    paths = config["paths"]
    paths.remove([orig_path, copy_path])
    config["paths"] = paths
    write_config(config)

def set_sync_time(sec, config):
    config["sync"] = sec
    write_config(config)

def cp_file(src_path, copy_path):
    try:
        copy_file = open(copy_path)
    except:
        try:
            shutil.copyfile( src_path, copy_path, None, follow_symlinks=True)
        except:
            log.error("user doesn't have rights to: " + copy_path)
    else:    
        srcT = modTime(src_path)
        copyT = modTime(copy_path)
        if copyT > srcT:
            try:
                shutil.copyfile( src_path, copy_path, None, follow_symlinks=True)
            except:
                log.error("user doesn't have rights to: " + copy_path)
        else:
            return

def sync(src, copy):
    if os.path.isdir(src):
        src_name = os.path.basename(src)
        if os.path.isdir(copy):
            os.mkdir(copy + "/" + src_name)
            dirlist = os.listdir(src)
            for rec in dirlist:
                sync(src=src + dirlist[rec],copy=copy + dirlist[rec])
        else:
            copy_parent = os.path.dirname(copy)
            os.mkdir(copy_parent + "/" + src_name)

    else:
        if os.path.isdir(copy):
            log.info("copying file" + src)
            cp_file(src, copy + src_name)
        else:
            copy_parent = os.path.dirname(copy)
            cp_file(src, copy_parent + src_name)


def sync_start(config):
    paths = config["paths"]
    for rec in paths:
        thread = threading.Thread(target=sync, args=(paths[rec][0],paths[rec][1]))
             


def main():
    logging.basicConfig(filename="log/syncus.log", level=logging.INFO)
    log.info("started syncus")

if __name__ == '__main__':
    main()