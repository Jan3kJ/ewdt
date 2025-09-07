# eWDT MicroPython Firmware for RP2040-Plus
# Implements requirements from README, using VBUS detection via ADC1 (GP27)

from machine import PWM, Pin, ADC
import time

# Pin assignments (adjust if needed)
SERVO_PIN = 15         # PWM output for servo
RELAY_PIN = 5         # Digital output for relay
LED_PIN = 25           # Digital output for internal LED
BUTTON_LED_PIN = 9    # Digital output for BUTTON LED
BATTERY_ADC_PIN = 26   # ADC0 for battery voltage divider
VREF_ADC_PIN = 29      # ADC3 for VSYS detection (via internal voltage divider)

# Constants
SERVO_ON_TIME = 7  # seconds, eWDT runtime 
LOW_BATTERY_VOLTAGE = 3.7  # volts, >10% capacity
FULL_BATTERY_VOLTAGE = 4.1  # volts, ~90% capacity
LED_BLINK_INTERVAL_SLOW = 3  # seconds
LED_BLINK_INTERVAL_FAST = 0.8  # seconds
ADC_STABILIZATION_TIME = 0.1  # seconds for ADC to stabilize
ADC_READINGS_COUNT = 5  # number of readings to average for stability

# Setup pins
servo = PWM(Pin(SERVO_PIN))
servo.freq(50)
relay = Pin(RELAY_PIN, Pin.OUT)
led = Pin(LED_PIN, Pin.OUT)
button_led = Pin(BUTTON_LED_PIN, Pin.OUT)
battery_adc = ADC(BATTERY_ADC_PIN)
vref_adc = ADC(VREF_ADC_PIN)


# Helper: Initialize ADC with proper stabilization
def init_adc():
    """Initialize ADC and wait for stabilization"""
    # Take a few readings to warm up the ADC
    for _ in range(3):
        battery_adc.read_u16()
        vref_adc.read_u16()
        time.sleep(0.01)
    
    # Wait for proper stabilization
    time.sleep(ADC_STABILIZATION_TIME)


# Helper: Read ADC with averaging for stability
def read_adc_stable(adc, samples=ADC_READINGS_COUNT):
    """Read ADC multiple times and return average for stability"""
    readings = []
    for _ in range(samples):
        readings.append(adc.read_u16())
        time.sleep(0.01)  # Small delay between readings
    
    # Simple average of all readings
    return sum(readings) / len(readings)


# Helper: Read battery voltage (adjust conversion for your divider)
def read_battery_voltage():
    raw = read_adc_stable(battery_adc)
    voltage = (raw / 65535) * 3.3 * 2  # 2x for divider
    return round(voltage, 2)


# Helper: Read VREF voltage (internal voltage divider)
def read_vref_voltage():
    raw = read_adc_stable(vref_adc)
    voltage = (raw / 65535) * 3.3 * 3  # 3.3V internal reference, 3x for internal divider
    return round(voltage, 2)


# Helper: Detect USB connection via VBUS (divider to ADC1) with multiple checks
def is_usb_connected():
    """Detect USB connection with multiple readings for reliability"""
    # Take multiple readings to ensure stable detection
    usb_detected_count = 0
    total_checks = 3
    
    for _ in range(total_checks):
        vref_voltage = read_vref_voltage()
        if vref_voltage > 4.2:  # vref_adc higher than 4.2V means USB connected
            usb_detected_count += 1
        time.sleep(0.01)  # Small delay between checks
    
    # Require majority of readings to indicate USB connection
    return usb_detected_count >= (total_checks // 2 + 1)


def print_voltage():
    if is_usb_connected():
        print('VRef: {} V'.format(read_vref_voltage()))
        print('VBat: {} V'.format(read_battery_voltage()))


def led_on():
    led.on()  # interal LED for debugging
    button_led.on()


def led_off():
    led.off()
    button_led.off()


# Helper: Set servo speed for continuous rotation
def set_servo_speed(speed):
    """
    speed: -1.0 (full speed clockwise) to 0 (stop) to 1.0 (full speed counter clockwise)
    """
    # For 50Hz PWM, 1.5ms pulse is stop, 1.0ms is full reverse, 2.0ms is full forward
    # 1.0ms/20ms = 5%, 1.5ms/20ms = 7.5%, 2.0ms/20ms = 10%
    min_duty = 2100   # 5% of 65535 - decreased by exeperiment
    mid_duty = 4915   # 7.5% of 65535
    max_duty = 7600   # 10% of 65535 - increased by exeperiment
    if speed > 0:
        duty = int(mid_duty + (max_duty - mid_duty) * speed)
    elif speed < 0:
        duty = int(mid_duty + (mid_duty - min_duty) * speed)
    else:
        duty = mid_duty
    print('duty cycle: ', duty)
    servo.duty_u16(duty)


# Helper: Blink LED
def blink_led(times, interval, interrupt=False):
    for _ in range(times):
        led_on()
        if interrupt and not is_usb_connected(): break  # interrupt if usb get disconnected
        time.sleep(interval)
        led_off()
        if interrupt and not is_usb_connected(): break  # interrupt if usb get disconnected
        time.sleep(interval/2)  # 1/2 of interval off looks better


# Charging mode: LED blinks slowly until battery is full, then off
def charging_mode():
    while is_usb_connected():
        if read_battery_voltage() < FULL_BATTERY_VOLTAGE:
            blink_led(30, LED_BLINK_INTERVAL_SLOW, interrupt=True)
            print_voltage()
        else:
            # fully charged and usb still connected
            print('Battery fully charged')
            print_voltage()
            led_on()
            relay.off()
            time.sleep(10)

    # if unplugged befor fully charged
    led_off()
    relay.off()  # Ensure relay is off after charging


def normal_mode():
    # Start servo and relay
    led_on()
    set_servo_speed(1.0)  # Full speed forward
    time.sleep(SERVO_ON_TIME)
    set_servo_speed(0)    # Stop
    led_off()
    time.sleep(ADC_STABILIZATION_TIME)  # small delay after servo is stopped to avoid wrong adc readings
    if read_battery_voltage() < LOW_BATTERY_VOLTAGE:
        blink_led(4, LED_BLINK_INTERVAL_FAST)  
    relay.off()  # Ensure relay is off after operation


# Main function
def main():        
    relay.on()
    led_on()  # recognize button press
    
    # Initialize ADC properly before making any decisions
    print("Initializing ADC...")
    init_adc()
    
    # Double-check USB connection with proper delay
    print("Checking USB connection...")
    if is_usb_connected():
        print("USB connected")
        print_voltage()
        charging_mode()
    else:
        print("USB not connected")
        normal_mode()

    led_off()
    relay.off()  # Ensure relay is off after charging
    
set_servo_speed(0)  # ensure servo is stopped when powered via usb
main()

# for testing, when running this file directly via MicroPico
print_voltage()
relay.off()
