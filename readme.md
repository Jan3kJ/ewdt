# Project eWDT

An electric Weiss Distribution Technique (WDT) tool to evenly distribute coffee grounds in the portafilter. This is a remix of Damian's eWDT ([original model](https://www.printables.com/model/591918-ewdt)).

## Overview
This project automates the WDT process using a continuous rotation servo, relay, and a momentary switch with an integrated LED, all powered by a lithium battery and controlled by a Waveshare RP2040-Plus running MicroPython.

## Hardware Components
- **RP2040-Plus by Waveshare**
- **5V Relay**
- **MT3608 Adjustable DC-DC Boost Converter**
- **Lithium Battery**
- **Momentary Switch with Integrated LED**
- **EF90D 360° Continuous Rotation Servo**
- **Voltage Divider (2 × 100kΩ resistors for battery, 2 × 100kΩ for VBUS)**

## Pin Assignments
| Function                | RP2040 Pin | Notes                                      |
|-------------------------|------------|--------------------------------------------|
| Servo PWM               | GP15       | PWM capable                                |
| Relay Control           | GP14       | Digital output                             |
| Switch Input            | GP13       | Digital input, with pull-down resistor     |
| Switch LED              | GP12       | Digital output                             |
| Battery Voltage Sense   | GP26 (ADC0)| Analog input (via voltage divider)         |
| VBUS Sense              | GP27 (ADC1)| Analog input (via voltage divider from VBUS)|

## Wiring Diagram (Textual)
- **Servo**: VCC (5V from boost), GND, Signal to GP15
- **Relay**: VCC, GND, IN to GP14
- **Switch**: One side to GND, other to GP13 (with pull-down)
- **Switch LED**: Anode to GP12 (with resistor), cathode to GND
- **Battery Voltage Divider**: Connect between battery + and GND, center tap to GP26
- **VBUS Voltage Divider**: Connect between VBUS (USB 5V) and GND, center tap to GP27

## Functional Requirements
### Normal Operation
- When the switch is pressed:
    - The relay is activated, powering the system.
    - The servo rotates continuously for 5 seconds (simulating a DC motor action).
    - The switch LED is ON during this time.
    - After 5 seconds, the servo stops, the relay is deactivated (cutting power), and the LED turns OFF.
    - If battery voltage drops below 3.4V, after the servo stops, the switch LED blinks for 2 seconds.
- The relay always switches OFF after operation, cutting off battery power until the button is pressed again.

### Charging Mode
- When USB is connected (VBUS detected):
    - The battery charges.
    - The relay is OFF (system is powered down except for charging logic).
    - The servo cannot be started; switch presses are ignored.
    - The switch LED blinks slowly (0.5s interval) until battery voltage reaches 4.1V, then turns OFF.
    - When charging is complete or USB is disconnected, the relay remains OFF.

## Description
- Battery voltage is measured via a voltage divider (2 × 100kΩ resistors) to ADC0 (GP26).
- USB VBUS is detected via a voltage divider (2 × 100kΩ resistors) to ADC1 (GP27).
- The momentary switch connects the RP2040, MT3608, and relay with the positive terminal of the battery.
- The relay is used to cut off all power to the system after each operation or charging session, maximizing battery life.
- Firmware is written in MicroPython and located in `ewdt/ewdt_firmware.py`.

## Usage Notes
- **Upload the firmware** to your RP2040-Plus using a tool like Thonny or ampy.
- **Ensure all voltage dividers are correctly wired** to avoid over-voltage on ADC pins (never exceed 3.3V on GPIOs).
- **Servo calibration:** If the servo does not stop or rotate as expected, adjust the PWM duty cycle values in the firmware.
- **Safety:** Always disconnect the battery and USB before modifying wiring.

## License
This project is open-source and provided as-is. See the original [eWDT model](https://www.printables.com/model/591918-ewdt) for hardware inspiration.


