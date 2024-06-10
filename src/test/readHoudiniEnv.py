import os

# Set environment variables
os.environ['OTLS'] = "tools/houdini/otls"
os.environ['ICONS'] = "$OTLS/icons"

# Function to expand environment variables recursively
def expand_env_variables(value):
    return os.path.expandvars(value)

# Expand ICONS variable
expanded_icons = expand_env_variables(os.environ['ICONS'])

# Print the expanded value
print("Expanded ICONS:", expanded_icons)