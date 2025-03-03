import tkinter as tk
from tkinter import ttk, messagebox
import serial
import serial.tools.list_ports


# 串口通信类
class SerialController:
    def __init__(self):
        self.ser = serial.Serial()
        self.ser.timeout = 1

    def open_serial(self, port, baudrate):
        if not self.ser.is_open:
            self.ser.port = port
            self.ser.baudrate = baudrate
            try:
                self.ser.open()
                return True
            except Exception as e:
                messagebox.showerror("错误", f"无法打开串口: {e}")
                return False
        return False

    def close_serial(self):
        if self.ser.is_open:
            self.ser.close()
            return True
        return False

    def send_command(self, command):
        if self.ser.is_open:
            try:
                self.ser.write(command.encode())
                return True
            except Exception as e:
                messagebox.showerror("错误", f"发送指令失败: {e}")
                return False
        return False


# 主窗口类
class RobotControlApp:
    def __init__(self, root):
        self.root = root
        self.root.title("机械臂控制程序")
        self.root.geometry("800x800")

        # 串口控制器
        self.serial_controller = SerialController()
        self.default_port = "/dev/ttyUSB0"
        self.speed = 100  # 默认速度值

        # 串口选择和控制
        self.create_serial_control_frame()

        # 复位与急停
        self.create_stop_frame()

        # 坐标控制区
        self.create_posctrl_frame()

        # 吸嘴控制
        self.create_suction_frame()

        # 速度设置区
        self.create_speed_frame()

    def create_serial_control_frame(self):
        frame = ttk.LabelFrame(self.root, text="串口控制")
        frame.pack(pady=10, padx=10, fill="x")

        # 串口选择
        port_label = ttk.Label(frame, text="串口：")
        port_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.port_combo = ttk.Combobox(frame, values=self.get_serial_ports())
        self.port_combo.set(self.default_port)  # 设置默认串口
        self.port_combo.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # 波特率输入
        baudrate_label = ttk.Label(frame, text="波特率：")
        baudrate_label.grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.baudrate_entry = ttk.Entry(frame, width=10)
        self.baudrate_entry.insert(0, "115200")  # 默认波特率
        self.baudrate_entry.grid(row=0, column=3, padx=5, pady=5, sticky="w")

        # 打开和关闭串口按钮
        open_btn = ttk.Button(frame, text="打开串口", command=self.open_serial)
        open_btn.grid(row=0, column=4, padx=5, pady=5)
        close_btn = ttk.Button(frame, text="关闭串口", command=self.close_serial)
        close_btn.grid(row=0, column=5, padx=5, pady=5)

        # 手动发送命令
        command_label = ttk.Label(frame, text="命令：")
        command_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.command_entry = ttk.Entry(frame, width=40)
        self.command_entry.grid(
            row=1, column=1, columnspan=3, padx=5, pady=5, sticky="w"
        )
        send_command_btn = ttk.Button(
            frame, text="发送命令", command=self.send_custom_command
        )
        send_command_btn.grid(row=1, column=4, padx=5, pady=5)
        # send_command_btn = ttk.Button(
        #     frame, text="一键复位", command=self.send_reset_command
        # )
        # send_command_btn.grid(row=1, column=5, padx=5, pady=5)

        # 串口通信信息显示框
        self.serial_info_text = tk.Text(frame, height=5, width=50)
        self.serial_info_text.grid(
            row=2, column=0, columnspan=6, padx=5, pady=5, sticky="nsew"
        )
        self.serial_info_text.configure(state="disabled")

    def get_serial_ports(self):
        ports = [port.device for port in serial.tools.list_ports.comports()]
        return ports

    def open_serial(self):
        port = self.port_combo.get()
        baudrate = self.baudrate_entry.get()
        if port and baudrate:
            try:
                baudrate = int(baudrate)
                if self.serial_controller.open_serial(port, baudrate):
                    self.update_serial_info("串口已打开")
                else:
                    self.update_serial_info("串口打开失败")
            except ValueError:
                self.update_serial_info("波特率必须是整数")
        else:
            self.update_serial_info("请选择串口和波特率")

    def close_serial(self):
        if self.serial_controller.close_serial():
            self.update_serial_info("串口已关闭")

    def update_serial_info(self, message):
        self.serial_info_text.configure(state="normal")
        self.serial_info_text.insert(tk.END, message + "\n")
        self.serial_info_text.configure(state="disabled")
        self.serial_info_text.see(tk.END)  # 自动滚动到最后一行

    def send_custom_command(self):
        command = self.command_entry.get()
        if command:
            if self.serial_controller.send_command(command + "\n"):
                self.update_serial_info(f"发送成功: {command}")
            else:
                self.update_serial_info(f"发送失败: {command}")
        else:
            self.update_serial_info("请输入命令")

    def create_stop_frame(self):
        frame = ttk.LabelFrame(self.root, text="复位与急停")
        frame.pack(pady=10, padx=10, fill="x")

        open_btn = ttk.Button(frame, text="复位", command=self.send_reset_command)
        open_btn.grid(row=0, column=0, padx=5, pady=5)
        close_btn = ttk.Button(frame, text="急停", command=self.send_stop_command)
        close_btn.grid(row=0, column=1, padx=5, pady=5)

    def send_reset_command(self):
        command = f"Origin_{self.speed}"
        if self.serial_controller.send_command(command + "\n"):
            self.update_serial_info(f"复位成功，速度: {self.speed}")
        else:
            self.update_serial_info(f"复位失败")

    def send_stop_command(self):
        command = "Stop\n"
        if self.serial_controller.send_command(command):
            self.update_serial_info(f"发送成功: {command.strip()}")
        else:
            self.update_serial_info(f"发送失败: {command.strip()}")

    def create_posctrl_frame(self):
        frame = ttk.LabelFrame(self.root, text="坐标发送")
        frame.pack(pady=10, padx=10, fill="x")

        # 关节坐标
        self.joint_x = ttk.Entry(frame, width=10)
        self.joint_x.grid(row=0, column=1, padx=5, pady=5)
        self.joint_y = ttk.Entry(frame, width=10)
        self.joint_y.grid(row=0, column=2, padx=5, pady=5)
        self.joint_z = ttk.Entry(frame, width=10)
        self.joint_z.grid(row=0, column=3, padx=5, pady=5)
        joint_btn = ttk.Button(frame, text="发送关节坐标", command=self.send_joint_data)
        joint_btn.grid(row=0, column=4, padx=5, pady=5)

        # 关节偏移
        self.joint_offset_x = ttk.Entry(frame, width=10)
        self.joint_offset_x.grid(row=1, column=1, padx=5, pady=5)
        self.joint_offset_y = ttk.Entry(frame, width=10)
        self.joint_offset_y.grid(row=1, column=2, padx=5, pady=5)
        self.joint_offset_z = ttk.Entry(frame, width=10)
        self.joint_offset_z.grid(row=1, column=3, padx=5, pady=5)
        joint_offset_btn = ttk.Button(
            frame, text="发送关节偏移", command=self.send_joint_offset_data
        )
        joint_offset_btn.grid(row=1, column=4, padx=5, pady=5)

        # 世界坐标
        self.world_x = ttk.Entry(frame, width=10)
        self.world_x.grid(row=2, column=1, padx=5, pady=5)
        self.world_y = ttk.Entry(frame, width=10)
        self.world_y.grid(row=2, column=2, padx=5, pady=5)
        self.world_z = ttk.Entry(frame, width=10)
        self.world_z.grid(row=2, column=3, padx=5, pady=5)
        world_btn = ttk.Button(frame, text="发送世界坐标", command=self.send_world_data)
        world_btn.grid(row=2, column=4, padx=5, pady=5)

        # 世界偏移
        self.world_offset_x = ttk.Entry(frame, width=10)
        self.world_offset_x.grid(row=3, column=1, padx=5, pady=5)
        self.world_offset_y = ttk.Entry(frame, width=10)
        self.world_offset_y.grid(row=3, column=2, padx=5, pady=5)
        self.world_offset_z = ttk.Entry(frame, width=10)
        self.world_offset_z.grid(row=3, column=3, padx=5, pady=5)
        world_offset_btn = ttk.Button(
            frame, text="发送世界偏移", command=self.send_world_offset_data
        )
        world_offset_btn.grid(row=3, column=4, padx=5, pady=5)

        # 直线运动
        self.line_x = ttk.Entry(frame, width=10)
        self.line_x.grid(row=4, column=1, padx=5, pady=5)
        self.line_y = ttk.Entry(frame, width=10)
        self.line_y.grid(row=4, column=2, padx=5, pady=5)
        self.line_z = ttk.Entry(frame, width=10)
        self.line_z.grid(row=4, column=3, padx=5, pady=5)
        line_btn = ttk.Button(frame, text="发送直线运动", command=self.send_line_data)
        line_btn.grid(row=4, column=4, padx=5, pady=5)

        # 直线偏移
        self.line_offset_x = ttk.Entry(frame, width=10)
        self.line_offset_x.grid(row=5, column=1, padx=5, pady=5)
        self.line_offset_y = ttk.Entry(frame, width=10)
        self.line_offset_y.grid(row=5, column=2, padx=5, pady=5)
        self.line_offset_z = ttk.Entry(frame, width=10)
        self.line_offset_z.grid(row=5, column=3, padx=5, pady=5)
        line_offset_btn = ttk.Button(
            frame, text="发送直线偏移", command=self.send_line_offset_data
        )
        line_offset_btn.grid(row=5, column=4, padx=5, pady=5)

    def send_joint_data(self):
        x = self.joint_x.get()
        y = self.joint_y.get()
        z = self.joint_z.get()
        command = f"JointAngle_{x},{y},{z},{self.speed}\n"
        if self.serial_controller.send_command(command):
            self.update_serial_info(f"发送成功: {command.strip()}")
        else:
            self.update_serial_info(f"发送失败: {command.strip()}")

    def send_joint_offset_data(self):
        x = self.joint_offset_x.get()
        y = self.joint_offset_y.get()
        z = self.joint_offset_z.get()
        command = f"JointAngleOffset_{x},{y},{z},{self.speed}\n"
        if self.serial_controller.send_command(command):
            self.update_serial_info(f"发送成功: {command.strip()}")
        else:
            self.update_serial_info(f"发送失败: {command.strip()}")

    def send_world_data(self):
        x = self.world_x.get()
        y = self.world_y.get()
        z = self.world_z.get()
        command = f"DescartesPoint_{x},{y},{z},{self.speed}\n"
        if self.serial_controller.send_command(command):
            self.update_serial_info(f"发送成功: {command.strip()}")
        else:
            self.update_serial_info(f"发送失败: {command.strip()}")

    def send_world_offset_data(self):
        x = self.world_offset_x.get()
        y = self.world_offset_y.get()
        z = self.world_offset_z.get()
        command = f"DescartesPointOffset_{x},{y},{z},{self.speed},50\n"
        if self.serial_controller.send_command(command):
            self.update_serial_info(f"发送成功: {command.strip()}")
        else:
            self.update_serial_info(f"发送失败: {command.strip()}")

    def send_line_data(self):
        x = self.line_x.get()
        y = self.line_y.get()
        z = self.line_z.get()
        command = f"DescartesLine_{x},{y},{z},{self.speed}\n"
        if self.serial_controller.send_command(command):
            self.update_serial_info(f"发送成功: {command.strip()}")
        else:
            self.update_serial_info(f"发送失败: {command.strip()}")

    def send_line_offset_data(self):
        x = self.line_offset_x.get()
        y = self.line_offset_y.get()
        z = self.line_offset_z.get()
        command = f"DescartesLinearOffset_{x},{y},{z},{self.speed}\n"
        if self.serial_controller.send_command(command):
            self.update_serial_info(f"发送成功: {command.strip()}")
        else:
            self.update_serial_info(f"发送失败: {command.strip()}")

    def create_suction_frame(self):
        frame = ttk.LabelFrame(self.root, text="吸嘴控制")
        frame.pack(pady=10, padx=10, fill="x")

        # 吸嘴打开和关闭
        open_btn = ttk.Button(frame, text="打开吸嘴", command=self.open_suction)
        open_btn.grid(row=0, column=0, padx=5, pady=5)
        close_btn = ttk.Button(frame, text="关闭吸嘴", command=self.close_suction)
        close_btn.grid(row=0, column=1, padx=5, pady=5)

    def open_suction(self):
        command = "Suction_1\n"
        if self.serial_controller.send_command(command):
            self.update_serial_info(f"发送成功: {command.strip()}")
        else:
            self.update_serial_info(f"发送失败: {command.strip()}")

    def close_suction(self):
        command = "Suction_0\n"
        if self.serial_controller.send_command(command):
            self.update_serial_info(f"发送成功: {command.strip()}")
        else:
            self.update_serial_info(f"发送失败: {command.strip()}")

    def create_speed_frame(self):
        frame = ttk.LabelFrame(self.root, text="参数设置")
        frame.pack(pady=10, padx=10, fill="x")

        # 速度输入
        speed_label = ttk.Label(frame, text="速度：")
        speed_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.speed_entry = ttk.Entry(frame, width=10)
        self.speed_entry.insert(0, str(self.speed))  # 默认速度
        self.speed_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # 设置速度按钮
        set_speed_btn = ttk.Button(frame, text="设置速度", command=self.set_speed)
        set_speed_btn.grid(row=0, column=2, padx=5, pady=5)

    def set_speed(self):
        try:
            new_speed = int(self.speed_entry.get())
            if new_speed < 0:
                raise ValueError
            self.speed = new_speed
            command = f"Speed_{self.speed}"
            if self.serial_controller.send_command(command):
                self.update_serial_info(f"发送成功: {command.strip()}")
            else:
                self.update_serial_info(f"发送失败: {command.strip()}")
        except ValueError:
            self.update_serial_info("请输入有效的整数速度值")


# 主程序
if __name__ == "__main__":
    root = tk.Tk()
    app = RobotControlApp(root)
    root.mainloop()
