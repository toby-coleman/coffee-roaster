import argparse
import math
from busio import SPI
from digitalio import DigitalInOut
import board
import adafruit_max31855


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Read thermocouple')
    parser.add_argument('--samples', default=1, type=int, help='Number of samples')
    args = parser.parse_args()

    spi = SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
    cs = DigitalInOut(board.D6)

    sensor = adafruit_max31855.MAX31855(spi, cs)

    internal_temp = 0 # sensor.reference_temperature
    samples = []
    for x in range(args.samples):
        try:
            samples.append(sensor.temperature_NIST)
        except RuntimeError:
            pass
    # Remove any bad readings
    samples = [s for s in samples if not math.isnan(s)]
    if len(samples) > 3:
        # Take trimmed mean
        samples = sorted(samples)[1:-1]
    thermocouple_temp = sum(samples) / len(samples)
    
    # Print output in CSV format
    print('{0},{1}'.format(thermocouple_temp, internal_temp))
