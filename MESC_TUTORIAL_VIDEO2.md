# MESC Firmware and documentation

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

