#!/usr/bin/env python3
import iaacsync
import os

class FileAsset:
    def validate(config):
        validated = False
        if 'text' in config: 
            if 'filepath' in config:
                validated = True
            else:
                print(f"Missing filepath field in config: {config}")
        else:
            print(f"Missing text field in config: {config}")

        return validated

    def check(filepath, config):
        asset_in_sync = False 
        
        current_text = ''
        current_filepath = ''
        try:
            with open(filepath, 'r+') as f:
                current_text = f.read()
                current_filepath = filepath

            if current_text == config['text'] and current_filepath == config['filepath']:
                asset_in_sync = True
            else:
                print(f"Asset with ID: {filepath} out of sync with config: {config}")
        except Exception as e:
            print(f"Error checking asset state with ID: {filepath}. Error:  {e.__class__}, {e}")

        return asset_in_sync

    def create(config):
        text = config['text']
        filepath = config['filepath']
        print(f"Writing text: {text} to filepath: {filepath}...")
        with open(filepath, 'w+') as f:
            f.write(text)
        return filepath

    def delete(filepath):
        deleted_successfully = False
        print(f"Deleting filepath: {filepath}...")
        try:
            if os.path.isfile(filepath):
                os.remove(filepath)
                deleted_successfully = True
            else:
                deleted_successfully = True
                
        except Exception as e:
            print(f"Error deleting file: {filepath}. Error: {e.__class__}, {e}")

        return deleted_successfully

if __name__ == "__main__":
    i = iaacsync.IaacSync('/tmp/testfileconf', '/tmp/teststate.txt', FileAsset)
