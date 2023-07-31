#!/usr/bin/env python3
import os

class FileAssetWithUpdate:
    """This is an example of how to use the IAAC Sync folder to create text files which contain our text
        Refer to the exampleconf folder for structure of the text files

        Each spec config consists of the following format:
        ```
        filepath: <Filepath where to write the content>
        text: <What text should be present in the file>
        ```
    """

    def update(asset_id, config, **args):
        """Custom method to update the file if it already exists in the state
        
        Args:
            asset_id (str): Existing Asset ID to update
            config (dict): Configuration/Spec describing the asset
            args (dict): Adding optional arguments

        Returns:
            bool: Whether the asset was updated successfully
        """
        asset_updated_successfully = False
        print(f"Updating file with Asset ID: {asset_id}...")
        try:
            text = config['text']
            filepath = config['filepath']
            if os.path.isfile(filepath):
                print(f"Writing text: {text} to filepath: {filepath}...")
                with open(filepath, 'w') as f:
                    f.write(text)
                asset_updated_successfully = True
            else:
                print(f"File: {filepath} not found")
        except Exception as e:
            print(f"Error creating asset with config: {config}. Error: {e.__class__}, {e}")

        return asset_updated_successfully

    def validate(config, **args):
        """Custom method to validate whether the syntax of the config file provided is correct

        Args:
            config (dict): Configuration/Spec describing the asset
            args (dict): Adding optional arguments

        Returns:
            bool: Whether the syntax of the spec config file is correct 
        """
        validated = False

        if 'message' in args:
            print(f"Printing optional message: {args['message']}")

        try:
            if 'text' in config: 
                if 'filepath' in config:
                    validated = True
                else:
                    print(f"Missing filepath field in config: {config}")
            else:
                print(f"Missing text field in config: {config}")
        except Exception as e:
            print(f"Error validating asset with config: {config}. Error:  {e.__class__}, {e}")

        return validated

    def check(asset_id, config, **args):
        """Custom method for integrity checking aka check whether the current with asset ID (`asset_id`) 
        has same config as the spec/config provided as assets could be changed in the background without
        updating the IAAC Sync folder (source of truth). 

        This is invoked everytime a sync is being performed. 

        If the state doesn't match config, then asset will be deleted and re-created

        If we don't wish to check whether the current state matches, then simply return `True`. In such
        a case, asset will only be created IF the config has been changed in IAAC Sync folder

        Args:
            asset_id (str): Unique identifier identifying the asset which was built
            config (dict): Configuration/Spec (source of truth)
            args (dict): Adding optional arguments

        Returns:
            bool: Whether the asset is in sync (aka matches the config provided) 
        """
        asset_in_sync = False 
        
        current_text = ''
        current_filepath = ''

        if 'message' in args:
            print(f"Printing optional message: {args['message']}")

        try:
            with open(asset_id, 'r+') as f:
                current_text = f.read()
                current_filepath = asset_id

            if current_text == config['text'] and current_filepath == config['filepath']:
                asset_in_sync = True
            else:
                print(f"Asset with ID: {asset_id} out of sync with config: {config}")

        except Exception as e:
            print(f"Error checking asset state with ID: {asset_id}. Error:  {e.__class__}, {e}")

        return asset_in_sync

    def create(config, **args):
        """Custom method to create the asset based on the config provided

        Args:
            args (dict): Adding optional arguments

        Returns:
            bool: Whether the asset has been created successfully
        """
        asset_id = ''

        if 'message' in args:
            print(f"Printing optional message: {args['message']}")

        try:
            text = config['text']
            filepath = config['filepath']
            print(f"Writing text: {text} to filepath: {filepath}...")
            with open(filepath, 'w+') as f:
                f.write(text)
            asset_id = filepath

        except Exception as e:
            print(f"Error creating asset with config: {config}. Error: {e.__class__}, {e}")

        return asset_id

    def delete(asset_id, **args):
        """Custom method to delete the existing asset.        

        Args:
            asset_id (str): Unique identifier identifying the asset to delete
            args (dict): Adding optional arguments

        Returns:
            bool: Whether the asset has been deleted successfully OR it no longer exists
        """
        deleted_successfully = False

        if 'message' in args:
            print(f"Printing optional message: {args['message']}")

        print(f"Deleting filepath: {asset_id}...")
        try:
            if os.path.isfile(asset_id):
                os.remove(asset_id)
                deleted_successfully = True
            else:
                deleted_successfully = True
                
        except Exception as e:
            print(f"Error deleting file: {asset_id}. Error: {e.__class__}, {e}")

        return deleted_successfully
