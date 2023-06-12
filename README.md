# IoTDeviceControllerWithApp

Project Title: IoT Based Micro-service Architecture for Embedded Systems Control
This project showcases a backend micro-service architecture designed to interact with an IoT based embedded system. The application allows users to monitor and control the parameters of the embedded system remotely through an intuitive web interface. The underlying micro-services architecture makes the system highly scalable, flexible, and capable of handling real-time data streams.



Core Functionalities:
Control Service: This service provides an interface to control the parameters of the embedded system. Users can update the temperature threshold and the angle of rotation of the actuator remotely through the provided endpoints.
Logging Service: This service is responsible for recording the actions of the embedded system. It captures and stores the sensor data in a SQLite database. Users can query this data anytime to understand the system behavior over a period of time.
Service Registry: This is the Service Finder that acts as a central registry for all the micro-services in the architecture. Each service registers itself with the Service Finder upon startup, providing its name and network address.
API Gateway: This component acts as a single-entry point to the system, routing the incoming requests to the appropriate service. This layer also provides additional functionalities such as request logging, error handling, and enabling CORS for the system.
Cloud-based IP Address Management: We have implemented a cloud-based IP address management solution where each microservice updates its IP address upon startup. Other services can fetch the updated IP addresses from the cloud.
The project is implemented using Python with Flask and FastAPI, and the data storage is managed by SQLite and Redis databases.



How to Use:
PowerShell Script Specifications:
The script initializes multiple services that are integral to an IoT based micro-service architecture. The script primarily focuses on setting up and managing Docker containers and starting various micro-services within a specific environment.

Pre-requisites:
Docker installed and running
Internet connection
Features:
The script starts the necessary services required for the project by spinning up Docker containers and initiating server instances for each of the micro-services.
The script checks for the status of a Docker container named 'control-cache' and takes the necessary action based on the status (running, exited, paused).
The script uses four Start-Job cmdlets to spin up four different micro-services, each running on a different port.
Docker Container:
The 'control-cache' container is responsible for running a Redis server on port 6379.
Micro-services:
Service Finder: Runs on port 8001, acts as the registry for all the micro-services.
Logging Service: Runs on port 8002, records the actions of the embedded system.
Control Service: Runs on port 8003, provides an interface to control the parameters of the embedded system.
API Gateway: Runs on port 8000, acts as the entry point to the system, routing the incoming requests to the appropriate service.
Implementation:
PowerShell is the scripting language used for the implementation.
Docker is used for creating and managing containers.
Start-Job cmdlets are used to spin up micro-services in the background.
The script uses the waitress-serve and uvicorn ASGI servers to start the applications.
The script also uses the Start-Sleep cmdlet to add delays between the initialization of different services, allowing each service enough time to fully initialize before the next one starts.
Usage:
This script is typically run as part of the project startup process, whenever the project's services need to be initialized. It should be run on a system that meets the pre-requisites and has all the necessary micro-service codebases in the appropriate directories.

Please replace 'C:\Users\gabri\OneDrive\Área de Trabalho\frank\projeto final\backend\' with your project path for each service. The script is designed to be run from a PowerShell command prompt.

In the root directory of the project, run ./run.ps1 in the powershell command line.



Specs:

Embedded System:

Technology: ESP8266 microcontroller

Functionalities:
Temperature reading with the DHT11 sensor.
Control of a servo motor.
Wi-Fi connectivity and HTTP communication.
Retrieval of control parameters from a server (condition and angle).
Sending temperature readings and activation status to the server.




Frontend:

Technology: React Native with Expo

Functionalities:
Fetching and storing the gateway IP address from a remote server using HTTP communication.
Displaying a dynamic user interface that adjusts based on fetched data (loading and error states).
Fetching control parameters (rotation angle for a servo and a temperature threshold) from the server and presenting these in an adjustable slider interface.
Sending updated control parameters to the server using HTTP communication.
Fetching a list of sensor data from the server.
Displaying sensor data (including a trigger status, a temperature value, and a timestamp) in a tabular format.
Providing a manual refresh option for the user to fetch the latest sensor data from the server.




Backend:


Finder Service:

Technology: Python, Flask, Requests, Waittress

Functionalities:

Maintains a list of services (name and address) that register with it.
Sends the local machine's IP address to a cloud-based API for others to use.
Provides routes for services to register themselves and their addresses.
Provides a route for clients to get a list of all registered services.
Logs request and response data for all incoming requests.


Logging Service:

Technology: Python, FastAPI, SQLAlchemy, Requests, Uvicorn

Functionalities:

Registers itself with the Finder service upon startup.
Maintains a SQLite database for storing sensor data.
Provides a route for recording sensor data in the database.
Provides a route for clients to fetch all recorded sensor data.
Logs request and response data for all incoming requests.


Control Service:

Technology: Python, FastAPI, Redis, Requests, Uvicorn

Functionalities:

Registers itself with the Finder service upon startup.
Maintains Redis database for storing control parameters (temperature condition and actuator rotation angle).
Provides routes for updating and fetching the control parameters.
Logs request and response data for all incoming requests.


Gateway Service:

Technology: Python, FastAPI, HTTPX, Requests, Uvicorn

Functionalities:

Fetches the list of all services from the Finder service upon startup.
Provides a unified API endpoint to interact with all other services.
Forwards incoming requests to the appropriate service based on the service name in the request URL.
Handles exceptions and sends appropriate responses.
