# MESC Firmware and documentation
## see this vidieo: https://youtu.be/oS0gFUgAbKI?si=wD3mVZEL_7NAHPBq

MESC_Common/Inc/MESC_MOTOR_DEFAULTS.h
Must set the following parameters that are specific to your motor

```
#if defined(YOUR_MOTOR_NAME)            //Create a new block name
#define MAX_MOTOR_PHASE_CURRENT 200.0f  // Amps, that's specific to this motor
#define DEFAULT_MOTOR_POWER 250.0f      // Watts, same
#define DEFAULT_FLUX_LINKAGE 0.0068f    // wB
#define DEFAULT_MOTOR_Ld 0.000020f      // Henries
#define DEFAULT_MOTOR_Lq 0.0000250f     // Henries
#define DEFAULT_MOTOR_R 0.011f          // Ohms
#define DEFAULT_MOTOR_PP 14             // Pole Pairs
```

Now, be sure to include this into: 
MESC_Firmware/MESC_F405RG/Core/Inc/MESC_F405.h
```
#include "MP2_V0_1.h"
```
also be sure to comment out all the other potential header files! 

MESC_Firmware/MESC_F405RG/Core/Inc/MP2_V0_1.h
```
#define YOUR_MOTOR_NAME // has to be consistent with MESC_MOTOR_DEFAULTS.h
```
These values are similar to motor defaults but are meant to be specific to the board you are using -- which is capable of running more than one motor. 
```
#define ABS_MAX_PHASE_CURRENT 400.0f 
#define ABS_MAX_BUS_VOLTAGE 80.0f
#define ABS_MIN_BUS_VOLTAGE 45.0f

#define MAX_IQ_REQUEST 200.0f 

//Phase and Vbus voltage sensors
#define R_VBUS_BOTTOM 3300.0f 
#define R_VBUS_TOP 150000.0f

```
## Notes
-ABS_MAX_PHASE_CURRENT: The MP2 will not exceed this phase current
-ABS_MAX_BUS_VOLTAGE: if exceeded by VBat, MP2 throws an error 
-ABS_MIN_BUS_VOLTAGE: if VBat drops below, MP2 throws an error 
-MAX_IQ_REQUEST 200.0f: set to half of ABS_MAX_PHASE_CURRENT
-R_VBUS_BOTTOM and TOP refer to the voltage divider that measures VBat, the values shown are because resistors on the board are 150k, and 3.3k. 
-Obviously there are many other values in these files -- **you do not need to change any of them**

## Using the STM32CubeIDE debugger
Useful values to track:
MESC_error
mtr[0]

mtr[0] can be expanded and a large set of variables are visible. 

## Variables discussed in the tutorial
MESC_error
mtr[0].m.Vmax
vars.adc1_MAX	

## Using the MESC terminal

Find a com port, setting up a terminal on STM32 architectures

https://www.carminenoviello.com/2015/03/02/how-to-use-stm32-nucleo-serial-port/
https://shawnhymel.com/1795/getting-started-with-stm32-nucleo-usb-virtual-com-port/
https://www.youtube.com/watch?v=92A98iEFmaA
https://www.youtube.com/watch?v=dEQwSl8mCFs

Commands used during the tutorial
Removed all previously saved values

```
save -d 
```

set 


Introductory commands

get, view all variables
```
get
```

get specific value
```
get motor_sensor
```

set, example:
```
set curr_max 30
```

adc1_min

stream data
```
status json
```

stop streaming 
```
status stop
```

change between sensorless and openloop
```
set motor_sensor 0
set motor_sensor 2
```
