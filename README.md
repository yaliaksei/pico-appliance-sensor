# Appliance sensor based on Raspberry Pico W
## Idea
This solution allows to modernize washing or drying machine and let them inform about end of cycle
so user can pick up wear and start a next cycle if necessary without delays.

## Hardware design
Raspberry Pico W
3 female-to-female wires
Vibration sensor

## Software design
Python script runs and tracks the number of vibrations within monitoring window. If vibrations exceed 
threshold script sends notification about start or end program depending on flags.

## Further improvements
There is an idea to add a web server on the Pico W so user can get information
about the current status like cycle on/off, number of vibration events detected, etc.
Additionally, user will be able to control sensitivity of the device. 