# Using S7 device service

In this tutorial, you will be using both the virtual and S7 device service at the same time.

You will be then viewing these 

## Tutorial Structure

The tutorial folder contains the following structure:
```
tutorial/
├── docker-compose.yml
└── deployment/
    ├── commands/
    │   └── ... shell script to run S7 Virtual commands
    ├── Dockerfile
    ├── python_app
    |   ├── templates
    |   ├── app.py
    |   └── requirements.txt
    └── deployment/
        └──... same as deployment in Tutorial 3
``` 
# Changes from last tutorial
-   The XRT instance now has config for S7, Virtual and opc-ua server.
-   S7 and Virtual now have updated profile and state dirs which are now pointing to folders inside XRT_PROFILE_DIR.
    For example this is what it is for virtual ${XRT_PROFILE_DIR}/virtual, ${XRT_STATE_DIR}/virtual.
    This is because they have to be kept seperate as each device service has different config options.
-   The docker compose file now has a OPC-UA Browser container in it to allow you to see the results. This can be access on localhost:8080 using TODO as the server address

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

Amazing, You have successfully run the Virtual and S7 device service with the OPC-UA Browser. I hope your starting to see how flexible XRT is and how it allows you to do alsorts of configs.

In tutorial 4 we will be looking at adding a python program which subscribes to MQTT broker for the reading of values from the virtual device and the s7 device. It then does some data processing on this data every 10 secounds in this case put it through a bit of machine learning called a linear regression. It then publishs the result back to the virtual devices. 