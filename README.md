# OT-2 Protocols

Opentrons OT-2 Protocols for Sextonlabs

## Custom Labware

Located in `custom_labware` folder

Contents

- Perkin Elmer 384 Well Plate
- Thermo Scientific 96 Matrix Tube Rack

## Protocols

### 5520f0_master

- Master fix and stain protocol
- 3 Perkin Elmer 384 well plates
- PBS, PFA, 2 Antibody Stains
- Asperiate speed set to 35
- Approx running time: 6-7 hours

### fix

- Dedicated fix steps in a protocol
- removes 46 uL of liquid first
- 2 pbs washes
- 15 minute wait after pfa
- adds 50 uL pbs at end


### stain

- Dedicated stain protocol
- first removes 45 uL of liquid from each well
- adds 25 uL of primary stain
- 60 minute wait
- 2 pbs washes
- addes 25 uL of secondary stain
- 30 minute wait
- 2 pbs washes
- add final 50 uL of pbs