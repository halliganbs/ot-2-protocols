# TRIPLE WASH FOR n number of plates

def get_values(*names):
    import json
    _all_values = json.loads("""{"m300_mount":"left","plates":3,"new_tip":"never","disp_speed":35,"asp_height":0.5}""")
    return [_all_values[n] for n in names]


metadata = {
    'protocolName': 'Staining Cell-Based Assay Plates',
    'author': 'Sakib <sakib.hossain@opentrons.com>',
    'description': 'Custom Protocol Request',
    'apiLevel': '2.9'
}

def run(ctx):
    
    [m300_mount, plates, new_tip, disp_speed,
        asp_height] = get_values(  # noqa: F821
        "m300_mount", "plates", "new_tip", "disp_speed",
        "asp_height")

    cols = 24

    # Load Labware
    plates = [ctx.load_labware(
              'perkinelmer_384_wellplate_145ul', slot)
              for slot in range(1, plates+1)]
    pbs_reservoir = ctx.load_labware('nest_1_reservoir_195ml', 8)
    waste_reservoir = ctx.load_labware('nest_1_reservoir_195ml', 9)
    tipracks = [ctx.load_labware('opentrons_96_tiprack_300ul',
                                 slot) for slot in range(10, 12)]

    # Load Pipette
    m300 = ctx.load_instrument('p300_multi_gen2', m300_mount,
                               tip_racks=tipracks)

    # Single Well Reagents
    # primary_antibody = reagent_reservoir.rows()[0][4]
    # secondary_antibody = reagent_reservoir.rows()[0][5]

    # Wells
    # pbs_wells = pbs_reservoir.rows()[0] + reagent_reservoir.rows()[0][:6]

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
    wasteTrack = VolTracker(waste_reservoir, 194000, 'multi', 'waste',
                            msg='Empty Waste Reservoir', start=0, end=1)
    pbsTrack = VolTracker(pbs_reservoir, 194000, 'multi', start=0, end=1,
                          msg='Replenish PBS')
    # Protocol Steps

    # Add/Remove PBS
    m300.flow_rate.dispense = disp_speed

    def add_remove_pbs(wells, vol):
        ctx.comment('Adding and Removing PBS')
        if not m300.has_tip:
            m300.pick_up_tip()
        for well in wells:
            m300.aspirate(vol, pbsTrack.tracker(vol))
            m300.dispense(vol, well)
            m300.aspirate(vol, well.bottom(asp_height))
            m300.dispense(vol, wasteTrack.tracker(vol))
        # m300.drop_tip()

    for i, plate in enumerate(plates, 1):
        ctx.comment(f"Starting Plate {i} wash 1")
        dest_wells = [plate.rows()[i][col] for col in range(cols) for i in
                      range(2)][:cols*2]
        
        add_remove_pbs(dest_wells, 50)
        
    for i, plate in enumerate(plates, 1):
        ctx.comment(f"Starting Plate {i} wash 2")
        dest_wells = [plate.rows()[i][col] for col in range(cols) for i in
                      range(2)][:cols*2]
        # m300.drop_tip()
        # Add/Remove PBS (2-3)
        add_remove_pbs(dest_wells, 50)

    for i, plate in enumerate(plates, 1):
        ctx.comment(f"Starting Plate {i} wash 3")
        dest_wells = [plate.rows()[i][col] for col in range(cols) for i in
                      range(2)][:cols*2]
        # m300.drop_tip()
        # Add/Remove PBS (2-3)
        add_remove_pbs(dest_wells, 50)

    m300.drop_tip()
    m300.home()

