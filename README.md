# Raspberry Pi Coffee Roaster

This software can control a popcorn-maker for use as a coffee roaster.

## Requirements

1.  Raspberry Pi;
2.  Popcorn maker, modified with a solid-state relay to allow the heater circuit to be turned on/off;
3.  Type K thermocouple to measure the temperature inside the popcorn roaster, aloong with a [MAX31855](https://www.adafruit.com/product/269) circuit to connect it to the Raspberry Pi; and
4.  Account with [balena.io](https://www.balena.io/) to deploy the Raspberry Pi software.

## Initial setup

The software contains three main components:

1.  A [Node-RED](https://nodered.org/) flow, which reads the thermocouple and controls the solid-state relay;
2.  A [Redis](https://redis.io/) database to store data logged by Node-RED; and
3.  A [Dash](https://plot.ly/products/dash/) web interface to view and control the device.

Push the repo to Balena and add the `USERNAME` and `PASSWORD` environment variables to the device. These contain the login credentials for Node-RED - see [here](https://github.com/balena-io-projects/balena-node-red) for instructions on how to create the password.

To view/edit the control flow, go to `http://$RASPBERRY_PI_ADDRESS:8080`.  For the main user interface go to `http://$RASPBERRY_PI_ADDRESS`.

## Useful references

### Raspberry Pi

1.  [Wiring](https://learn.adafruit.com/max31855-thermocouple-python-library?view=all#hardware-spi-2-11) to connect the MAX31855 thermocouple circuit to the Raspberry Pi's SPI interface.
2.  [Raspberry Pi pins](https://pinout.xyz/pinout/spi) for SPI interface.

### Node-RED

1.  Python libraries for [GPIO](https://github.com/adafruit/Adafruit_Python_GPIO) and [MAX31855](https://github.com/adafruit/Adafruit_Python_MAX31855) (required to read the thermocouple).
2.  [Node-RED MAX31855 module](https://github.com/Heatworks/node-red-contrib-adafruit-max31855).

### Redis

1.  [Redis commands](https://redis.io/commands).
