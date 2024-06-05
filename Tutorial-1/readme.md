# Getting Started with XRT

In this tutorial, you will learn the basics of XRT and how to set up and run an XRT instance using Docker Compose.

You will be using the virtual device service in XRT to do this which is a device used for testing and learning XRT without the need to connect to a actual device or simulator.

## Prerequisites

Before you begin, make sure you have the following installed on your system:

-   Docker: [Install Docker](https://docs.docker.com/get-docker/)
-   Docker Compose: [Install Docker Compose](https://docs.docker.com/compose/install/)
-   Mosquitto client: [Install Mosquitto Client](http://www.steves-internet-guide.com/install-mosquitto-linux/)

Please note that you also need to ensure you have no other MQTT brokers running on port 1883. This can be done like the following `systemctl start mosquitto.service` for mosquitto mqtt.

You must also have a XRT License and have the enviroment variable XRT_LICENSE_FILE set to the path to the file.

## Tutorial Structure

The tutorial folder contains the following structure:
```
tutorial/
├── docker-compose.yml
└── virtual/
    ├── commands/
    │   └── ... shell script to run commands
    └── deployment/
        ├── config/
        │   ├── main.json
        │   └── ... component config files
        ├── profiles/
        │   └── profile.json
        │   └── ... your profiles  
        └── state/
            ├── devices.json
            └── schedules.json
``` 
-   The `docker-compose.yml` file is used to define and run the XRT instance, and MQTT broker.
-   The `virtual` folder contains the necessary configurations and commands for XRT.

## Configuration

### Commands

The `commands` folder holds a range of commands you can send over MQTT to XRT through the MQTT management API. More information on this can be found at [https://docs.iotechsys.com/edge-xrt22/mqtt-management/mqtt-management.html#get-device-resources](https://docs.iotechsys.com/edge-xrt22/mqtt-management/mqtt-management.html#get-device-resources).

### Deployment

The `deployment` folder contains the configuration for XRT and is further divided into three folders:

1.  `config`: This folder holds the JSON files used to configure your XRT instance with specific components and their settings. Each component has its own config file, and all config files are specified in the `main.json` file within this folder. This is usually point to by XRT_CONFIG_DIR.
2.  `profiles`: This folder holds the configurations for devices, and each configuration is specific to the device service the device will use. This is usually point to by XRT_PROFILE_DIR.
    -   `profiles.json`: Holds a list of all profile in this folder.
3.  `state`: This folder contains two JSON files used to store the state of XRT. This is usually point to by XRT_STATE_DIR.
    -   `devices.json`: Holds a list of all devices, including their names, profiles they use, and any other device-specific configurations.
    -   `schedules.json`: Holds a list of scheduled reads, with each schedule having a device they are reading, the interval, the name of the schedule, and the resource(s) it is reading.

## Running the XRT Instance

To start the XRT instance, MQTT broker, and web UI, follow these steps:

1.  Open a terminal and navigate to the tutorial folder containing the `docker-compose.yml` file.
2.  Run the following command to start the XRT instance, and MQTT broker:
	```
	docker compose up
	```
	This command will read the `docker-compose.yml` file and start the necessary containers.
3.  Once the containers are up and running, you can run commands in the commands file.
    You can also see the requests, replies and telemetry data by using `mosquitto_sub -t '#'`
4.  Once you are done use `docker compose down` to pull down the containers

## Conclusion

Congratulations! You have successfully set up and run an XRT instance using Docker Compose. You can now explore the different configurations, send commands to XRT through MQTT, and monitor the data being sent to MQTT.

Feel free to modify the configurations and experiment with different settings to further understand the capabilities of XRT.

When you are ready feel free to move on to tutorial 2 where we will be using a S7 device service to communicate with a simulator using profiles you will generate yourself!
