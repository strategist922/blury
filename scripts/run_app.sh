#!/bin/bash

source activate blury
cd /app && pip install -U . 
blury $@
