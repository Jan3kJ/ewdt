# Project eWDT

An electric WDT tool to evenly distribute coffee grounds in the portafilter. This is a remix of Damian's eWDT ([original model](https://www.printables.com/model/591918-ewdt)).

## Overview
This project automates the WDT process using a continuous rotation servo, relay, and a momentary switch with an integrated LED, all powered by a lithium battery and controlled by a Waveshare RP2040-Plus running MicroPython.

## Hardware Components
- **RP2040-Plus by Waveshare**
- **5V Relay**
- **MT3608 Adjustable DC-DC Boost Converter**
- **Lithium Battery**
- **Momentary Switch with Integrated LED + 270Ω resistor**
- **EF90D 360° Continuous Rotation Servo**
- **Voltage Divider (2 × 100kΩ resistors for battery)**

## Schematic

<img src="img/schematic.svg" alt="Schematic" width="500"/>

## Pin Assignments
| Function                | RP2040 Pin | Notes                                      |
|-------------------------|------------|--------------------------------------------|
| Servo PWM               | GP15       | PWM output (50Hz)                          |
| Relay Control           | GP5        | Digital output                             |
| Internal LED            | GP25       | Digital output (onboard LED)               |
| Switch LED              | GP9        | Digital output (external button LED)       |
| Battery Voltage Sense   | GP26 (ADC0)| Analog input (via voltage divider)         |
| VSYS Sense         | GP29 (ADC3)| Analog input (via voltage divider from VSYS)|

## Wiring Diagram (Textual)
- **Servo**: VCC (5.7V from boost converter), GND, Signal to GP15
- **Relay**: VCC to 3V3, GND, IN to GP5
- **Switch**: One side to GND, other to relay (see schematic)
- **Switch LED**: Anode to GP9 (with resistor), cathode to GND
- **Battery Voltage Divider**: Connect between battery + and GND, center tap to GP26

## Functional Requirements (as implemented)
### Normal Operation
- When the system is powered (button press):
    - The relay is activated, powering the system.
    - The servo rotates continuously for 7 seconds (full speed, adjustable in code).
    - Both the internal LED (GP25) and the button LED (GP9) are ON during this time.
    - After 7 seconds, the servo stops, LEDs turn OFF.
    - If battery voltage drops below 3.7V, the LEDs blink rapidly for 2 seconds.
    - The relay is deactivated (cutting power) after operation.
- The relay always switches OFF after operation, cutting off battery power until the button is pressed again.

### Charging Mode
- When USB is connected (VSYS/ADC3 > 4.2V):
    - The battery charges.
    - The relay is switched ON.
    - The servo cannot be started; switch presses are ignored.
    - The LEDs blink slowly (3s interval) until battery voltage reaches 4.1V, then stay ON for 10s, then turn OFF.
    - When charging is complete or USB is disconnected, the relay is switched off.

## Firmware Details
- Firmware is written in MicroPython and located in `main.py`.
- Pin assignments and logic are defined at the top of the file.
- Battery voltage is measured via a voltage divider (2 × 100kΩ resistors) to ADC0 (GP26).
- USB/VSYS is detected via internal voltage divider to ADC3 (GP29). If VSYS > 4.2V, USB is considered connected.
- The relay is used to cut off all power to the system after each operation or charging session, maximizing battery life.
- The servo is controlled by PWM (50Hz, duty cycle for stop/forward/reverse adjustable in code).
- Both the internal LED and the button LED are used for status indication (on, off, blink fast/slow).
- All ADC readings are averaged for stability.

## State Chart

<img src="img/states.svg" alt="State Chart" width="600"/>

## Usage Notes
- **Upload the firmware** to your RP2040-Plus using a tool like Thonny or ampy.
- **Ensure all voltage dividers are correctly wired** to avoid over-voltage on ADC pins (never exceed 3.3V on GPIOs).
- **Servo calibration:** If the servo does not stop or rotate as expected, adjust the PWM duty cycle values in the firmware.
- **Safety:** Always disconnect the battery and USB before modifying wiring.

## License
This project is open-source and provided as-is. See the original [eWDT model](https://www.printables.com/model/591918-ewdt) for hardware inspiration.


