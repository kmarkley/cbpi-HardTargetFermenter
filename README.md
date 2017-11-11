# Hard Target Fermenter Controller

Basic hysteresis controller with two additional features:

1. Auto mode is always on.  If it gets turned off, a background task will turn it back on.

2. Target temp is set in hardware settings.  If the target is changed, a background task will reset it to the original value.

Originally written to control the exhaust fan in a CraftBeerPi enclosure.  Provides thermostatic control of the fan immediately at startup and without the possibility of accidentally disabling it.  

Might also be good for a secondary storage fridge.
