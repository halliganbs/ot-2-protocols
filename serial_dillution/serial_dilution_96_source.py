def get_values(*names):
    import json
    _all_values = json.loads("""{"m300_mount":"left","plates":2,
                    "new_tip":"never","disp_speed":35,"asp_height":0.5}""")
    return [_all_values[n] for n in names]

metadata = {
    'protocolName': 'Serial Dilution of 384 plates',
    'author': 'bshalligan <bhalliga@med.umich.edu>',
    'description': 'Serial dilution of 384 well plates with 96 well source',
    'apiLevel': '2.9'
}

def run(ctx):

    [m300_mount, plates, new_tip, disp_speed,
        asp_height] = get_values(  # noqa: F821
        "m300_mount", "plates", "new_tip", "disp_speed",
        "asp_height")

    cols = 24

    # Deck setup
    plates = [ctx.load_labware(
              'perkinelmer_384_wellplate_145ul', slot)
              for slot in ['5','6']]
    
    source = ctx.load_labware('96_well', '2')
    waste = ctx.load_labware('nest_1_reservoir_195ml', '3')
    tipracks = [ctx.load_labware('opentrons_96_tiprack_300ul', 
                                        slot) for slot in ['1','4']]

    # pipette
    m300 = ctx.load_instrument('p300_multi_gen2', m300_mount,
                                 tip_racks=tipracks)


    # Volume Tracker
    class VolTracker:
        def __init__(self, labware, well_vol, pip_type='single',
                     mode='reagent', start=0, end=12, msg='Reset Labware'):
            try:
                self.labware_wells = dict.fromkeys(
                    labware.wells()[start:end], 0)
            except Exception:
                self.labware_wells = dict.fromkeys(
                    labware, 0)
            self.labware_wells_backup = self.labware_wells.copy()
            self.well_vol = well_vol
            self.pip_type = pip_type
            self.mode = mode
            self.start = start
            self.end = end
            self.msg = msg

        def tracker(self, vol):
            '''tracker() will track how much liquid
            was used up per well. If the volume of
            a given well is greater than self.well_vol
            it will remove it from the dictionary and iterate
            to the next well which will act as the reservoir.'''
            well = next(iter(self.labware_wells))
            if self.labware_wells[well] + vol >= self.well_vol:
                del self.labware_wells[well]
                if len(self.labware_wells) < 1:
                    ctx.pause(self.msg)
                    self.labware_wells = self.labware_wells_backup.copy()
                well = next(iter(self.labware_wells))
            if self.pip_type == 'multi':
                self.labware_wells[well] = self.labware_wells[well] + vol*8
            elif self.pip_type == 'single':
                self.labware_wells[well] = self.labware_wells[well] + vol
            if self.mode == 'waste':
                ctx.comment(f'''{well}: {int(self.labware_wells[well])} uL of
                            total waste''')
            else:
                ctx.comment(f'''{int(self.labware_wells[well])} uL of liquid
                            used from {well}''')
            return well

