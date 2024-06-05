# Using S7 device service

In this tutorial, you will be using the S7 device service instead of the virtual in the previous.

As the S7 device service require a S7 device to read so in this case we will be using a Simulate added to the docker compose file.

## Tutorial Structure

The tutorial folder contains the following structure:
```
tutorial/
├── docker-compose.yml
└── s7/
    ├── commands/
    │   └── ... shell script to run commands
    └── deployment/
        ├── config/
        │   ├── main.json
        │   ├── s7.json
        │   └── ... component config files
        ├── profiles/
        │   └── profile.json
        │   └── ... your profiles  
        └── state/
            ├── devices.json
            └── schedules.json
``` 
# Changes from last tutorial
-   The Virtual device service config has been swapped from the previous tutorial to a S7 device service.
-   The mqtt_bridge.json has been updated to use the s7 topic rather then virtual.
-   The commands, profiles and state directory have been updated to be relevant to S7 device.
-   The docker-compose.yml now has a s7 simulator in it and XRT now has a enviroment variable for the ip address of the S7 device which is called `S7_SIM_ADDRESS`.

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

Well Done! You have successfully run the S7 device service.

When you are ready feel free to move on to tutorial 3 where we will be using a XRT instance with two device services, the virtual device service from tutorial 1 and S7 from tutorial 2. It also will include a OPC-UA server which you can access from our OPC-UA browser to see the values in the devices.