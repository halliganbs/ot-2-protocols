def get_values(*names):
    import json
    _all_values = json.loads("""{"m300_mount":"left","plates":1,"new_tip":"never","disp_speed":35,"asp_height":0.5}""")
    return [_all_values[n] for n in names]


metadata = {
    'protocolName': 'Compound Tube Transfer',
    'author': 'halliganbs <bhalliga@umich.edu>',
    'description': 'Transfer compounds from 96 well tube racks to 384 well plate',
    'apiLevel': '2.9'
}


def run(ctx):

    [m300_mount, plates, new_tip, disp_speed,
        asp_height] = get_values(  # noqa: F821
        "m300_mount", "plates", "new_tip", "disp_speed",
        "asp_height")

    cols = 24

    # Load Labware
    plate = ctx.load_labware('perkinelmer_384_wellplate_145ul', 1)

    t1 = ctx.load_labware('thermoscientific_96_aluminumblock_1000ul', 2)
    t2 = ctx.load_labware('thermoscientific_96_aluminumblock_1000ul', 3)
    t3 = ctx.load_labware('thermoscientific_96_aluminumblock_1000ul', 4)
    t4 = ctx.load_labware('thermoscientific_96_aluminumblock_1000ul', 5)

    tipracks = [ctx.load_labware('opentrons_96_tiprack_300ul',
                                 slot) for slot in range(6, 12)]

    # Load Pipette
    m300 = ctx.load_instrument('p300_multi_gen2', m300_mount,
                               tip_racks=tipracks)



    # Volume Tracking
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

    # Volume Trackers for Multi-well Reagents
    # wasteTrack = VolTracker(waste_reservoir, 194000, 'multi', 'waste',
    #                         msg='Empty Waste Reservoir', start=0, end=1)
    # pbsTrack = VolTracker(pbs_reservoir, 194000, 'multi', start=0, end=1,
    #                       msg='Replenish PBS')
    # pfaTrack = VolTracker(reagent_reservoir, 14900, 'multi',
    #                       start=0, end=4, msg='Replenish 4% PFA')
    # permTrack = VolTracker(reagent_reservoir, 14900,
    #                        'multi', start=4, end=8,
    #                        msg='Replenish Perm Buffer')
    # primaryAntiTrack = VolTracker(reagent_reservoir, 14900,
    #                               'multi', start=8, end=10,
    #                               msg='Replenish Primary Antibody')
    # secondaryAntiTrack = VolTracker(reagent_reservoir, 14900,
    #                                 'multi', start=10, end=12,
    #                                 msg='Replenish Secondary Antibody')

    # t1Track = VolTracker(t1, 900, pip_type='multi',start=0, end=4, msg='tube rack 1 out')
    t1_wells = [plate.rows()[0][col] for col in range(2,12)][:cols*2]
    t2_wells = [plate.rows()[1][col] for col in range(2,12)][:cols*2]
    t3_wells = [plate.rows()[0][col] for col in range(12,22)][:cols*2]
    t4_wells = [plate.rows()[1][col] for col in range(12,22)][:cols*2]

    # Protocol Steps

    for s, d in zip([t1.rows()[0][col] for col in range(1,11)], t1_wells):
       m300.transfer(40, s, d, touch_tip=True, new_tip='always')

    for s, d in zip([t2.rows()[0][col] for col in range(1,11)], t2_wells):
        m300.transfer(40, s, d, touch_tip=True, new_tip='always')
    
    for s, d in zip([t3.rows()[0][col] for col in range(1,11)], t3_wells):
        m300.transfer(40, s, d, touch_tip=True, new_tip='always')
    
    for s, d in zip([t4.rows()[0][col] for col in range(1,11)], t4_wells):
        m300.transfer(40, s, d, touch_tip=True, new_tip='always')