import RPi.GPIO as GPIO
import shlex
import time
import subprocess

command_line = "mopidy"
args = shlex.split(command_line)
p = subprocess.Popen(args)


