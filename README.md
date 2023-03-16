# PyIAACSync

## Introduction
infrastructure-as-code tools such as Terraform and Palumi gaining popularity and increasingly becoming neceessary to support the principles of Site Reliability Engineering (SRE). 

However, there are a couple of disadvantages in existing tools in the market:
- Terraform requires knowledge of golang to be able to sync assets
- Both Terraform and Paulmi can be quite complex for beginners to manage and maintain

PyIAACSync provides a framework which allows software engineering getting into infrastructure-as-code to easily create and sync assets which they have defined in YAML spec files, in a polled manner (non-event driven). The infrastructue can be `anything` (AWS asset, GCP asset, any SIEM detection rule) that 

Software engineers need to create the following:
1. A folder (`iaac_sync_folder`) that contains the specs/configs for the infrastructure to create
2. A simple asset python file that contains a class describing the asset with the following `static` functions:
   - validate: to validate whether the spec/config that has been supplied in the 
   - create: to create the asset via the supplied spec/config
   - delete: to delete that has been supplied via the spec/config
   - check: to check whether the asset that has been deployed matches the spec/config aka `integrity check`. If not, the asset will be re-created

Please see `Usage` section that describes the example in more detail

## Install
```
python3 -m pip install -r requirements.txt
```

## Usage
We will be using the example described in the `example` folder.

## TODO
Create a python package to put into PyPI