def get_values(*names):
    import json
    _all_values = json.loads("""{"plates":"4","pipette_type":"p300_multi","tip_type":0,"trough_type":"nest_12_reservoir_15ml","plate_type":"perkinelmer_384_wellplate_145ul","dilution_factor":2,"num_of_dilutions":10,"total_mixing_volume":5,"tip_use_strategy":"never"}""")
    return [_all_values[n] for n in names]


metadata = {
    'protocolName': 'Customizable Serial Dilution',
    'author': 'Opentrons <protocols@opentrons.com>',
    'source': 'Protocol Library',
    'apiLevel': '2.5'
    }


def run(protocol_context):
    [plates, pipette_type, tip_type, trough_type, plate_type,
     dilution_factor, num_of_dilutions, total_mixing_volume,
        tip_use_strategy] = get_values(  # noqa: F821
            'plates','pipette_type', 'tip_type', 'trough_type', 'plate_type',
            'dilution_factor', 'num_of_dilutions',
            'total_mixing_volume', 'tip_use_strategy'
        )

    # labware
    trough = protocol_context.load_labware(
        trough_type, '2')
    liquid_trash = trough.wells()[-1]
    # changed for 384 well plates
    # plate = protocol_context.load_labware(
    #     plate_type, '3')
    plates = [protocol_context.load_labware(
              'perkinelmer_384_wellplate_145ul', slot)
              for slot in range(1, plates+1)]
    # REPLACED BY 5520f0 tips
    # if 'p20' in pipette_type:
    #     tip_name = 'opentrons_96_filtertiprack_20ul' if tip_type \
    #         else 'opentrons_96_tiprack_20ul'
    # else:
    #     tip_name = 'opentrons_96_filtertiprack_200ul' if tip_type \
    #         else 'opentrons_96_tiprack_300ul'
    # tiprack = [
    #     protocol_context.load_labware(tip_name, slot)
    #     for slot in ['1', '4']
    # ]

    tiprack = [protocol_context.load_labware('opentrons_96_tiprack_300ul',
                                 slot) for slot in ['1', '4']]

    pipette = protocol_context.load_instrument(
        pipette_type, mount='left', tip_racks=tiprack)

    transfer_volume = total_mixing_volume/dilution_factor
    diluent_volume = total_mixing_volume - transfer_volume

    if 'multi' in pipette_type:

        # Distribute diluent across the plate to the the number of samples
        # And add diluent to one column after the number of samples for a blank
        pipette.transfer(
            diluent_volume,
            trough.wells()[0],
            plate.rows()[0][1:1+num_of_dilutions]
        )

        # Dilution of samples across the 96-well flat bottom plate
        if tip_use_strategy == 'never':
            pipette.pick_up_tip()

        for s, d in zip(
                plate.rows()[0][:num_of_dilutions],
                plate.rows()[0][1:1+num_of_dilutions]
        ):
            pipette.transfer(
                transfer_volume,
                s,
                d,
                mix_after=(3, total_mixing_volume/2),
                new_tip=tip_use_strategy
            )

        # Remove transfer volume from the last column of the dilution
        pipette.transfer(
            transfer_volume,
            plate.rows()[0][num_of_dilutions],
            liquid_trash,
            new_tip=tip_use_strategy,
            blow_out=True
        )

        if tip_use_strategy == 'never':
            pipette.drop_tip()

    else:
        # Distribute diluent across the plate to the the number of samples
        # And add diluent to one column after the number of samples for a blank
        for col in plate.columns()[1:1+num_of_dilutions]:
            pipette.distribute(
                diluent_volume, trough.wells()[0], [well for well in col])

        for row in plate.rows():
            if tip_use_strategy == 'never':
                pipette.pick_up_tip()

            for s, d in zip(row[:num_of_dilutions], row[1:1+num_of_dilutions]):

                pipette.transfer(
                    transfer_volume,
                    s,
                    d,
                    mix_after=(3, total_mixing_volume/2),
                    new_tip=tip_use_strategy
                )

                pipette.transfer(
                    transfer_volume,
                    row[num_of_dilutions],
                    liquid_trash,
                    new_tip=tip_use_strategy,
                    blow_out=True
                )

            if tip_use_strategy == 'never':
                pipette.drop_tip()
