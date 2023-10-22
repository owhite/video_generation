# MESC Firmware and documentation
## see this vidieo: https://www.youtube.com/watch?v=nHqouHzY8-Y

Downloading MESC:
+ The latest build is https://github.com/davidmolony/MESC_Firmware
+ The branch for this video is BLAH_BLAH_BLAH
+ There are lots of git tools for pulling branches
+ Or you can do it on the command line with:
```
$ git clone --branch BLAH_BLAH_BLAH https://github.com/davidmolony/MESC_Firmware.git
```

Advice for loading MESC into STM32CubeIDE:
+ Loading STM32CubeIDE can be really annoying
+ The easiest way is create a whole new workspace
+ Open STM32CubeIDE, when it asks if you want to open a workspace, hit browse
+ Create a new workspace folder, hit open
+ When the IDE starts, use the menu
+ Window->Show view->Project explorer
+ Hopefully that shows window that says "Import projects"
+ Then find "Existing Projects into Workspace"
+ Link that to the top level folder for MESC project you downloaded

If all this gets loaded, these are the three files you have to edit. Note that sometimes these are in a slightly different directory structure in STM32CubeIDE. The files:
+ MESC_Common/Inc/MESC_MOTOR_DEFAULTS.h
+ MESC_F405RG/Core/Inc/MP2_V0_1.h
+ MESC_F405RG/Core/Inc/MESC_F405.h

## Editing MESC_MOTOR_DEFAULTS.h: 
These are variables that need to be created for your motor, these are the variables I'm going to use for a TP128:
```
#elif defined(TP128)
#define MAX_MOTOR_PHASE_CURRENT 350.0f //350A seems like a reasonable upper limit for these
#define DEFAULT_MOTOR_POWER 12000.0f   //Go on, change this to 15000
#define DEFAULT_FLUX_LINKAGE 0.0167f   //Set this to the motor linkage in wB
#define DEFAULT_MOTOR_Ld 0.000032f     //Henries
#define DEFAULT_MOTOR_Lq 0.000046f     //Henries
#define DEFAULT_MOTOR_R 0.0080f        //Ohms
#define DEFAULT_MOTOR_PP 5
```

