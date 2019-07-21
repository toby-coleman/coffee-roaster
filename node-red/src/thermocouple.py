import argparse
import math
import Adafruit_MAX31855.MAX31855 as MAX31855


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Read thermocouple')
    parser.add_argument('--clk', default=25, type=int, help='Clock')
    parser.add_argument('--cs', default=24, type=int, help='Chip select')
    parser.add_argument('--do', default=18, type=int, help='Data out')
    parser.add_argument('--samples', default=1, type=int, help='Number of samples')
    args = parser.parse_args()

    sensor = MAX31855.MAX31855(args.clk, args.cs, args.do)

    internal_temp = sensor.readInternalC()
    samples = [sensor.readTempC() for x in range(args.samples)]
    # Remove any bad readings
    samples = [s for s in samples if not math.isnan(s)]
    if len(samples) > 3:
        # Take trimmed mean
        samples = sorted(samples)[1:-1]
    thermocouple_temp = sum(samples) / len(samples)
    
    # Print output in CSV format
    print('{0},{1}'.format(thermocouple_temp, internal_temp))
