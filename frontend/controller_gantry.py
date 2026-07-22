from PyQt6.QtCore import QObject
from PyQt6.QtWidgets import QFileDialog, QInputDialog, QMessageBox, QDialog
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QVector3D
import os
import shutil
import json
from backend.comms import serialDevice
# from workers.runWorker import runWorker
# from backend.gcode_to_rapid import conversionHandler
# from backend.offsetAndRotate import transform
# from frontend.dialog_convertToRapid import GCodeDialog
# from frontend.dialog_transform import GetTransformationInformation
# import pyqtgraph.opengl as gl
import re
# import numpy as np
import time

LINE_COLOR = (1, 0.5, 0, 1) # orange
#LINE_COLOR = (0.75,0,0,1) # Cardinal

class gantryControl(QObject):

    def __init__(self,view,systemState,interfaceState,parent = None):
        super().__init__()
        self.comms = serialDevice()
        self.jog_speed = 0
        self.view = view
        self.jog_increment = 50
        self.systemState = systemState
        self.interfaceState = interfaceState
        self.PARENT_DIRECTORY = self.interfaceState.get_PARENT_DIRECTORY()
        self.rapid_path = None
        self.config_path = None
        self.gcode_path = None
        self.project = self.interfaceState.get_PROJECT()
        self.config_dict = None
        self.homed = False
        self.xlim = 300
        self.ylim = 275
        self.zlim = 216
        self.xSum = 0
        self.ySum = 0
        self.zSum = 0

        self.view.jogRequested.connect(self.jog)
        self.view.speedChanged.connect(self.set_jog_speed)
        self.view.jogChanged.connect(self.set_jog_increment)
        self.view.connectGantry.connect(self.retry_connection)
        self.view.allStopRequested.connect(self.allstop)
        self.view.setHomeRequested.connect(self.set_home)
        self.view.returnHomeRequested.connect(self.return_home)
        # self.view.load_gcode_clicked.connect(self.load_gcode)
        # self.view.validate_path_clicked.connect(self.validatePath)
        # self.view.load_rapid_clicked.connect(self.load_rapid)
        # self.view.transform_clicked.connect(self.transform_rapid)
        # self.view.run_clicked.connect(self.run)
        # self.populate_config_dropdown()


    def set_home(self):
        self.xSum = 0
        self.ySum = 0
        self.zSum = 0
        self.homed = True
        print("Gantry Home has been set.")

    def return_home(self):
        if self.homed:
            homing = ['X','Y','Z']
            dist = [self.xSum,self.ySum,self.zSum]
            old_speed = self.jog_speed
            self.set_jog_speed(15)
            for idx,axis in enumerate(homing):
                rsp = self.jog(axis,-1,dist[idx])
                print("[HOMING] " + rsp)
                complete = False
                while not complete:
                    rsp = self.jog(axis,-1,dist[idx])
                    if rsp is None:
                        return
                    if "Please Wait" in rsp:
                        time.sleep(0.5)
                        continue

                    complete = True
            self.set_jog_speed(old_speed)
        else:
            print("[ERROR] Cannot return to Home. Home is not set.")

    def retry_connection(self):
        self.view.connectionStatus.setText("Attempting to connect...")
        time.sleep(0.1)
        if self.comms.ser_con is None:
            self.comms = serialDevice()
            if self.comms.ser_con is None:
                self.view.connectionStatus.setText("Connection Failed.")
            else:
                self.view.connectionStatus.setText("Connected!")
                self.set_jog_speed(self.jog_speed)
        else:
            self.view.connectionStatus.setText("Connected!")
            self.set_jog_speed(self.jog_speed)
    
    def handle_disconnect(self):
        self.comms.ser_con = None
        self.view.connectionStatus.setText("Disconnected, try to connect again.")

    def send(self,msg):
        # sends messages and handles disconnects
        try:
            rsp = self.comms.sendAndReceive(msg)
            if rsp == False:
                self.handle_disconnect()
            else:
                print(rsp.strip('\n'))
                return rsp
        except Exception as e:
            self.handle_disconnect()
            print(f"[ERROR][GANTRYCONTROL][SEND] Something went wrong in sending. {e}")
    
    def set_jog_increment(self,inc):
        self.jog_increment = inc

    def set_jog_speed(self,speed):
        if self.comms.ser_con is None:
            print(f"[ERROR] Gantry is disconnected. Cannot set speed.")
        else:
            self.send("S"+str(speed))
            self.jog_speed = speed
    
    def jog(self,axis:str,direction:float, increment=None):
        if increment is None:
            increment = self.jog_increment

        if self.comms.ser_con is None:
            print(f"[ERROR] Gantry is disconnected. Cannot jog.")
            return "Disconnect"
        else:
            if self.homed:
                if axis == "X" and (0 <= (self.xSum+direction*increment) <= self.xlim):
                    rsp = self.send(axis+str(direction*increment))
                    if 'Please Wait' not in rsp:
                        self.xSum = self.xSum+direction*increment
                    return rsp
                    
                elif axis == "Y" and (0 <= (self.ySum+direction*increment) <= self.ylim):
                    rsp = self.send(axis+str(direction*increment))
                    if 'Please Wait' not in rsp:
                        self.ySum = self.ySum+direction*increment
                    return rsp
                    
                elif axis == "Z" and (0 <= (self.zSum+direction*increment) <= self.zlim):
                    old_speed = self.jog_speed
                    self.set_jog_speed(10) # prevents skipping
                    rsp = self.send(axis+str(direction*increment))
                    if 'Please Wait' not in rsp:
                        self.zSum = self.zSum+direction*increment
                    self.set_jog_speed(old_speed)
                    return rsp
                else:
                    print(f"[ERROR][JOG] Software imposed Jogging Limit Exceeded in {axis}.\n    X Limit: {self.xlim} Pos: {self.xSum}\n    Y Limit: {self.ylim} Pos: {self.ySum}\n    Z Limit: {self.zlim} Pos: {self.zSum}\n")
                    return "limit"
            else:
                rsp = self.send(axis+str(direction*increment))
                return rsp

    def allstop(self):
        if self.comms.ser_con is None:
            print(f"[ERROR] Gantry is disconnected. Cannot execute All Stop.")
        else:
            self.send("A")
            print("[ALL STOP] Home lost. Reset Home.")
            self.homed = False
    
    # def populate_config_dropdown(self):
    #     config_folder = os.path.join(self.PARENT_DIRECTORY, "saved_print_configs")
    #     if not os.path.exists(config_folder):
    #         config_names = []
    #     else:
    #         config_names = [f for f in os.listdir(config_folder) if f.endswith('.json')]
    #     # self.view.update_config_dropdown(config_names)

    # def load_selected_config(self):
    #     # selected_config = self.view.config_combo.currentText()
    #     if not selected_config:
    #         QMessageBox.warning(self.view, "No Selection", "Please select a configuration.")
    #         return

    #     src_path = os.path.join(self.PARENT_DIRECTORY, "saved_print_configs", selected_config)
    #     dst_folder = os.path.join(self.PARENT_DIRECTORY, "config")
    #     self.config_path = os.path.join(dst_folder, "config.json")

    #     if not os.path.exists(src_path):
    #         QMessageBox.critical(self.view, "Error", "Selected config file does not exist.")
    #         return

    #     os.makedirs(dst_folder, exist_ok=True)
    #     shutil.copyfile(src_path, self.config_path)
    #     print(f"{selected_config} loaded as config.json.")
    #     with open(src_path) as j:
    #         self.config_dict = json.load(j)
        
    #     self.updateBuildPlate()
    #     # self.view.buttonState_configLoaded()
        
    
    # def load_rapid(self):
    #     path, _ = QFileDialog.getOpenFileName(
    #         self.view, "Select Rapid File", "", "Rapid Files (*.txt);;All Files (*)"
    #     )
    #     print(path)
    #     if path != "":
    #         self.rapid_path = path
    #         self.project = os.path.basename(os.path.dirname(os.path.dirname(self.rapid_path)))
    #         self.interfaceState.set_PROJECT(self.project) # set the project to make it easier to access elsewhere
    #         print(f"Path Loaded, file selected: {os.path.basename(path)}")
    #         self.saveRapidFilePath()
    #         self.view.buttonState_confirmPath()
    #         self.displayToolpath(self.parse_rapid())
    #     else:
    #         self.view.buttonState_configLoaded()
    
    # def silent_load_rapid(self, path):
    #     # Silent method for loading rapid in the event that the rapid is modified by some other part of the program, e.g. if it's transformed, it should load in the transformed file
    #     print(path)
    #     if path != "":
    #         self.rapid_path = path
    #         self.project = os.path.basename(os.path.dirname(os.path.dirname(self.rapid_path)))
    #         self.interfaceState.set_PROJECT(self.project) # set the project to make it easier to access elsewhere
    #         print(f"Path Loaded, file selected: {os.path.basename(path)}")
    #         self.saveRapidFilePath()
    #         self.view.buttonState_confirmPath()
    #         self.displayToolpath(self.parse_rapid())
    #     else:
    #         self.view.buttonState_configLoaded()
    
    # def transform_rapid(self):
    #     dialog = GetTransformationInformation(self.view)
    #     if dialog.exec() == QDialog.DialogCode.Accepted:
    #         x_coord,y_coord,z_offset,rotation,pivot = dialog.get_values()
    #         new_path = transform(self.rapid_path,self.project,x_coord,y_coord,z_offset,rotation,pivot)
    #         self.silent_load_rapid(new_path)

    # def load_gcode(self):
    #     """ Loads gcode and conducts rapid conversion"""
    #     try:
    #         dialog = GCodeDialog()
    #         if dialog.exec() == QDialog.DialogCode.Accepted:
    #             self.tool = dialog.tool_dropdown.currentText()
    #             self.gcode_path = dialog.result_path
    #             result = conversionHandler(self.gcode_path,self.tool)
    #             self.rapid_path = result
    #             self.saveRapidFilePath()
    #             self.view.buttonState_confirmPath()
    #             self.displayToolpath(self.parse_rapid())
    #         else:
    #             print("Conversion Cancelled")
    #     except Exception as e:
    #         print(f"Unhandled Error: {e}")

    # def parse_rapid(self):
    #     """
    #     Parses a rapid file and extracts T MoveL and E MoveL commands into a list.
    #     Each entry will be in the format: ["T" or "E", [x, y, z]].
    #     """
    #     results = []
    #     # Regex to match lines like 'E MoveL [[-109.0302,-20.4172,0.55], ...'
    #     pattern = re.compile(r'^(T|E)\s+MoveL\s+\[\[([-\d\.]+),([-\d\.]+),([-\d\.]+)\]')

    #     with open(self.rapid_path, 'r') as file:
    #         for line in file:
    #             line = line.strip()
    #             match = pattern.match(line)
    #             if match:
    #                 move_type = match.group(1)  # "T" or "E"
    #                 x, y, z = map(float, match.groups()[1:4])  # Convert to floats
    #                 results.append([move_type, [x, y, z]])
    #     return results

    # def saveRapidFilePath(self):
    #     try:
    #         with open(self.config_path,"r") as f:
    #             temp = json.load(f)
    #             temp["PublisherCommandFile"]["file_path"] = self.rapid_path

    #         with open(self.config_path, "w") as f:
    #             json.dump(temp, f, indent=2)
    #             # force os to clear cache and sync file, should fix a weird memory error.
    #             f.flush()
    #             os.fsync(f.fileno())

    #         print("Updated Config")
    #     except Exception as e:
    #         print(f"ERROR: {e}")
    
    # def handleRunResult(self):
    #     print("Run Complete!")
    #     self.view.buttonState_readyToRun()

    # def run(self):
    #     print("Run Started")
    #     self.view.buttonState_running()
    #     self.thread = QThread()
    #     self.worker = runWorker()
    #     self.worker.moveToThread(self.thread)
    #     self.thread.started.connect(self.worker.run)  # Start worker when thread starts
    #     self.worker.finished.connect(self.handleRunResult)
    #     self.worker.finished.connect(self.thread.quit)
    #     self.worker.finished.connect(self.worker.deleteLater)
    #     self.thread.finished.connect(self.thread.deleteLater)
    #     self.thread.start()
    #     print(self.thread)
    #     # self.view.runSystemStarted.emit()

    # def displayToolpath(self, points):
    #     """
    #     Plot a 3D toolpath using pyqtgraph.

    #     Args:
    #         points (list): A list of toolpath points in the form:
    #                     [["MOVETYPE", [x, y, z]], ...]
    #                     MOVETYPE is either "T" (travel) or "E" (extrusion).
    #     """
    #     import numpy as np
    #     import pyqtgraph.opengl as gl

    #     # 1. Clear previous toolpath lines while keeping the grid
    #     for item in self.view.toolpath_view.items[:]:
    #         if not isinstance(item, gl.GLGridItem):  # Preserve only the grid
    #             self.view.toolpath_view.removeItem(item)

    #     if not points:
    #         return  # Nothing to plot


    #     # 2. Prepare groups to separate travel (T) and extrusion (E)
    #     # Each "group" represents a continuous connected segment.
    #     e_point_group = []   # Active extrusion segment being built
    #     e_groups = []        # List of completed extrusion segments
    #     t_point_group = []   # Active travel segment being built
    #     t_groups = []        # List of completed travel segments

    #     last_coords = None
    #     last_move_type = None

    #     # 3. Iterate through all points and group them
    #     for move_type, coords in points:
    #         if move_type == "E":
    #             # Starting a new extrusion after a travel move
    #             if last_move_type == "T" and last_coords is not None:
    #                 # Close out the current travel group
    #                 t_groups.append(t_point_group)
    #                 t_point_group = []

    #                 # Add the last travel point to extrusion group
    #                 # so that the transition is visually connected
    #                 e_point_group.append(last_coords)

    #             # Add this point to the current extrusion segment
    #             e_point_group.append(coords)

    #         else:  # "T" move
    #             # Starting a new travel segment after extrusion
    #             if last_move_type == "E" and last_coords is not None:
    #                 # Close out the current extrusion group
    #                 e_groups.append(e_point_group)
    #                 e_point_group = []

    #                 # Add the last extrusion point to travel group
    #                 t_point_group.append(last_coords)

    #             # Add this point to the current travel segment
    #             t_point_group.append(coords)

    #         # Update trackers
    #         last_move_type = move_type
    #         last_coords = coords

    #     # 4. Add any leftover points to their respective group lists
    #     if t_point_group:
    #         t_groups.append(t_point_group)
    #     if e_point_group:
    #         e_groups.append(e_point_group)


    #     # 5. Draw extrusion paths
    #     for e_points in e_groups:
    #         if len(e_points) > 1:  # Only draw if at least 2 points
    #             e_pos = np.array(e_points, dtype=float)
    #             e_line = gl.GLLinePlotItem(
    #                 pos=e_pos,
    #                 color=LINE_COLOR,
    #                 width=2,
    #                 antialias=True,
    #                 mode='line_strip'
    #             )
    #             self.view.toolpath_view.addItem(e_line)


    #     # 6. Draw travel paths
    #     for t_points in t_groups:
    #         if len(t_points) > 1:  # Only draw if at least 2 points
    #             t_pos = np.array(t_points, dtype=float)
    #             t_line = gl.GLLinePlotItem(
    #                 pos=t_pos,
    #                 color=(0.25, 0.25, 0.25, 1),  # Gray for travel
    #                 width=2,
    #                 antialias=True,
    #                 mode='line_strip'
    #             )
    #             self.view.toolpath_view.addItem(t_line)
    
    # def validatePath(self):
    #     self.view.buttonState_readyToRun()

    # def updateBuildPlate(self):
    #     self.view.toolpath_view.removeItem(self.view.grid)
    #     self.view.grid = gl.GLGridItem()
    #     self.view.toolpath_view.addItem(self.view.grid)
    #     self.view.grid.setSpacing(10, 10)
    #     self.view.grid.setSize(self.config_dict["Build Area"]["X"],self.config_dict["Build Area"]["Y"])
    #     try:
    #         if self.config_dict["Center Type"]["Center on X AND Y"]:
    #             self.view.grid.translate(self.config_dict["Build Area"]["X"]/2,self.config_dict["Build Area"]["Y"]/2,0)
    #         elif self.config_dict["Center Type"]["Center on X"]:
    #             self.view.grid.translate(self.config_dict["Build Area"]["X"]/2,0,0)
    #         elif self.config_dict["Center Type"]["Center on Y"]:
    #             self.view.grid.translate(0,self.config_dict["Build Area"]["Y"]/2,0)
    #         #self.view.toolpath_view.setCameraPosition(pos=QVector3D(self.config_dict["Build Area"]["X"],self.config_dict["Build Area"]["Y"],600),elevation=45,azimuth=45)
    #         #self.view.toolpath_view.setCameraPosition(distance=self.config_dict["Build Area"]["Y"]*2)
    #     except Exception as e:
    #         print(f"Controller Error: {e}")