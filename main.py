# eWDT MicroPython Firmware for RP2040-Plus
# Implements requirements from README, using VBUS detection via ADC1 (GP27)

import machine
import time

# Pin assignments (adjust if needed)
SERVO_PIN = 15         # PWM output for servo
RELAY_PIN = 14         # Digital output for relay
SWITCH_PIN = 13        # Digital input for momentary switch
LED_PIN = 25           # Digital output for switch LED
BATTERY_ADC_PIN = 26   # ADC0 for battery voltage divider
VREF_ADC_PIN = 29      # ADC3 for VSYS detection (via internal voltage divider)

# Constants
SERVO_ON_TIME = 5  # seconds
LOW_BATTERY_VOLTAGE = 3.4  # volts
FULL_BATTERY_VOLTAGE = 4.1  # volts
LED_BLINK_INTERVAL = 0.5  # seconds

# Setup pins
servo = machine.PWM(machine.Pin(SERVO_PIN))
servo.freq(50)
relay = machine.Pin(RELAY_PIN, machine.Pin.OUT)
switch = machine.Pin(SWITCH_PIN, machine.Pin.IN, machine.Pin.PULL_DOWN)
led = machine.Pin(LED_PIN, machine.Pin.OUT)
battery_adc = machine.ADC(BATTERY_ADC_PIN)
vref_adc = machine.ADC(VREF_ADC_PIN)


# Helper: Read battery voltage (adjust conversion for your divider)
def read_battery_voltage():
    raw = battery_adc.read_u16()
    voltage = (raw / 65535) * 3.3 * 2  # 2x for divider
    return voltage


# Helper: Read VREF voltage (internal voltage divider)
def read_vref_voltage():
    raw = vref_adc.read_u16()
    voltage = (raw / 65535) * 3.3 * 3  # 3.3V internal reference, 3x for internal divider
    return voltage


# Helper: Detect USB connection via VBUS (divider to ADC1)
def is_usb_connected():
    vref_voltage = read_vref_voltage()
    return vref_voltage > 4.5 # vref_adc higher than 4.5V means USB connected


# Helper: Set servo speed for continuous rotation
def set_servo_speed(speed):
    """
    speed: -1.0 (full speed clockwise) to 0 (stop) to 1.0 (full speed counter clockwise)
    """
    # For 50Hz PWM, 1.5ms pulse is stop, 1.0ms is full reverse, 2.0ms is full forward
    # 1.0ms/20ms = 5%, 1.5ms/20ms = 7.5%, 2.0ms/20ms = 10%
    min_duty = 2100   # 5% of 65535 - decreased by exepriemnt
    mid_duty = 4915   # 7.5% of 65535
    max_duty = 7600   # 10% of 65535 - increased by exepriemnt
    if speed > 0:
        duty = int(mid_duty + (max_duty - mid_duty) * speed)
    elif speed < 0:
        duty = int(mid_duty + (mid_duty - min_duty) * speed)
    else:
        duty = mid_duty
    print('duty cycle: ', duty)
    servo.duty_u16(duty)

# Helper: Blink LED
def blink_led(times, interval):
    for _ in range(times):
        led.on()
        time.sleep(interval)
        led.off()
        time.sleep(interval)

# Charging mode: LED blinks slowly until battery is full, then off
def charging_mode():
    while is_usb_connected():
        if read_battery_voltage() < FULL_BATTERY_VOLTAGE:
            blink_led(1, LED_BLINK_INTERVAL)
        else:
            led.off()
            return


# Main loop
def main():        
    while True:
        if is_usb_connected():
            print("USB connected")
            charging_mode()
            relay.off()  # Ensure relay is off after charging
            continue  # Ignore switch while charging        
        else:
            print("USB not connected")
            if switch.value():
                print("Button pressed")
                # Start servo and relay
                relay.on()
                led.on()
                set_servo_speed(1.0)  # Full speed forward
                time.sleep(SERVO_ON_TIME)
                set_servo_speed(0)    # Stop
                relay.off()
                led.off()
                if read_battery_voltage() < LOW_BATTERY_VOLTAGE:
                    blink_led(4, 0.25)  # 2 seconds total
                relay.off()  # Ensure relay is off after operation
            else:
                led.off()
        time.sleep(0.1)


main() 

