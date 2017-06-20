# 02443-simulation


## Dependencies

`pip install numpy`

`pip install pygame`

`pip install sortedcontainers`

## File description
`animation.py`: Takes care of the animation of the cars

`main.py`: mainScript that lets user control spawn rate and other parameters

`simulation.py`: Simulater that has definitions for time step, and spawning vehicles

`vehicle.py`: The vehicle and human vehicle with attached decision propabilities and update rules

`vehicle_container.py`: The vehicle as an object, with dimensions and methods for getting relevant neighbors

`visualisation.py`: pygame base file for setting up the board and doing events

`viz.py`: Old visualisation file that has logic within the visualisation itself, look at it for inspiration, uses pygames sprites
