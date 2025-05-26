# Supplementary Material

This is the supplementary material of paper **An Empirical Study of Memory Leaks in Large-Scale Open-Source C/C++ Repositories**.

The supplementary material includes **6 parts**: 

- our main dataset
- list of 80 target repositories
- SQL of OSSInsight
- candidate tools and reasons for selecting or excluding
- pipeline scripts
- memory leak related CWE-id. 

The structure of the directory is shown as follow:

````
Supplementary_material
    │   README.md						# This README file
    │   Dataset.csv    					# Our dataset of PRs related to memory leak
    │   oss_insight.sql    				# SQL statement used in ossinsight.io
    │   Cadidate_tools.md    			# Document of candidate tools 
    │   CWE-id.md    					# memory leak related CWE-id 
    │   repo.txt    					# List of target repositories
    │   license.txt    					# MIT License file
    └─── Scripts						# Dir of our automated pipeline scripts
        	│   requirement.txt			# Python requirement file
            └─── analyze				# Scripts of auto executing detection tools
            └─── assets					# Assets including web-config and regex
            └─── downloader				# Scripts to download GitHub files
            └─── files					# External files
            		└─── analyzers		# Put analyzers here
            		└─── memleak_files	# Memory leak files will be downloaded here
            		└─── pics			# Result pictures will be generated here
            └─── statistics				# Scripts to generate statistics result
            └─── utils					# Utils for pipeline
````

