#!/usr/bin/env python3
import os
import sys

from fileasset import FileAsset

if __name__ == "__main__":

    # Include the IAAC Sync class
    parent_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
    sys.path.append(parent_dir)    
    import iaacsync

    # Execute Iaac Sync and display any exceptions generated 
    try:
        i = iaacsync.IaacSync('exampleconf', 'out-teststate.yaml', FileAsset, delete_all_only=True)

    except Exception as e:
        print(f"Error running Iaac Sync. Exception: {e.__class__}, {e}")
