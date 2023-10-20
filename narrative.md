A Consortium Facilitation, Coordination, and Analysis Center for the HVP


This is a tutorial to flash MESC firmware to a MP2 electronic speed controller

Before I start I'd like to thank my friends who have done most of the work with developing this firmware and ESC. 

We are going to break this up into two videos. The first video is a minimal build needed to compile MESC code to run on an MP2. The steps will include:

## Connecting your MP2 to a ST-LINK device
+ Loading MESC into the STM32CubeIDE
+ Configuring the code to work for your motor
+ Connect your pill
+ Flashing the code

The second video will include:
Starting the STMCube debugger
Viewing variables coming from the MP2
Using the MP2 terminal
Spinning the motor

The video will NOT cover 
building an MP2
determining your motor parameters
a deep discussion on how MESC firmware operates

## Video 

This is a partial list of what you need. 
Install the STM32Cube IDE, you'll need a physical device called an STLinks V2 which is very inexpensive. You'll need an STM32 pill. There are two pills to choose from:

STM32F411 BlackPill and the 
STM32F405 open source pill. A link is given for the open source pill. 

This video is just a guide. I avoid step-by-step tutorial because the MESC code is always changing, the STM32CubeIDe interface is likely to change. Things vary depending on what operating system you're using and the pills are slightly different

A COUPLE OTHER ITEMS BEFORE STARTING
MESC project in STM32CubeIDE code imports:
CPU configuration
All the code
Don’t confuse with other tutorials

There are MANY ways to perform a flash
Platformio, openOCD, make, st-link utility

But the easiest way to perform the compile is with the STM 32 CUBE IDE

Flashing will NOT instantly spin a motor, in fact I recommend disconnecting the pill altogether for your first flash. 

LOADING MESC INTO STMCUBE
To get started with loading mesc
lets create a local copy of MESC from the GitHub site. 
There's a link in my comments section that takes you to github
go there and download a zip file. 
in my case, it downloads and gets uncompressed. 
Importing code into an STMCube project can be quite frustrating. 
A safe way is to start a new workspace. 

Open STMCube, go to top level folder, create a new workspace folder, open that, and launch. 

Hopefully STMCube will show import project
you can use to this wizard import an existing project
Find your uncompressed the folder, hit Next, 
Now you'll lots of MESC folders here. 
Hit Open and if everything's working properly, the Import Projects wizard will show you a bunch of different folders
Hit Finish and here we are
You can see all the MESC code in the project explorer
Hit save

==================================================
CONFIGURE THE MESC CODE TO RUN FOR A MOTOR
This is a relatively complicated task. 
keep in mind we will create a separate gihub branch with the exact code changes shown here
will include a document to use as a cheat sheet. 

The following is the set of files you need to edit for a basic MP2 configuration:

MESC_Common/Inc/MESC_MOTOR_DEFAULTS.h
MESC_F405RG/Core/Inc/MP2_V0_1.h
MESC_F405RG/Core/Inc/MESC_F405.h

Notice that for the first file the include directory is coming from MESC_Common, 
the other two files are found in MESC_F405RG. 

LET'S TAKE A look MESC_MOTOR_DEFAULTS.h in the project explorer

As I mentioned, this video will not show you how to physically  and electronically determine your motor parameters

But there is a document tutorial for finding these numbers in the description section of this video

For now we are going assume you already know these numbers and want to plug them in

This is an example code block that needs to be filled in for your motor
it has values for flux linkage, 
motor inductance (called "LQ" and "LD") and motor resistance, 
pole pairs, phase current and power. 

For example, I have new motor, the toppower 128. 
here are the variables I used for the TP128

MESC_F405RG/Core/Inc/MP2_V0_1.h

Next let's look at the MP2_V0_1. This file is used by MESC for MP2 board. Note that MESC works for lots of other ESCs as well. 

But this is the list of variables that you need to touch in this file:

#define ABS_MAX_PHASE_CURRENT 400.0f 
#define ABS_MAX_BUS_VOLTAGE 50.0f
#define ABS_MIN_BUS_VOLTAGE 38.0f
#define MAX_IQ_REQUEST 200.0f 
#define R_VBUS_BOTTOM 3300.0f 
#define R_VBUS_TOP 100000.0f

ABS_MAX_PHASE_CURRENT control of the total amount of amps that can dumped into each phase of the controller. 
ABS_MAX_BUS_VOLTAGE and ABS_MIN_BUS_VOLTAGE are cutoff values for battery voltage coming into the controller

MAX_IQ_REQUEST refers to how much the user can crank the throttle and request the controller to deliver in amps. 

set this amount to half of what you used in ABS_MAX_PHASE_CURRENT

R_VBUS_BOTTOM and R_VBUS_TOP refer to values for resistors that are used as voltage dividers 
to measure PHASE voltage. 
Take a look at the section of the MP2 circuit that I'm talking about. 
These may vary between MP2 boards, but in my case because I have 100k and 3.3k resistors so I use these values

_Next let's take a look to MESC_F405.h_ 

We are going to uncomment:

#include "MP2_V0_1.h"

so the include that you just edited will be used here. 
Be sure to comment out the other header files
there's nothing else to change 
but, let me call attention to these two values

ADC1MIN and ADC1MAX

Your throttle is probably goign to be connected to ADC1 input
this sets the lower and upper limits associated with the throttle
We'll return to using these values in the next video. 

NOW WE WILL CONNECT THE ST-LINK to your computer and the pill
ST-LINKs are available from lots of different sources. 
There are many tutorials for using them to flash a pill
The idea here is, the ST-LINK device to a USB cord, your USB is connected to your computer. 
Then wires to go from the ST-LINK over to the pill. 
There's only four wires, and they are usually labeled with these names. 
Once that's connected, you can flash the MESC code. 
Bear in mind that you may want to restart the STM32 CUBE IDE after you have plugged in the STLINK

FLASH THE MESC CODE
My pill uses a F405, so let's go to this folder
If I click on one of these files it will know what architecture to compile. 
Hit the build icon. That compilation runs, you can see it in this window. 

Next we are going to flash the pill
Remember, if you are doing this for the first time do not connect the pill to the MP2.
To flash, select the debug configuration file, and then press the debug icon. 
It loads and there we are. You have flashed your STM32 device. 

In the next tutorial we'll use the debugger to make sure everything is working and eventually spin the motor 


