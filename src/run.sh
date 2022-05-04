#! /bin/bash

echo -e "\e[1;31m 1. run periodic task \e[0m"
python3 main.py scheduler

echo -e "\e[1;31m 2. server start \e[0m"
python3 main.py scheduler

echo -e "\e[1;31m 3. finished! \e[0m"
