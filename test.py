#!/usr/bin/env python3
import iaacsync
import os

class FileAsset:
    def create(config):
        text = config['text']
        filepath = config['filepath']
        print(f"Writing text: {text} to filepath: {filepath}...")
        with open(filepath, 'w+') as f:
            f.write(text)
        return filepath

    def delete(filepath):
        print(f"Deleting filepath: {filepath}...")
        deleted_successfully = False
        try:
            if os.path.isfile(filepath):
                os.remove(filepath)
                deleted_successfully = True
        except Exception as e:
            print(f"Error deleting file: {filepath}. Error: {e.__class__}, {e}")
        return deleted_successfully

if __name__ == "__main__":
    i = iaacsync.IaacSync('/tmp/testfileconf', '/tmp/teststate.txt', FileAsset)