#!/usr/bin/env python
import hashlib
import os
import yaml

CONFIG_FILE_EXTENSIONS = [".yaml", ".yml"]

class AssetNotCreatedException(Exception):
    """Exception generated when an asset is not created
    """
    pass

class AssetNotDeletedException(Exception):
    pass

class FileNotFoundException(Exception):
    pass

class ConfigFileInvalidSyntax(Exception):
    pass

class IaacSync:
    def __init__(self, iaac_sync_folder, state_file, asset, conf_file_extensions=CONFIG_FILE_EXTENSIONS, init=False, delete_all=False):
        self.iaac_sync_folder = iaac_sync_folder
        self.state_file = state_file
        self.asset = asset
        self.conf_file_extensions = conf_file_extensions
        self.state = {}
        if init:
            self.init_state()
        if delete_all:
            self.__delete_assets()
        else:
            self.__sync_assets()

    def init_state(self):
        """Create a new state file
        """
        with open(self.state_file, "w") as f:
            f.write('{}')

    def write_state(self):
        """Write the state to state file
        """
        with open(self.state_file, "w") as f:
            yaml.dump(self.state, f)

    def read_state(self):
        """Read the state from the state file
        """
        was_state_read = False
        if os.path.isfile(self.state_file):
            with open(self.state_file, "r") as f:
                self.state = yaml.safe_load(f)
                was_state_read = True
        else:
            raise FileNotFoundException(f"State file: {self.state_file} not found. Was init?")
        return was_state_read

    def __delete_assets(self):
        if self.read_state():
            if self.state:
                state_config_paths = list(self.state.keys())
                for config_path in state_config_paths:
                    asset_id = self.state['config_path'].get('asset_id', None)
                    if self.asset.delete(asset_id):
                        # Remove the asset tracking from the state since it is no longer being tracked in git
                        del self.state[config_path]


    def __sync_assets(self):
        """Sync assets by comparing the file hashes of config file and recreating file

        Raises:
            FileNotFoundException: When the state file is not found
            ConfigFileInvalidSyntax: If config file path was invalid
        """
        all_config_files = []
        
        if self.read_state():
            
            # Loop through each config fie in the IAAC Sync folder
            for dir_path, _, files in os.walk(self.iaac_sync_folder):

                for f in files:
                    
                    # Work only with the conf files
                    if any([f.endswith(ext) for ext in self.conf_file_extensions]):
                        
                        config_path = os.path.join(dir_path, f)

                        all_config_files.append(config_path)

                        config_hash = self.__calculate_hash(config_path)
                        state_conf = self.state.get(config_path, None)
                        
                        state_hash = ''
                        asset_id = ''

                        if state_conf:
                            state_hash = state_conf['hash']
                            asset_id = state_conf['asset_id']
                        else:
                            self.state[config_path] = {
                                'asset_id': '',
                                'hash': '',
                            }

                         # Read the config from file
                        config = ''
                        with open(config_path, "r") as f:
                            config = yaml.safe_load(f)

                        # Validate whether the config is correctly provided before syncing
                        if self.asset.validate(config):
                            
                            # If the spec file has changed OR is brand new, then create the asset again
                            is_asset_in_sync = True
                            if asset_id:
                                is_asset_in_sync = self.asset.check(asset_id, config)

                            if (not state_hash) or (state_hash != config_hash) or not is_asset_in_sync:

                                try:
                                    # Recreate the asset
                                    asset_id =  self.__recreate_asset(config_path, asset_id, config)

                                    if asset_id:
                                        # Update the state file with the hash and the new asset ID created
                                        self.state[config_path]['hash'] = config_hash
                                        self.state[config_path]['asset_id'] = asset_id 

                                except Exception as e:
                                    raise ConfigFileInvalidSyntax(f"Config file: {config_path} syntax invalid. Error: {e.__class__}, {e}")


            if self.state:
                state_config_paths = list(self.state.keys())
                for config_path in state_config_paths:
                    if config_path not in all_config_files:
                        asset_id = self.state[config_path].get('asset_id', None)
                        if asset_id:
                            if self.asset.delete(asset_id):
                                # Remove the asset tracking from the state since it is no longer being tracked in git
                                del self.state[config_path]

            self.write_state()

        else:
            raise FileNotFoundException(f"State file: {self.state_file} not found. Was file init or state file not copied")

    def __calculate_hash(self, file_path):
        """Function calculates SHA256 hash for a file path

        Args:
            file_path (str): Path to the file found for which hash must be calculated

        Raises:
            FileNotFoundException: Config file not found

        Returns:
            str: Readable SHA256 hash OR None, if file not found 
        """
        readable_hash = ""
        if os.path.isfile(file_path):
            with open(file_path,"rb") as f:
                bytes = f.read()
                readable_hash = hashlib.sha256(bytes).hexdigest();
        else:
            raise FileNotFoundException(f"File: {file_path} not found")

        return readable_hash

    def __recreate_asset(self, file_path, existing_asset_id, config):
        """Recreate (delete and create) an asset based on the 

        Args:
            file_path (str): File path to the config file (to be used when printing error messages)
            existing_asset_id (str): Existing asset ID to delete
            config (str): Config  representing the object

        Returns:
            str: ID of the asset that was created successfully, otherwise None.

        Raises:
            AssetNotCreatedException: If the asset could not be created
            AssetNotDeletedException: If the asset could not be deleted
        """
        asset_id = None

        if existing_asset_id:
            if self.asset.delete(existing_asset_id):
                asset_id = self.asset.create(config)
            else:
                raise AssetNotDeletedException(f"Asset with config in file {file_path} could not be deleted")
            
        else:
            asset_id = self.asset.create(config)

            if not asset_id:
                raise AssetNotCreatedException(f"Asset with config in file {file_path} could not be created")
            
        return asset_id

