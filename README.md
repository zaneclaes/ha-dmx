# DMX Lighting Controller for Home Assistant

## About

Control your USB DMX lights via Home Assistant.

## Requirements

You must have Home Assistant with a MQTT broker.

The Home Assistant computer must have a USB-to-DMX device attached (i.e., the [Enttec DMX Pro](https://amzn.to/43KLCSn))

## Installation

1. Add this repository (https://github.com/zaneclaes/ha-dmx) to your Home Assistant add-on repositories.
2. In the options, choose your USB device and conifgure your MQTT broker (more about the lighting options below).
3. Start the add-on and check the log output to make sure that your USB-to-DMX device is detected and the Universe is created properly:

```
--- devices ---
Device 1: Dummy Device
  port 0, OUT Dummy Port, RDM supported
Device 2: Enttec Usb Pro Device, Serial #: 02347365, firmware 1.44
  port 0, IN, priority 100
  port 0, OUT
--- universe ---
Creating Universe #1 for Device #2 and Port #0
```

If you see something other that `Device 2` and `port 0` (for OUT communication) in the device list, change your `device_num` and `device_port` options accordingly. 

If connecting more than one light, you may need to modify the `light_bytes` option to match the packet size of each light. The default is 4 bytes, for brightess+RGB. However, many lights may have additional settings like a 5th "effect" byte (i.e., strobe). In this case, set the `light_bytes` to 5 (the effect is not supported by this add-on, but failure to set the `light_bytes` will cause subsequent lights to start at the wrong address).

## Usage

The add-on will automatically create the maximum amount of RGB lights in Home Assistant. Make sure that the lights are set to DMX mode (if applicable) and are configured for the correct channel.

## Example

The [U'King LED Uplights](https://amzn.to/4kueQvj) have a 5th "effect" byte, so `light_bytes` is set to 5. The OUT from the Enttec Pro is connected to the IN on the first uplight, and then they are daisy-chained together. 

DMX mode is enabled by pressing the `MODE` button on the back of the uplight until "d001" appears. For the second uplight, the `UP` button is pressed to select "d005" (matching the second dmx address), and so on.

## Limitations

Each DMX device must follow the standard brightness+RGB pattern (i.e., [b,r,g,b]). The software assumes it can write these 4 bytes at each channel offset to drive the lights.