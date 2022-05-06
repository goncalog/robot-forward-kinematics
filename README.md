# Robot Forward Kinematics

This is a Python script that uses forward kinematics to generate a path for a two-wheeled robot from its wheel speeds. It also projects 2D laser scans data around the generated path.

## How to run it
To run the script and generate the graphs, please follow these instructions:

1. Clone this repo
```bash
git clone https://github.com/goncalog/robot-forward-kinematics.git
cd robot-forward-kinematics
```

2. Extract the data and save it to .txt files:

If you have saved the data to a bag file, re-play it and save it to files with the following commands:
```bash
ros2 topic echo <topic-name> >> wheel_velocity_axis0.txt
ros2 topic echo <topic-name> >> wheel_velocity_axis1.txt
ros2 topic echo -f <topic-name> >> laser.txt
```
(you need to have ROS2 installed for this to work; alternatively use a Docker image to run everything - [docs.ros.org/en/foxy/How-To-Guides/Run-2-nodes-in-single-or-separate-docker-containers.html](https://docs.ros.org/en/foxy/How-To-Guides/Run-2-nodes-in-single-or-separate-docker-containers.html))

3. Run the python script

In the root project folder *robot-forward-kinematics*:
```bash
python3 main.py
```

## Tech stack
- Python3
- ROS2
- Docker
