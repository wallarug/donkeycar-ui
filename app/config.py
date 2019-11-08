import os
import sys

# Figure out where this config file lives
base_dir = os.path.dirname(os.path.abspath(__file__))

TEMPLATE_PATH = os.path.join(base_dir, "templates")
STATIC_PATH = os.path.join(base_dir, "static")

# Network Settings
port = 8888

