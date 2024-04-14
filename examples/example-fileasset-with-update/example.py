#!/usr/bin/env python3
import argparse
import os
import sys
import time

from fileassetwupd import FileAssetWithUpdate

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

def sync_error_handler(err_class, err_msg):
    """Function called when sync error handler encounters an error"""
    print(f"Error syncing an asset. Error: {err_class}, {err_msg}")

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('-a', '--action', required=True, choices=CHOICES_ACTION,
                        help=HELP_ACTION)
    parser.add_argument('-f', '--init-state-file', help="Initial state file to use, optionally")
    parser.add_argument('-if', '--init-force', action='store_true', 
        help="Force initialization of the state file aka re-create state file even if it already exists")
    args = parser.parse_args()

    # Include the IAAC Sync class
    parent_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
    sys.path.append(parent_dir)    
    from pyiaacsync import pyiaacsync

    # Passing an optional random argument to demonstrate how **args can be used
    
    random_args = {}
    ## uncomment line below to demonstrate how the random arguments can work
    #random_args = {'message': 'hello world'}

    # Execute Iaac Sync and display any exceptions generated 
    try:
        if args.action == 'init':

            if args.init_state_file:
                i = pyiaacsync.IaacSync('exampleconf', 'out-teststate.yaml', FileAssetWithUpdate, init=True, 
                        init_force=args.init_force, init_state_file=args.init_state_file,
                        **random_args)
            else:
                i = pyiaacsync.IaacSync('exampleconf', 'out-teststate.yaml', FileAssetWithUpdate, init=True,
                        init_force=args.init_force, **random_args)

        elif args.action == 'delete_assets':
            i = pyiaacsync.IaacSync('exampleconf', 'out-teststate.yaml', FileAssetWithUpdate, delete_all_only=True, 
                                    continue_sync_on_error=True, callback_on_sync_error=sync_error_handler, 
                                    **random_args)
        
        elif args.action == 'validate_configs':
            i = pyiaacsync.IaacSync('exampleconf', 'out-teststate.yaml', FileAssetWithUpdate, validate_configs_only=True,
                    args=random_args)

        elif args.action == 'sync_once':
            i = pyiaacsync.IaacSync('exampleconf', 'out-teststate.yaml', FileAssetWithUpdate, 
                                    continue_sync_on_error=True, callback_on_sync_error=sync_error_handler, 
                                    **random_args)

        elif args.action == 'sync': 
            
            while True:
                i = pyiaacsync.IaacSync('exampleconf', 'out-teststate.yaml', FileAssetWithUpdate,
                        continue_sync_on_error=True, callback_on_sync_error=sync_error_handler,
                        **random_args)

                print(f"Waiting for a second before resyncing...")
                time.sleep(1)

    except Exception as e:
        print(f"Error running Iaac Sync. Exception: {e.__class__}, {e}")
        import traceback
        print(traceback.print_exc())
