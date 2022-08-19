import pyvisa

try:
    # Try to reference the Visa library dll
    rm = pyvisa.ResourceManager("C:\\Windows\\System32\\visa32.dll")
except:
    # If it fails, try to reference the Visa library dll in the default path
    rm = pyvisa.ResourceManager()
print(rm.list_resources())
