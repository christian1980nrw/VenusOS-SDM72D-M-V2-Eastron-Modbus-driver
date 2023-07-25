# VenusOS-SDM72D-M-V2-Eastron-Modbus-driver
Victron SDM72D-M-2 MID Modbus ESS driver
code for Victron Energy Venus OS v2.93. / also tested on v3.00~22

The default meter password is 1000 if anyone else needs it.

Tested with the following equipment:
Smartmeter: SDM72DM-V2 (MID 2023) https://amzn.to/3JQkkja (currently only costs 62.50 EUR).

It should also work with the cheaper https://amzn.to/3KkEROl (without MID certification, currently 54 EUR).

RS485 USB adapter: https://amzn.to/3Jw5lL8 (the version with FT232RL chip, currently 18.50 EUR)

First set your meter to 19200 baud (see manual). The default meter password is 1000. 

Second place this file TWE_Eastron_SDM72D.py together with TWE_Eastron_device.py in /opt/victronenergy/.

Add in file /opt/victronenergy/dbus-modbus-client/dbus-modbus-client.py below the expression "import carlo_gavazzi "

for Eastron meters SDM72D the expression: import TWE_Eastron_SDM72D

Next delete everything in folder /opt/victronenergy/dbus-modbus-client/__pycache__ and reboot.

See installation notes at https://community.victronenergy.com/idea/114716/power-meter-lib-for-modbus-rtu-based-meters-from-a.html
