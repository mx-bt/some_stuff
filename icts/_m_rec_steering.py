import socket
from robomaster import robot

# dh2   192.168.50.206
# ip    192.168.50.3

robots_ = ["3JKCK7W0030DCD", "3JKCK7W0030CS5", "3JKCK7W0030DFA"] # Javier, , Stormtrooper, NoName
def main():
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="sta", sn=robots_[1])
    ep_version = ep_robot.get_version()
    print(f"Robot Version {ep_version}")

    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('0.0.0.0', 12345))
                s.listen()
                # print(f"Waiting for incoming connections on port {port}...")
                conn, addr = s.accept()
                with conn:
                    # print(f"Connected by {addr}")
                    data = conn.recv(1024).decode('utf-8').split() 
                xyz = tuple(round(float(num), 2) for num in data)
                ep_robot.chassis.drive_speed(x=xyz[0],y=xyz[1],z=xyz[2],timeout=0)
                print(f"Command from {addr}: {xyz}")

        except KeyboardInterrupt:
            ep_robot.close()
            break


if __name__ == "__main__":
    main()