A document to find motor parameters can be found [here](https://github.com/badgineer/MP2-ESC/blob/main/docs/MOTOR_PARAM.md). A video showing parameter generation is [here](https://www.youtube.com/watch?v=9YggapDcg0M). 

## MESC_F405RG/Core/Inc/MESC_F405.h
Open MESC_F405.h and look at this code block:
```
#include "MP2_V0_1.h"
//#include "CL700_V0_3.h"
//#include "INDI-600.h"
//#include "MX_FOC_IMS.h"
//#include "MX_FOC_GaN.h"
//#include "GIGAVESC.h"
```
Notice that MP2_V0_1.h is uncommented, and out all the other potential header files are comment out. 

## MESC_F405RG/Core/Inc/MP2_V0_1.h

Remember we made a configuration for your motor? Make sure the name of that section is in this define

```
#define YOUR_MOTOR_NAME // has to be consistent with MESC_MOTOR_DEFAULTS.h
```

In this case we'll use: 
```
#define TP128 
```

Next move to this code block in the same file:
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

- ABS_MAX_PHASE_CURRENT: The MP2 will not exceed this phase current
- ABS_MAX_BUS_VOLTAGE: if exceeded by VBat, MP2 throws an error 
- ABS_MIN_BUS_VOLTAGE: if VBat drops below, MP2 throws an error 
- MAX_IQ_REQUEST 200.0f: set to half of ABS_MAX_PHASE_CURRENT
- R_VBUS_BOTTOM and TOP refer to the voltage divider that measures VBat, the values shown are because resistors on the board are 150k, and 3.3k. 
- Obviously there are many other values in these files -- **you do not need to change any of them**

Now try poking the hammer icon which will launch a compile.

Once your compile works try connecting the STLINK V2 as showning in the video, and see if you can flash the firmware on to your pill. 

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
##########
This is a tutorial to flash MESC firmware to a MP2 electronic speed controller. Before I start I'd like to thank my friends who have done most of the work with developing this firmware and ESC. 

We are going to break this up into two videos. The first video is a minimal build needed to compile MESC code to run on an MP2. The steps will include:

Connecting your MP2 to a ST-LINK device
Loading MESC into the STM32CubeIDE
Configuring the code to work for your motor
Flashing the code

The second video will include:
Starting the STMCube debugger
Viewing variables coming from the MP2
Using the MP2 terminal
Spinning the motor

The video will NOT cover building an MP2, determining your motor parameters, or provide a deep discussion on how MESC firmware operates

Video 1

This is a partial list of what you need. You'll need to install the STM32Cube IDE. You'll need a physical device called an STLinks V2 which is very inexpensive. You'll need an STM32 pill. There are two pills to choose from,

STM32F411 BlackPill and the STM32F405 open source pill. 

This video is just a guide. It's not a step-by-step tutorial. This is because MESC is likely to change,
the STM32CubeIDe interface is likely to change. Things vary depending on what operating system you're using
and the pills are different

CONNECTING THE ST-LINK
Let's get started. The first thing youre going to do is connect your STM32 PILL to an ST-LINK device. ST-LINK are available from lots of different sources. There are many tutorials for using them to flash a pill them. The idea here is, the ST-LINK device to a USB cord, your USB is connected to your computer. Then wires to go from the ST-LINK over to the pill. There's only four wires, and they are usually labeled with these names. Once that's connected, you can flash the MESC code. 

LOADING MESC INTO STMCUBE
Let's first make a local copy of MESC from the GitHub site. This is done by starting with a search, going to the site and downloading a zip file. That's goes to my download folder and in my case, it gets uncompressed. Importing code into an STMCube project can be quite frustrating. Let's try starting from a completely new workspace. Open STMCube, go to top level folder, creating a new folder, open that, and launch. 

Hopefully STMCube will show import project, and you can use to this wizard import an existing project. Find the folder, hit Next, you'll can see lots of MESC folders here. Hit Open and if everything's working properly, the ImportProjects wizard will show you a bunch of different folders that it's selected for import into this project. Hit Finish and here we are. 

CONFIGURING THE CODE TO WORK FOR YOUR MOTOR

This is a relatively complicated task. But the first thing you should know is we are documenting every change that is shown in this video. Well make a separate github branch with this document and for you to use as a cheat sheet. You dont have to scramble to make all these changes while watching the video.

The following is the set of files to edit for the MP2 configuration:

MESC_Common/Inc/MESC_MOTOR_DEFAULTS.h
MESC_F405RG/Core/Inc/MP2_V0_1.h
MESC_F405RG/Core/Inc/MESC_F405.h

Notice that for the first file the include directory is coming from MESC_Common, the other two files are found in MESC_F405RG. Let's start with: 

LET'S TAKE A QUICK LOOK AT THE PROJECT EXPLORER

MESC_Common/Inc/MESC_MOTOR_DEFAULTS.h

MESC motor defaults may require the most work up front. Take a look at this code block, it is responsible for the flux linkage, motor inductance (called "LQ" and "LD") and motor resistance, pole pairs, phase current and power. There is a written tutorial for finding these numbers, for now we are going to skip over how these values are determined. I have a big hub motor made QS called a QS205, and I show you the lines of code needed for that motor. 

MESC_F405RG/Core/Inc/MP2_V0_1.h

Next let's look at the MP2_V0_1. This file contains a lot of parameters important for the MP2 board. 
The following is the variables that you need to touch in this file:

#define ABS_MAX_PHASE_CURRENT 400.0f 
#define ABS_MAX_BUS_VOLTAGE 50.0f
#define ABS_MIN_BUS_VOLTAGE 38.0f
#define MAX_IQ_REQUEST 200.0f 
#define R_VBUS_BOTTOM 3300.0f 
#define R_VBUS_TOP 100000.0f

ABS_MAX_PHASE_CURRENT provide user control of the total amount of amps used for each phase of the controller. 
ABS_MAX_BUS_VOLTAGE and ABS_MIN_BUS_VOLTAGE should be relatively obvious.

MAX_IQ_REQUEST refers to how much the user can crank the throttle and request the controller to deliver amps. Set this amount to half of what you used in ABS_MAX_PHASE_CURRENT

R_VBUS_BOTTOM and R_VBUS_TOP refer to values for resistors that are used as voltage dividers to measure battery voltage. These may vary between MP2 boards, but in my case they are set to these values

Finally take a look to MESC_F405.h

We are going to uncomment:

#include "MP2_V0_1.h"

so this include is used. Be sure to comment out the other header files

there's nothing else to change, but let me also call attention to these two values

#define  ADC1MIN 1200
#define  ADC1MAX 2700

My throttle is connected to ADC1, and this sets the lower and upper limits that will make the motor turn. We'll return to that in the next video. 

FLASH THE MESC CODE

I'm going to focus on using the F405 pill for now, so what I'm going to do is click on one of these files in this folder. Hit the build icon. That compilation is going to run and you can see it in this window. 

To flash, select the debug configuration file, and then press the debug icon. It loads and there we are. You have flashed your STM32 device. 

Before we proceed, i want to mention that often, if you look at tutorials on using STMCube IDE, it walks you through the process of configuring the CPU. You don't need to do that here. If you've imported the MESC project into STMcube, the architecture configuration are already handled to, for now dont worry about clock speeds or pin settings.

So again:
MESC project in STM32CubeIDE code handles:

CPU configuration, All the code

It's not like other tutorials where you have to deal with pin settings, timers

There are MANY ways to perform a flash
Platformio, openOCD, make, st-link utility
Sometimes you can unbrick ESCs

Flashing does NOT instantly spin a motor
In the next tutorial we'll use the debugger to make sure everything is working and eventually spin the motor 


