import math
from bokeh.plotting import figure, output_file, save
from IPython.core.display import display, HTML

def get_angular_velocity(vel_left, vel_right, track_width):
    return (vel_right - vel_left) / track_width

def get_signed_distance(vel_left, vel_right, track_width):
    return track_width / 2 * (vel_left + vel_right) / (vel_right - vel_left)

def get_icc(x, y, angular_pos, signed_distance):
    return {
        x: x - signed_distance * math.sin(angular_pos),
        y: y + signed_distance * math.cos(angular_pos),
    }

def calc_new_position(x, y, angular_pos, angular_velocity, d_time, icc):
    new_x = math.cos(angular_velocity * d_time) * (x - icc[x]) - math.sin(angular_velocity * d_time) * (y - icc[y]) + icc[x]
    new_y = math.sin(angular_velocity * d_time) * (x - icc[x]) + math.cos(angular_velocity * d_time) * (y - icc[y]) + icc[y]
    new_angular_pos = angular_pos + angular_velocity * d_time
    return (new_x, new_y, new_angular_pos)

def get_new_position(pos, left_wheel_velocity, right_wheel_velocity, track_width):
    if left_wheel_velocity == right_wheel_velocity:
        new_x = pos[0] + left_wheel_velocity * robot_d_time * math.cos(pos[2])
        new_y = pos[1] + left_wheel_velocity * robot_d_time * math.sin(pos[2])
        return (new_x, new_y, pos[2])
    else:
        angular_velocity = get_angular_velocity(left_wheel_velocity, right_wheel_velocity, track_width)
        signed_distance = get_signed_distance(left_wheel_velocity, right_wheel_velocity, track_width)

        icc = get_icc(pos[0], pos[1], pos[2], signed_distance)

        return calc_new_position(pos[0], pos[1], pos[2], angular_velocity, robot_d_time, icc)

def get_data(path):
    data = []
    with open(path, encoding="utf-8") as file:
        for line in file.readlines():
            if (line.startswith("data")):
                data.append(float(line.replace("data: ", "").replace("\n", "")))

    return data

def get_laser_data(path):
    laser_data = []
    scan = {}
    is_ranges_data = False
    ranges = []
    with open(path, encoding="utf-8") as file:
        for line in file.readlines():
            if (line.startswith("angle_min")):
                scan["angle_min"] = float(line.replace("angle_min: ", "").replace("\n", ""))
            elif (line.startswith("angle_max")):
                scan["angle_max"] = float(line.replace("angle_max: ", "").replace("\n", ""))
            elif (line.startswith("angle_increment")):
                scan["angle_increment"] = float(line.replace("angle_increment: ", "").replace("\n", ""))
            elif (line.startswith("angle_increment")):
                scan["angle_increment"] = float(line.replace("angle_increment: ", "").replace("\n", ""))
            elif (line.startswith("ranges")):
                is_ranges_data = True
            elif (line.startswith("- ")) and is_ranges_data:
                try:
                    ranges.append(float(line.replace("- ", "").replace("\n", "")))
                except:
                    continue
            elif (line.startswith("intensities")):
                scan["ranges"] = ranges
                laser_data.append(scan)
                scan = {}
                is_ranges_data = False
                ranges = []

    return laser_data

def plot(path):
    f = figure(title = "Robot Path", plot_width = 300, plot_height = 300)
    x = [pos[0] for pos in path]
    y = [pos[1] for pos in path]
    f.line(x, y)

    output_file("line.html")
    save(f)

    graph = open("line.html", "r")
    display(HTML(graph.read()))

def calc_scan_points(pos, scan):
    scan_points = []
    starting_angular_pos = pos[2]
    for i, range in enumerate(scan["ranges"]):
        if (range > 0):
            current_angle = starting_angular_pos + (i * scan["angle_increment"])
            scan_point_x = range * math.cos(current_angle) + pos[0]
            scan_point_y = range * math.sin(current_angle) + pos[1]
            scan_points.append((scan_point_x, scan_point_y))
    return scan_points

def project_laser_scans(path, laser_data):
    projected_laser_scans = []
    for i, pos in enumerate(path[1:]):
        projected_laser_scan = calc_scan_points(pos, laser_data[i])
        projected_laser_scans.append(projected_laser_scan)
    return projected_laser_scans

def plot_laser_scans(projected_laser_scans):
    f = figure(title = "Robot Laser Scans", plot_width = 300, plot_height = 300)
    x = [pos[0] for pos in projected_laser_scans]
    y = [pos[1] for pos in projected_laser_scans]
    f.circle(x, y)

    output_file("circle.html")
    save(f)

    graph = open("circle.html", "r")
    display(HTML(graph.read()))

def flatten(list_to_flatten):
    return [item for sublist in list_to_flatten for item in sublist]

def combined_plot(path, projected_laser_scans):
    f = figure(title = "Robot Path + Laser Scans", plot_width = 300, plot_height = 300)
    x = [pos[0] for pos in path]
    y = [pos[1] for pos in path]
    f.line(x, y)

    x1 = [pos[0] for pos in projected_laser_scans]
    y1 = [pos[1] for pos in projected_laser_scans]
    f.circle(x1, y1)

    output_file("line_and_circle.html")
    save(f)

    graph = open("line_and_circle.html", "r")
    display(HTML(graph.read()))

# Upload, process data and generate path graphs
left_wheel_velocities = get_data("wheel_velocity_axis0.txt")
right_wheel_velocities = get_data("wheel_velocity_axis1.txt")

# position -> (x, y, angular_pos)
robot_initial_pos = (0, 0, 0)
robot_path = [robot_initial_pos]

robot_wheel_radius = 0.135
robot_track_width = 0.67
# Time interval between velocity measurements in seconds
robot_d_time = 23666397740 / 1000000000 / len(left_wheel_velocities)

left_wheel_velocities = [-x for x in left_wheel_velocities]
left_wheel_velocities = [x * robot_wheel_radius for x in left_wheel_velocities]
right_wheel_velocities = [x * robot_wheel_radius for x in right_wheel_velocities]

for i in range(0, len(left_wheel_velocities)):
    robot_path.append(get_new_position(robot_path[i], left_wheel_velocities[i], right_wheel_velocities[i], robot_track_width))
plot(robot_path)

robot_laser_data = get_laser_data("laser.txt")
robot_projected_laser_scans = project_laser_scans(robot_path, robot_laser_data)
plot_laser_scans(flatten(robot_projected_laser_scans))

combined_plot(robot_path, flatten(robot_projected_laser_scans))
