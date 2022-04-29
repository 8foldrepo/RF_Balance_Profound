import pyvisa


def connect_oscilloscope():
    rm = pyvisa.ResourceManager()
    resources = rm.list_resources()
    inst = None
    for resource in resources:
        if '0x179B' in resource:
            inst = rm.open_resource(resource)
    return inst


# Script/example code for testing out hardware class
if __name__ == "__main__":
    inst = connect_oscilloscope()

    inst.write("WAV:FORM ASCII")

    for i in range(1000):
        inst.query("WAV:PRE?")
        inst.write("WAV:DATA?")
        print(inst.read())

    # may not be run if script is terminated early
    inst.close()
