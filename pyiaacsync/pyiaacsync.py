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
    """Exception generated when an asset is not deleted
    """
    pass

class FileNotFoundException(Exception):
    """Exception generated when a file has not been found
    """
    pass

class FileAlreadyExists(Exception):
    """Exception generated when a file already exists
    """
    pass

class ConfigFileInvalidSyntax(Exception):
    """Exception generated when an invalid config gets merged
    """
    pass

class IaacSync:
    """Class used for deploying and syncing IAAC assets defined in an IAAC Sync folder (`iaac_sync_folder`) (e.g. a folder managed via git 
    for version control) that contains various configs describing how to create assets using the `asset` functions
    """
    def __init__(self, iaac_sync_folder, state_file, asset, conf_file_extensions=CONFIG_FILE_EXTENSIONS, 
            init=False, init_force=False, init_state_file=None, delete_all_only=False, validate_configs_only=False):
        """Function to sync spec configs defined in IAAC Sync folder 

        Args:
            iaac_sync_folder (str): The IAAC Sync folder path which contains the spec for asset to create
            state_file (str): The path of the state which will be used for syncing the assets
            asset (object): A class that represents the asset to sync. The asset is an class which defines the validate, check, 
                create, delete methods
            conf_file_extensions (list, optional): List of extensions in iaac_sync_folder. Defaults to CONFIG_FILE_EXTENSIONS.
            init (bool, optional): Initialize the state file only. Defaults to False.
            init_state_file (str, optional): An optional initial state file to use when performing initialize. Defaults to None.
            init_force (bool, optional): Force initialization even if init file exists. Defaults to False.
            delete_all_only (bool, optional): Delete all the assets that have been created and clean the state file. Defaults to `False`.
            validate_configs_only (bool, optional): _description_. Defaults to False.
        """
        self.iaac_sync_folder = iaac_sync_folder
        self.state_file = state_file
        self.asset = asset
        self.conf_file_extensions = conf_file_extensions
        self.state = {}
        if init:
            self.init_state(init_state_file, init_force)
        elif delete_all_only:
            self.__delete_assets()
        elif validate_configs_only:
            self.__validate_configs()
        else:
            self.__sync_assets()

    def init_state(self, init_state_file=None, init_force=False):
        """Create a new state file, or use an existing state file if it exists
        
        Args:
            init_state_file (str, optional): Path to Initial stae file to use, if any. Defaults to None
            init_force (bool, optional): Force initialization even if init file already exists. 
        """
        if init_state_file:
            if os.path.isfile(init_state_file):
                if (not os.path.isfile(self.state_file)) or (init_force and os.path.isfile(self.state_file)):
                    with open(init_state_file, 'r') as f1:
                        with open(self.state_file, "w") as f2:
                            f.write(f1.read())
                else:
                    raise FileAlreadyExists(f"State file: {self.state_file} already exists. Use `init_force` flag to force re-creation")
            else:
                raise FileNotFoundException(f"Init state file: {init_state_file} not found")
        else:
            # Create a new state file
            if (not os.path.isfile(self.state_file)) or (init_force and os.path.isfile(self.state_file)):
                with open(self.state_file, "w") as f:
                    f.write('{}')
            else:
                raise FileAlreadyExists(f"State file: {self.state_file} already exists. Use `init_force` flag to force re-creation")

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
            raise FileNotFoundException(f"State file: {self.state_file} not found. Was init run?")
        return was_state_read

    def __delete_assets(self):
        """Delete all the assets that have been previously created, and update state file
        """
        if self.read_state():
            if self.state:
                state_config_paths = list(self.state.keys())
                for config_path in state_config_paths:
                    asset_id = self.state[config_path].get('asset_id', None)
                    if self.asset.delete(asset_id):
                        # Remove the asset tracking from the state since it is no longer being tracked in git
                        del self.state[config_path]
                        
            self.write_state()

    def __validate_configs(self):
        """Simply validate ALL configurations that exist in config files in IAAC Sync folder

        Raises:
            ConfigFileInvalidSyntax: A config in the state file is not accurate
        """

        # Loop through each config fie in the IAAC Sync folder
        for dir_path, _, files in os.walk(self.iaac_sync_folder):
            for f in files:
                config_path = os.path.join(dir_path, f)

                # Read the config from file
                config = ''
                try:
                    with open(config_path, "r") as f:
                        config = yaml.safe_load(f)
                except Exception as e:
                    raise ConfigFileInvalidSyntax(f"Config file: {config_path} syntax invalid. Error: {e.__class__}, {e}")

                # Validate whether the config is correctly provided before syncing
                if config:
                    self.asset.validate(config)
                    
    def __sync_assets(self):
        """Sync assets by comparing the file hashes of config file and recreating file

        Raises:
            FileNotFoundException: When the state file is not found
            ConfigFileInvalidSyntax: If config spec file's content is deemed invalid
        """
        all_config_files = []
        
        if self.read_state():
            
            # Loop through each config fie in the IAAC Sync folder
            for dir_path, _, files in os.walk(self.iaac_sync_folder):

                for f in files:
                    
                    # Work only with the conf files
                    if any([f.endswith(ext) for ext in self.conf_file_extensions]):
                        
                        config_path = os.path.join(dir_path, f)

                        # Keep track of ALL the asset config files
                        all_config_files.append(config_path)

                        # Calculate the hash for config which will be checked to see if they have changed
                        config_hash = self.__calculate_hash(config_path)
                        state_conf = self.state.get(config_path, None)
                        
                        # Get the hash of existing assets. If it doesn't exist then 
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
                        try:
                            with open(config_path, "r") as f:
                                config = yaml.safe_load(f)
                        except Exception as e:
                            raise ConfigFileInvalidSyntax(f"Config file: {config_path} syntax invalid. Error: {e.__class__}, {e}")

                        # Validate whether the config is correctly provided before syncing
                        if config:
                            if self.asset.validate(config):
                                
                                # Checking if the asset that currently exists matches the config in 'git'
                                is_asset_in_sync = True
                                if asset_id:
                                    is_asset_in_sync = self.asset.check(asset_id, config)

                                # If the spec file has changed OR is brand new, then create the asset again
                                if (not state_hash) or (state_hash != config_hash) or not is_asset_in_sync:

                                    # Recreate the asset
                                    asset_id =  self.__recreate_asset(config_path, asset_id, config)

                                    if asset_id:
                                        # Update the state file with the hash and the new asset ID created
                                        self.state[config_path]['hash'] = config_hash
                                        self.state[config_path]['asset_id'] = asset_id 

            # Delete any assets which are not in the config spec (git)
            if self.state:

                # Read all the config spec keys and loop through them
                state_config_paths = list(self.state.keys())
                for config_path in state_config_paths:

                    # Check if any are not in the config specs
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

