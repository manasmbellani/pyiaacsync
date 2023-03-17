#!/usr/bin/env python3
import argparse
import os
import sys
import time

from fileasset import FileAsset

DESCRIPTION = "An example script to demonstrate using pyiaacsync for deploying infra as code in a polling manner"

CHOICES_ACTION = [
    'init',
    'delete_assets',
    'validate_configs',
    'sync_once',
    'sync'
]

HELP_ACTION = """
"Action to perform. 

init: To create a state file.
delete_assets: To remove all existing assets and update state file
validate_configs: To validate ALL the configs
sync_once: To sync the assets from spec/configs once only
sync: To continuously sync the assets from spec/configs continuously
"""


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('-a', '--action', required=True, choices=CHOICES_ACTION,
                        help=HELP_ACTION)
    parser.add_argument('-f', '--init-state-file', help="Initial state file to use, optionally")
    parser.add_argument('-if', '--init-force', action='store_true', 
        help="Force initialization of the state file aka re-create state file even if it already exists")
    args = parser.parse_args()

    # Include the IAAC Sync class
    parent_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
    sys.path.append(parent_dir)    
    from pyiaacsync import pyiaacsync

    # Execute Iaac Sync and display any exceptions generated 
    try:
        if args.action == 'init':

            if args.init_state_file:
                i = pyiaacsync.IaacSync('exampleconf', 'out-teststate.yaml', FileAsset, init=True, 
                        init_force=args.init_force, init_state_file=args.init_state_file)
            else:
                i = pyiaacsync.IaacSync('exampleconf', 'out-teststate.yaml', FileAsset, init=True,
                        init_force=args.init_force)

        elif args.action == 'delete_assets':
            i = pyiaacsync.IaacSync('exampleconf', 'out-teststate.yaml', FileAsset, delete_all_only=True)
        
        elif args.action == 'validate_configs':
            i = pyiaacsync.IaacSync('exampleconf', 'out-teststate.yaml', FileAsset, validate_configs_only=True)

        elif args.action == 'sync_once':
            i = pyiaacsync.IaacSync('exampleconf', 'out-teststate.yaml', FileAsset)

        elif args.action == 'sync': 
            while True:
                i = pyiaacsync.IaacSync('exampleconf', 'out-teststate.yaml', FileAsset)

                print(f"Waiting for a second before resyncing...")
                time.sleep(1)

        

    except Exception as e:
        print(f"Error running Iaac Sync. Exception: {e.__class__}, {e}")
