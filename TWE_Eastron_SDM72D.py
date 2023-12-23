# VenusOS module for support of Eastron SDM72D-Modbus v2
# might work also with other Eastron devices > Product code on 0xfc02 (type u16b) to be added into models overview
# 
# Community contribution by Thomas Weichenberger
# Version 1.4 - 2022-02-13 - Victron VRM Portal statistics fixed by christian1980nrw 2023-04-18
# Updated version 2023-12-24 by Daniel Genrich: Add dbus-modbus-client v1.47 support (Firmware 3.20~35 Beta)
#
# Thanks to Victron for their open platform and especially for the support of Matthijs Vader
# For any usage a donation to seashepherd.org with an amount of 5 USD/EUR/GBP or equivalent is expected

# Tested with the following equipment:
# Smartmeter: SDM72DM-V2 (MID 2023) https://amzn.to/3JQkkja (currently only costs 62.50 EUR).
# It should also work with the cheaper https://amzn.to/3KkEROl (without MID certification, currently 54 EUR).
# RS485 USB adapter: https://amzn.to/3Jw5lL8 (the version with FT232RL chip, currently 18.50 EUR)
# First set your meter to 19200 baud (see manual). The default meter password is 1000. 
# Second place this file TWE_Eastron_SDM72D.py together with TWE_Eastron_device.py in /opt/victronenergy/.
# Add in file /opt/victronenergy/dbus-modbus-client/dbus-modbus-client.py below the expression "import carlo_gavazzi "
#    for Eastron meters SDM72D the expression: import TWE_Eastron_SDM72D
# See installation notes at https://community.victronenergy.com/idea/114716/power-meter-lib-for-modbus-rtu-based-meters-from-a.html

import logging
import TWE_Eastron_device as device
import probe
import time

from register import *

log = logging.getLogger()

class Reg_f32b(Reg_num):
    coding = ('>f', '>2H')
    count = 2
    rtype = float
        
nr_phases = [ 0, 1, 3, 3 ]

phase_configs = [
    'undefined',
    '1P',
    '3P.1',
    '3P.n',
]

class Eastron_SDM72Dv2(device.CustomName, device.EnergyMeter):
    productid = 0xb023 # Eastron id assigned by Victron Support
    productname = 'Eastron SDM72Dv2'
    min_timeout = 0.5

    def phase_regs(self, n):
        s = 0x0002 * (n - 1)
        return [
            Reg_f32b(0x0000 + s, '/Ac/L%d/Voltage' % n,        1, '%.1f V'),
            Reg_f32b(0x0006 + s, '/Ac/L%d/Current' % n,        1, '%.1f A'),
            Reg_f32b(0x000c + s, '/Ac/L%d/Power' % n,          1, '%.1f W'),  
        ]

    def device_init(self):
        self.info_regs = [
            Reg_u16(0xfc02, '/HardwareVersion'),
            Reg_u16(0xfc03, '/FirmwareVersion'),
            Reg_f32b(0x000a, '/PhaseConfig', text=phase_configs, write=(0, 3)),
            Reg_u32b(0x0014, '/Serial'),
        ]

        self.read_info()

        phases = nr_phases[int(self.info['/PhaseConfig'])]

# Register list for the SDM72 V2 see https://github.com/reaper7/SDM_Energy_Meter/blob/master/SDM.h#L104

        regs = [
            Reg_f32b(0x0034, '/Ac/Power',          1, '%.1f W'),
            Reg_f32b(0x0030, '/Ac/Current',        1, '%.1f A'),   
            Reg_f32b(0x0046, '/Ac/Frequency',      1, '%.1f Hz'),
            
# Option 1: Include phase balancing energy (additional grid import and export at the VRM portal statistics especially at 1 phase systems)           
#            Reg_f32b(0x0048, '/Ac/Energy/Forward', 1, '%.1f kWh'),
#            Reg_f32b(0x004a, '/Ac/Energy/Reverse', 1, '%.1f kWh'), 
#            Reg_f32b(0x0048, '/Ac/L1/Energy/Forward', 1, '%.1f kWh'),  # We dont have separate data for L2 and L3 at this meter
#            Reg_f32b(0x004a, '/Ac/L1/Energy/Reverse', 1, '%.1f kWh'),  # so we will use L1 only for VRM Portal statistics

# Option 2: Dont show phase balancing energy at VRM portal statistics (statistics may be minimally inaccurate with this option)           
             Reg_f32b(0x018C, '/Ac/Energy/Forward', 1, '%.1f kWh'),     # export minus import
             Reg_f32b(0x018C, '/Ac/Energy/Reverse', -1, '%.1f kWh'),    # export minus import (negative)
             Reg_f32b(0x018C, '/Ac/L1/Energy/Forward', 1, '%.1f kWh'),  # export minus import
             Reg_f32b(0x018C, '/Ac/L1/Energy/Reverse', -1, '%.1f kWh'), # export minus import (negative)
        ]

        for n in range(1, phases + 1):
            regs += self.phase_regs(n)

        self.data_regs = regs
        self.nr_phases = phases

    def get_ident(self):
        return 'cg_%s' % self.info['/Serial']

# identifier to be checked, if register identical on all SDM630 (only first 16 bytes in u16b of 32 bit register 0xfc02)
models = {
    137: {
        'model':    'SDM72DMv2',
        'handler':  Eastron_SDM72Dv2,
    },
    135: {
        'model':    'SDM72Dv2',
        'handler':  Eastron_SDM72Dv2,
    },
}

#TCP-IP LAN Access
#probe.add_handler(probe.ModelRegister(0xfc02, models,
#                                      methods=['tcp'],
#                                      units=[1]))

#USB Access
probe.add_handler(probe.ModelRegister(Reg_u16(0xfc02), models, 
	          methods=['rtu'],
		  units=[1],
		  rates=[19200]))
