# First Homework

**Foundational Cloud Infrastructure and Performance Analysis of a Containerized LLM Inference Service using the Docker Ecosystem**

Due date until <mark>1403-12-29</mark> at [this](https://docs.google.com/forms/d/e/1FAIpQLSd8tSIPcoEG5eFrucAlWCkpcZtAXNzwP7KmUrP_oICzbUSurw/viewform?usp=dialog) google form.

## Description

This introductory homework assignment is designed to establish a foundational understanding of core cloud infrastructure technologies, specifically focusing on containerization, multi-container orchestration, and basic service orchestration using the Docker ecosystem. Within the context of a cloud-native paradigm, this exercise explores the practical application of Docker, Docker Compose, and Docker Swarm for deploying and managing a representative application: <mark>an LLM-based sentiment analysis inference service</mark>.

The assignment emphasizes empirical performance analysis as a critical aspect of cloud deployments. Students will systematically progress through containerizing the LLM service with Docker, orchestrating it as a multi-container application using Docker Compose, and subsequently deploying and scaling it using Docker Swarm. At each stage, students are tasked with rigorously measuring and documenting key performance indicators, namely, **inference latency and resource utilization** (CPU, memory and Network I/O).

This methodical approach enables students to directly observe and quantify the impact of containerization and orchestration on the performance characteristics of the LLM inference service. By comparing performance metrics across different deployment configurations, students will gain practical insights into the benefits and potential trade-offs associated with each Docker tool in terms of latency and resource consumption.

## Objective

* **Containerize an Application using Docker:** Successfully package an LLM inference service into a Docker container, demonstrating proficiency in Dockerfile creation and image management.
* **Orchestrate Multi-Container Applications with Docker Compose:** Utilize Docker Compose to define and manage a single-service application, understanding the benefits of declarative configuration for containerized workloads.
* **Deploy and Scale Services with Docker Swarm:** Employ Docker Swarm to deploy the LLM inference service as a scalable service, exploring basic service orchestration and replica management.
* **Measure and Analyze Performance Metrics:** Implement and execute a performance measurement methodology to quantify inference latency and resource utilization (CPU and memory) for the LLM inference service across different Docker deployment configurations.
* **Compare Performance across Docker Tools:** Analyze and compare the measured performance data obtained from Docker containers, Docker Compose, and Docker Swarm deployments, drawing informed conclusions about the performance implications of each technology.
* **Establish a Baseline for Cloud Performance Analysis:** Develop a foundational understanding of performance metrics and measurement techniques in cloud environments, setting the stage for more sophisticated monitoring and analysis in subsequent assignments and research endeavors.


## Report expectations

- Compare and explain the monitored metrics, such as CPU, memory, network I/O, and latency, in a plot for all four deployment methods.
- Explain the pros and cons of running an application on your own system, Docker, Docker Compose, and Docker Swarm in your own words.

## Instructions

Considering this project structure:

```md
homeworks/one/
├── app.py (Python Flask application with LLM inference and logging)
├── Dockerfile (Dockerfile for containerizing the app)
├── requirements.txt (Python dependencies)
└── docker-compose.yml (Docker Compose configuration)
```

One has to set the working directory to `homeworks/one`, then create a new Python virtual environment in this folder and activate it (optional but recommended).

### Host machine setup

```sh
$ pip install -r ./requirements.txt
```

Take a quick look at the code located in `app.py`. There is an environment variable called `METRICS_LOG_FILE`. You need to change its value by setting it as a system environment variable in the next steps. This variable determines the file where the application will put outputs, and by default, it is `system_inference_metrics.csv`.

Then run the application on your own system via:

```sh
$ python ./app.py
```

When you run the application for the first time, it will take a moment to fetch the required packages. Please be patient until it is done.

The output logs are as follows:

```log
Device set to use cpu
* Serving Flask app 'app'
* Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
* Running on all addresses (0.0.0.0)
* Running on http://127.0.0.1:5000
* Running on http://172.31.16.142:5000
Press CTRL+C to quit
```

The first IP, 127.0.0.1, is your localhost system IP, which is the IP address you need to work with.

To ensure the inference application works fine, open another terminal and run this command:

```sh
# Example Request
$ curl -X POST -H "Content-Type: application/json" -d '{"text": "This movie was fantastic!"}' http://localhost:5000/infer
```

The result of a query is a CSV-formatted text like:

```csv
Inference Latency (ms),Prediction,Input Text,Timestamp
205.87,POSITIVE,This movie was fantastic!,2025-03-01T00:31:16.866537
```

Just take a look at the CSV file created with the name `system_inference_metrics.csv` and see the latency of the query. After viewing the CSV file content, <mark>delete it</mark>.

For this step, you need to run the `latency_test.sh` file via:

```sh
$ sh ./latency_test.sh 127.0.0.1 5000
```

In this script there is bunch of different comments about movies. After running it, the output is like:

```log
...
Query 157
Query 158
Query 159
Query 160
```

Note that the `system_inference_metrics.csv` file must contain <mark>161</mark> tuples.

### Containerization

After running these queries and fetching the results, please go ahead and take a look at the `Dockerfile`. I have filled this file with comments so you can understand what I am looking for in this file, but let me explain it here too. The file is the manifest you need to create a Docker image, but creating it does not mean you are running it. It is a manifest to show the orchestration tools how to build your image. You need to follow eight steps to build your image. These steps are as follows:

<ol>
<li>Use the official Python 3.12-slim image as the base image.</li>
<li>Set the working directory inside the container to /app.</li>
<li>Copy the requirements.txt file from the host machine to the container's working directory.</li>
<li>Install Python dependencies listed in requirements.txt.</li>
<li>Copy the app.py file from the host machine to the container's working directory.</li>
<li>Set an environment variable inside the container for the CSV file. This variable specifies the name of the CSV file to be used by the application, <mark><b>which must be `docker_system_inference_metrics.csv`.</b></mark></li>
<li>Expose port 5000 to allow external access to the application running inside the container.</li>
<li>Specify the command to run the application when the container starts.</li>
</ol>

You have to use these keywords and <mark>nothing</mark> other than these:

```docker
FROM
WORKDIR
COPY
ENV
RUN
EXPOSE
CMD
```

Then build the image with the name <mark>`llm-inference-image`</mark>, push it to [Docker Hub](https://hub.docker.com) (you need an account for that), and provide the image name like `<YOUR_DOCKER_HUB_NAME>/llm-inference-image` in your report.

```sh
# Just to be specific, build the image via `llm-inference-image` name:
$ docker build -t llm-inference-image .
```

**BONUS**: Use a GitHub action to create a CI pipeline, which means Continuous Integration:

**Code → Build → ~~Test~~ → Push Image**

Run the image to create a Docker container with the name `llm-inference-container` and do the port mapping so that it runs on port 5000 on your host machine.

Then run this command to send the queries:

```sh
# DO NOT CHANGE THE 127.0.0.1 IP ADDRESS
$ sh ./latency_test.sh 127.0.0.1 5000
```

If you have done the port mapping correctly, your queries will be sent out properly.

**NOTE**: Observe and note down the `CPU %`, `MEM %`, and `NET I/O` values while running the queries via the `docker stats` command. Report them.

Then connect to the container shell via:

```sh
$ docker exec -it llm-inference-container /bin/bash
```

Here, you will connect to the Docker container shell, and you have to be in the working directory that you set in the `Dockerfile`. Find the `docker_system_inference_metrics.csv` file, which I already told you to set after running the queries.

```sh
$ docker exec -it llm-inference-container /bin/bash
# Check to have these files in `/app` dir
# root@sth:/app# ls
# app.py docker_system_inference_metrics.csv requirements.txt
```

After finding the `docker_system_inference_metrics.csv` file path in your Docker container, copy it to your host machine via the `docker cp` command.

Stop (`docker stop`) and remove (`docker rm`) the container.

### Composing!

In this step, like the previous step, first make the `docker-compose.yml` file. The file is empty. Here are the notes you have to keep in mind when writing the `docker-compose.yml` file:

- Use your own image that you had published on Docker Hub (do not use a local image).
- Map the port so that you can run queries with this command:

```sh
# DO NOT CHANGE THE 127.0.0.1 IP ADDRESS
$ sh ./latency_test.sh 127.0.0.1 8080
```

- Set the correct value for the `METRICS_LOG_FILE` environment variable so that it provides the name `inside_compose_inference_metrics.csv` for the applications output.
- Define a volume so that it maps the `inside_compose_inference_metrics.csv` file from the container to the `compose_inference_metrics.csv` file in your host machine.

Do the composing, run the container, execute the queries while getting the container states, and turn down the container via Docker Compose.

### Orchestration & Scaling

Here, you need to work with Docker `swarm`.

First, run this command to enable Docker Swarm:

```sh
$ docker swarm init
```

Now deploy your image as a service:

```sh
$ docker service create --name llm-inference-service --publish 8080:5000 llm-inference-image:latest
```

**Note**: the service name should be **<mark>`llm-inference-service`</mark>**

Now, like before, run the queries via this command while monitoring its container via the `docker stats` command:

```sh
$ sh ./latency_test.sh 127.0.0.1 8080
```

Here, the configuration is just having one replica. In a scalable, reliable and available system, we need backups in case of any issues, so increase the number of containers to 3 by this command:

```sh
$ docker service scale llm-inference-service=3
```

Then check the service via:

```sh
$ docker service ps llm-inference-service
```

Now first run the `docker stats` and then run the queries again. How would you describe the change in all three containers' metrics like `NET I/O` values? <mark>Provide a detailed explanation in your report</mark>.

Now stop the services and leave the swarm by:

```sh
$ docker service rm llm-inference-service
$ docker swarm leave --force
```

The first homework is done.
