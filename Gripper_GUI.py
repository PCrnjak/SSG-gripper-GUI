import customtkinter
import platform
import os
import logging
from tkinter.messagebox import showinfo
from math import pi
import time
import threading
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
import tkinter as tk
#import Spectral_BLDC2 as Spectral
import Spectral_BLDC as Spectral

Communication1 = Spectral.CanCommunication(bustype='slcan', channel=None, bitrate=1000000)
Motor1 = Spectral.SpectralCAN(node_id=0, communication=None)

logging.basicConfig(level = logging.DEBUG,
    format='%(asctime)s.%(msecs)03d %(levelname)s:\t%(message)s',
    datefmt='%H:%M:%S'
)
logging.disable(logging.DEBUG)


# Finds out where the program and images are stored
my_os = platform.system()
if my_os == "Windows":
    Image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)))
    logging.debug("Os is Windows")
else:
    Image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)))
    logging.debug("Os is Linux")
    
logging.debug(Image_path)

text_size = 14

customtkinter.set_appearance_mode("Light")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

data_2_send = "Gripper data"
Connected = 0
Position_send = 0
Speed_send = 0
Current_send = 0

Activate_send = 0
Action_send = 0

Estop_send = 0
Release_dir_send = 0

prev_Position_send = 0
prev_Speed_send = 0
prev_Current_send = 0

prev_Activate_send = 0
prev_Action_send = 0

prev_Estop_send = 0
prev_Release_dir_send = 0

Clear_send = 0
Calibrate_send = 0

update_tick = 0

# Avg 65 FPS = 0.015s
# We have 100 samples * 0.015s = 1.5s, x scale goes from 0 to 1.5 seconds
x_len = 300
x = np.linspace(0, 4.5, 300)
ys1 = [0] * x_len
ys2 = [0] * x_len

def animate_sine_wave(i, line1, x):
    global frame_count
    global ys1
    frame_count += 1
    ys1.append(Motor1.gripper_position)
    ys1 = ys1[-x_len:]
    line1.set_ydata(ys1)
    return line1,

def animate_square_wave(i, line2, x):
    global ys2
    ys2.append(Motor1.gripper_current)
    ys2 = ys2[-x_len:]
    line2.set_ydata(ys2)
    return line2,


def GUI(var):
        
    global start_time, frame_count
    global x

    start_time = time.time()
    
    frame_count = 0
    app = customtkinter.CTk()

        # configure window
    app.title("Gripper controller.py")
    app.geometry(f"{1200}x{600}")
    app.attributes('-topmost',False)

    # Add app icon
    #logo = (os.path.join(Image_path, "logo.ico"))
    #app.iconbitmap(logo)

    # configure grid layout (4x4) wight 0 znači da je fixed, 1 znači da scale radi?
    app.grid_columnconfigure((1,2), weight=1)
    app.grid_columnconfigure((0), weight=1)
    app.grid_rowconfigure((0), weight=0)
    app.grid_rowconfigure((1), weight=0)
    app.grid_rowconfigure((2), weight=1)
    app.grid_rowconfigure((3), weight=0) 

    fig = plt.figure(figsize=(20, 12))

    #fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(70, 60))  # 3 rows, 1 column


    # Subplot 1: motor position Sine wave
    ax1 = fig.add_subplot(121)
    y_range = [0, 255] # What range to show on Y axis
    ax1.set_ylim(y_range)

    line1, = ax1.plot(x, np.sin(x))
    ax1.set_title("Position [Ticks]")
    ax1.grid(True)
    #ax.set_facecolor(np.random.rand(3,))

    # Subplot 2: motor speed Square wave
    ax2 = fig.add_subplot(122)
    y_range = [-1300, 1300] # What range to show on Y axis
    ax2.set_ylim(y_range)
    line2, = ax2.plot(x, np.sign(np.sin(2 * np.pi * x)))
    ax2.set_title("Current [mA]")
    ax2.grid(True)



    def Top_frame():
            Top_frame = customtkinter.CTkFrame(app ,height = 0,width=150, corner_radius=0, )
            Top_frame.grid(row=0, column=0, columnspan=4, padx=(5,5), pady=(5,5),sticky="new")
            Top_frame.grid_columnconfigure(0, weight=0)
            Top_frame.grid_rowconfigure(0, weight=0)

        
            Calibrate_button = customtkinter.CTkButton( Top_frame,text="Calibrate", width= 50, font = customtkinter.CTkFont(size=15, family='TkDefaultFont'),command = Calibrate_call)
            Calibrate_button.grid(row=0, column=0, padx=20,pady = (5,5),sticky="news")

            app.Activate_button = customtkinter.CTkButton( Top_frame,text="Activate", width= 50, font = customtkinter.CTkFont(size=15, family='TkDefaultFont'),command=Activate_call)
            app.Activate_button.grid(row=0, column=1, padx=20,pady = (5,5),sticky="news")

            Estop_button = customtkinter.CTkButton( Top_frame,text="Estop", width= 50, font = customtkinter.CTkFont(size=15, family='TkDefaultFont'),command=Estop_call)
            Estop_button.grid(row=0, column=2, padx=20,pady = (5,5),sticky="news")

            Clear_error_button = customtkinter.CTkButton( Top_frame,text="Clear", width= 50, font = customtkinter.CTkFont(size=15, family='TkDefaultFont'),command=Clear_error)
            Clear_error_button.grid(row=0, column=3, padx=20,pady = (5,5),sticky="news")

            CAN_id = customtkinter.CTkLabel( Top_frame, text="CAN ID", anchor="e")
            CAN_id.grid(row=0, column=4, padx=(5, 0))

            app.CAN_id_entry = customtkinter.CTkEntry( Top_frame, width= 100)
            app.CAN_id_entry.grid(row=0, column=5, padx=(5, 0),pady=(3,3))

            COM_port = customtkinter.CTkLabel( Top_frame, text="COM port", anchor="e")
            COM_port.grid(row=0, column=6, padx=(5, 0))

            app.COM_port_entry = customtkinter.CTkEntry( Top_frame, width= 100)
            app.COM_port_entry.grid(row=0, column=7, padx=(5, 0),pady=(3,3))

            Connect_button = customtkinter.CTkButton( Top_frame,text="Connect", width= 50, font = customtkinter.CTkFont(size=15, family='TkDefaultFont'),command= Connect_call)
            Connect_button.grid(row=0, column=8, padx=20,pady = (5,5),sticky="news")

            app.Object_detection = customtkinter.CTkLabel( Top_frame, text="Object detection: ", anchor="e")
            app.Object_detection.grid(row=0, column=9, padx=(5, 0))

            app.CAN_id_entry.insert(0,"0")
            app.COM_port_entry.insert(0,"COM41")



    def Commands_frame1():
            Commands_frame1 = customtkinter.CTkFrame(app ,height = 0,width=150, corner_radius=0, )
            Commands_frame1.grid(row=1, column=0, columnspan=1, padx=(5,5), pady=(5,5),sticky="news")
            Commands_frame1.grid_columnconfigure(0, weight=0)
            Commands_frame1.grid_rowconfigure(0, weight=0)

            appearance_mode_label = customtkinter.CTkLabel( Commands_frame1, text="Gripper commands", anchor="e")
            appearance_mode_label.grid(row=0, column=0, padx=(5, 0))

            Position_label = customtkinter.CTkLabel( Commands_frame1, text="Position", anchor="e")
            Position_label.grid(row=1, column=0, padx=(5, 0))

            Speed_label = customtkinter.CTkLabel( Commands_frame1, text="Speed", anchor="e")
            Speed_label.grid(row=2, column=0, padx=(5, 0))

            Current_label = customtkinter.CTkLabel( Commands_frame1, text="Current", anchor="e")
            Current_label.grid(row=3, column=0, padx=(5, 0))

            app.Position_slider = customtkinter.CTkSlider( Commands_frame1,width= 300,from_ = 0, to = 255,number_of_steps=255)
            app.Position_slider.grid(row=1, column=1,columnspan=1, padx=(0, 0), pady=(5, 5), sticky="news")
            app.Position_slider.set(100)

            app.Speed_slider = customtkinter.CTkSlider( Commands_frame1,width= 300,from_ = 0, to = 255,number_of_steps=255)
            app.Speed_slider.grid(row=2, column=1,columnspan=1, padx=(0, 0), pady=(5, 5), sticky="news")
            app.Speed_slider.set(30)

            app.Current_slider = customtkinter.CTkSlider( Commands_frame1,width= 300,from_ = 0, to = 1500,number_of_steps=1500)
            app.Current_slider.grid(row=3, column=1,columnspan=1, padx=(0, 0), pady=(5, 5), sticky="news")
            app.Current_slider.set(300)

            app.Position_entry = customtkinter.CTkEntry( Commands_frame1, width= 100)
            app.Position_entry.grid(row=1, column=2, padx=(5, 0),pady=(3,3))

            app.Speed_entry = customtkinter.CTkEntry( Commands_frame1, width= 100)
            app.Speed_entry.grid(row=2, column=2, padx=(5, 0),pady=(3,3))

            app.Current_entry = customtkinter.CTkEntry( Commands_frame1, width= 100)
            app.Current_entry.grid(row=3, column=2, padx=(5, 0),pady=(3,3))
        
            app.Position_numbers = customtkinter.CTkLabel( Commands_frame1, text="1000", anchor="e")
            app.Position_numbers.grid(row=1, column=3, padx=(5, 0))

            app.Speed_numbers = customtkinter.CTkLabel( Commands_frame1, text="1000", anchor="e")
            app.Speed_numbers.grid(row=2, column=3, padx=(5, 0))

            app.Current_numbers = customtkinter.CTkLabel( Commands_frame1, text="1000", anchor="e")
            app.Current_numbers.grid(row=3, column=3, padx=(5, 0))

            Set_position = customtkinter.CTkButton( Commands_frame1,text="Set", width= 50, font = customtkinter.CTkFont(size=15, family='TkDefaultFont'),command = Set_position_command)
            Set_position.grid(row=1, column=4, padx=20,pady = (5,5),sticky="news")

            Set_speed = customtkinter.CTkButton( Commands_frame1,text="Set", width= 50, font = customtkinter.CTkFont(size=15, family='TkDefaultFont'),command = Set_speed_command)
            Set_speed.grid(row=2, column=4, padx=20,pady = (5,5),sticky="news")

            Set_current = customtkinter.CTkButton( Commands_frame1,text="Set", width= 50, font = customtkinter.CTkFont(size=15, family='TkDefaultFont'),command = Set_current_command)
            Set_current.grid(row=3, column=4, padx=20,pady = (5,5),sticky="news")


    def Commands_frame2():
            Commands_frame2 = customtkinter.CTkFrame(app ,height = 0,width=150, corner_radius=0, )
            Commands_frame2.grid(row=1, column=1, columnspan=1, padx=(5,5), pady=(5,5),sticky="news")
            Commands_frame2.grid_columnconfigure(0, weight=0)
            Commands_frame2.grid_rowconfigure(0, weight=0)

            appearance_mode_label = customtkinter.CTkLabel( Commands_frame2, text="Gripper status", anchor="e")
            appearance_mode_label.grid(row=0, column=0, padx=(5, 0))

            app.Calib_status = customtkinter.CTkLabel( Commands_frame2, text="Not calibrated", anchor="e")
            app.Calib_status.grid(row=1, column=0, padx=(5, 0))

            app.Activation_status = customtkinter.CTkLabel( Commands_frame2, text="Not activated", anchor="e")
            app.Activation_status.grid(row=2, column=0, padx=(5, 0))

            app.Active_error = customtkinter.CTkLabel( Commands_frame2, text="No error", anchor="e")
            app.Active_error.grid(row=3, column=0, padx=(5, 0))

            app.Specific_error = customtkinter.CTkLabel( Commands_frame2, text="Temperature_error", anchor="e")
            app.Specific_error.grid(row=4, column=0, padx=(5, 0))


    def Commands_frame3():
            Commands_frame3 = customtkinter.CTkFrame(app ,height = 0,width=150, corner_radius=0, )
            Commands_frame3.grid(row=1, column=2, columnspan=1, padx=(5,5), pady=(5,5),sticky="news")
            Commands_frame3.grid_columnconfigure(0, weight=0)
            Commands_frame3.grid_rowconfigure(0, weight=0)

            appearance_mode_label = customtkinter.CTkLabel( Commands_frame3, text="Gripper feedback" , anchor="e")
            appearance_mode_label.grid(row=0, column=0, padx=(5, 0))

            app.Pos_feedback = customtkinter.CTkLabel( Commands_frame3, text="Position: ", anchor="e")
            app.Pos_feedback.grid(row=1, column=0, padx=(5, 0))

            app.Current_feedback = customtkinter.CTkLabel( Commands_frame3, text="Current: ", anchor="e")
            app.Current_feedback.grid(row=2, column=0, padx=(5, 0))

            #app.Object_detection = customtkinter.CTkLabel( Commands_frame3, text="Object detection: ", anchor="e")
            #app.Object_detection.grid(row=3, column=0, padx=(5, 0))




    Plots_frame = customtkinter.CTkFrame(app ,height = 0,width=150, corner_radius=0, )
    Plots_frame.grid(row=2, column=0, columnspan=4, padx=(5,5), pady=(5,5),sticky="news")
    Plots_frame.grid_columnconfigure(0, weight=1)
    Plots_frame.grid_rowconfigure(0, weight=1)

    appearance_mode_label = customtkinter.CTkLabel( Plots_frame, text="Top frame stuff", anchor="w")
    appearance_mode_label.grid(row=0, column=0, padx=(5, 0))

    canvas = FigureCanvasTkAgg(fig, master=Plots_frame)
    canvas.draw()
    canvas.get_tk_widget().grid(row=0, column=0, padx=(5, 0))


    def change_scaling_event(app, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    def change_appearance_mode_event(app, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def Bottom_frame():
            Bottom_frame = customtkinter.CTkFrame(app ,height = 0,width=150, corner_radius=0, )
            Bottom_frame.grid(row=3, column=0, columnspan=4, padx=(5,5), pady=(5,5),sticky="new")
            Bottom_frame.grid_columnconfigure(0, weight=0)
            Bottom_frame.grid_rowconfigure(0, weight=0)

            appearance_mode_label = customtkinter.CTkLabel( Bottom_frame, text="Appearance Mode:", anchor="w")
            appearance_mode_label.grid(row=0, column=0, padx=(5, 0))
            appearance_mode_optionemenu = customtkinter.CTkOptionMenu( Bottom_frame, values= ["Light","Dark"],
                                                                    command= change_appearance_mode_event)
            appearance_mode_optionemenu.grid(row=0, column=0, padx=(5, 0))

            app.FPS_label = customtkinter.CTkLabel( Bottom_frame, text="FPS ", anchor="e")
            app.FPS_label.grid(row=0, column=1, padx=(50, 50))

    def settings_frame():
            demo1 = customtkinter.CTkButton( settings_frame,text="demo1", font = customtkinter.CTkFont(size=15, family='TkDefaultFont'))
            demo1.grid(row=0, column=0, padx=20,pady = (10,20),sticky="news")

            scaling_label = customtkinter.CTkLabel( settings_frame, text="UI Scaling:", anchor="w")
            scaling_label.grid(row=0, column=1, padx=(5, 0))

            scaling_optionemenu = customtkinter.CTkOptionMenu( settings_frame, values=["80%", "90%", "100%", "110%", "120%","150%"],
                                                            command= change_scaling_event)
            scaling_optionemenu.grid(row=0, column=2,padx=(5, 0) )

            appearance_mode_label = customtkinter.CTkLabel( settings_frame, text="Appearance Mode:", anchor="w")
            appearance_mode_label.grid(row=0, column=3, padx=(5, 0))
            appearance_mode_optionemenu = customtkinter.CTkOptionMenu( settings_frame, values= ["Light","Light"],
                                                                    command= change_appearance_mode_event)
            appearance_mode_optionemenu.grid(row=0, column=4, padx=(5, 0))



        # This function periodically updates elements of the GUI that need to be updated
    def Stuff_To_Update():
        global update_tick
        global Position_send
        global Speed_send
        global Current_send
        global Activate_send
        global Action_send
        global Estop_send
        global Release_dir_send
        global Motor1, Connected, Communication1
        global Clear_send
        global Calibrate_send
        global prev_Position_send, prev_Speed_send, prev_Current_send, prev_Activate_send, prev_Action_send
        global prev_Estop_send, prev_Release_dir_send

        Action_send = 1
        update_tick = update_tick + 1
 
        gpos = app.Position_slider.get()
        app.Position_numbers.configure(text = str(gpos))

        gvel = app.Speed_slider.get()
        app.Speed_numbers.configure(text = str(gvel))

        gcur = app.Current_slider.get()
        app.Current_numbers.configure(text = str(gcur))
        #logging.debug("I update")

        if Connected == 1:
            if Clear_send == 1:
                 Motor1.Send_Clear_Error()
                 Clear_send = 0
            elif Calibrate_send == 1:
                 Motor1.Send_gripper_calibrate()
                 Calibrate_send = 0
            elif Estop_send == 1:          
                Motor1.Send_gripper_data_pack(Position_send,Speed_send,Current_send,Activate_send,Action_send,Estop_send,Release_dir_send) 
                Estop_send = 0
            else:
                if(Position_send == prev_Position_send and Speed_send == prev_Speed_send and Current_send == prev_Current_send and Activate_send ==
                   prev_Activate_send and Action_send == prev_Action_send and Estop_send == prev_Estop_send and Release_dir_send ==prev_Release_dir_send):
                     Motor1.Send_gripper_data_pack()
                else: 
                    Motor1.Send_gripper_data_pack(Position_send,Speed_send,Current_send,Activate_send,Action_send,Estop_send,Release_dir_send) 

                
            message, UnpackedMessageID = Communication1.receive_can_messages(timeout=0.05) 

            if message is not None:
                """
                print(f"Message is: {message}")
                print(f"Node ID is : {UnpackedMessageID.node_id}")
                print(f"Message ID is: {UnpackedMessageID.command_id}")
                print(f"Error bit is: {UnpackedMessageID.error_bit}")
                print(f"Message length is: {message.dlc}")
                print(f"Is is remote frame: {message.is_remote_frame}")
                print(f"Timestamp is: {message.timestamp}")
                """
                Motor1.UnpackData(message,UnpackedMessageID)
                if(UnpackedMessageID.command_id == 60):
                    if(update_tick >= 10):
                        app.Pos_feedback.configure(text ="Position: " + str(Motor1.gripper_position))
                        app.Current_feedback.configure(text ="Current: " + str(Motor1.gripper_current))
                        update_tick = 0

                    if(Motor1.gripper_object_detection == 0):
                        app.Object_detection.configure(text="Gripper in motion ")
                    elif(Motor1.gripper_object_detection == 1):
                        app.Object_detection.configure(text="Object detected when closing ")
                    elif(Motor1.gripper_object_detection == 2):
                        app.Object_detection.configure(text="Object detected when opening ")
                    elif(Motor1.gripper_object_detection == 3):
                        app.Object_detection.configure(text="Gripper is at position ")

                    if(Motor1.gripper_calibrated == 1):
                        app.Calib_status.configure(text ="Calibrated")
                    elif(Motor1.gripper_calibrated == 0):
                        app.Calib_status.configure(text ="Not calibrated")

                    if(Motor1.gripper_activated == 1):
                        app.Activation_status.configure(text ="Activated")
                    elif(Motor1.gripper_activated == 0):
                        app.Activation_status.configure(text ="Not activated")

                    if(UnpackedMessageID.error_bit == 1):
                       app.Active_error.configure(text ="Error active ")
                    elif(UnpackedMessageID.error_bit == 0):
                      app.Active_error.configure(text ="No error ")

                    if(Motor1.gripper_temperature_error == 1):
                         app.Specific_error.configure(text ="Temperature error ")
                    elif(Motor1.gripper_timeout_error == 1):
                         app.Specific_error.configure(text ="Timeout error ")
                    elif(Motor1.estop_error == 1):
                         app.Specific_error.configure(text ="Estop error ")
                    else:
                         app.Specific_error.configure(text ="")
                     
            else:
                None
                #print("No message after timeout period!")

            prev_Position_send = Position_send
            prev_Speed_send = Speed_send 
            prev_Current_send = Current_send
            prev_Activate_send = Activate_send
            prev_Action_send = Action_send
            prev_Estop_send = Estop_send
            prev_Release_dir_send = Release_dir_send

        app.after(20,Stuff_To_Update) # update data every 25 ms


    def change_scaling_event( new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    def change_appearance_mode_event( new_appearance_mode: str):
        if(new_appearance_mode == "Dark"):
            fig.patch.set_facecolor("#2b2b2b")
            canvas.draw()
        if(new_appearance_mode == "Light"):
            fig.patch.set_facecolor("White")
            canvas.draw()
        customtkinter.set_appearance_mode(new_appearance_mode)

    def Calibrate_call():
         global Calibrate_send
         Calibrate_send = 1

    def Activate_call():
         global Activate_send
         if Activate_send == 0:
              Activate_send = 1
              app.Activate_button.configure(text = "Deactivate")
         elif Activate_send == 1:
              app.Activate_button.configure(text = "Activate")
              Activate_send = 0
        
    def Connect_call():
        global Motor1, Connected, Communication1
        channel_var = app.COM_port_entry.get()
        id_var = app.CAN_id_entry.get()
        try:
            Communication1 = Spectral.CanCommunication(bustype='slcan', channel=channel_var, bitrate=1000000)
            Motor1 = Spectral.SpectralCAN(node_id=int(id_var), communication=Communication1)
            Connected = 1
        except:
            Connected = 0
        
    def Clear_error():
         global Clear_send
         Clear_send = 1

    def Estop_call():
         global Estop_send
         Estop_send = 1

    def Set_position_command():
         global Position_send
         pos_value_entry = app.Position_entry.get()
         if(pos_value_entry != ""):
            app.Position_slider.set(int(pos_value_entry))
            app.Position_entry.delete(0,tk.END)
         Position_send = int(app.Position_slider.get())

         global Speed_send
         speed_value_entry = app.Speed_entry.get()
         if(speed_value_entry != ""):
            app.Speed_slider.set(int(speed_value_entry))
            app.Speed_entry.delete(0,tk.END)
         Speed_send = int(app.Speed_slider.get())
    

         global Current_send
         current_value_entry = app.Current_entry.get()
         if(current_value_entry != ""):
            app.Current_slider.set(int(current_value_entry))
            app.Current_entry.delete(0,tk.END)
         Current_send = int(app.Current_slider.get())
                 

    def Set_speed_command():
         global Position_send
         pos_value_entry = app.Position_entry.get()
         if(pos_value_entry != ""):
            app.Position_slider.set(int(pos_value_entry))
            app.Position_entry.delete(0,tk.END)
         Position_send = int(app.Position_slider.get())

         global Speed_send
         speed_value_entry = app.Speed_entry.get()
         if(speed_value_entry != ""):
            app.Speed_slider.set(int(speed_value_entry))
            app.Speed_entry.delete(0,tk.END)
         Speed_send = int(app.Speed_slider.get())
    

         global Current_send
         current_value_entry = app.Current_entry.get()
         if(current_value_entry != ""):
            app.Current_slider.set(int(current_value_entry))
            app.Current_entry.delete(0,tk.END)
         Current_send = int(app.Current_slider.get())
        
    def Set_current_command():
         global Position_send
         pos_value_entry = app.Position_entry.get()
         if(pos_value_entry != ""):
            app.Position_slider.set(int(pos_value_entry))
            app.Position_entry.delete(0,tk.END)
         Position_send = int(app.Position_slider.get())

         global Speed_send
         speed_value_entry = app.Speed_entry.get()
         if(speed_value_entry != ""):
            app.Speed_slider.set(int(speed_value_entry))
            app.Speed_entry.delete(0,tk.END)
         Speed_send = int(app.Speed_slider.get())
    

         global Current_send
         current_value_entry = app.Current_entry.get()
         if(current_value_entry != ""):
            app.Current_slider.set(int(current_value_entry))
            app.Current_entry.delete(0,tk.END)
         Current_send = int(app.Current_slider.get())


    #Plots_frame()
    Top_frame()
    Bottom_frame()
    Commands_frame1()
    Commands_frame2()
    Commands_frame3()
    Stuff_To_Update()

    def calculate_fps():
        global start_time, frame_count
        current_time = time.time()
        elapsed_time = current_time - start_time
        if elapsed_time >= 1:
            fps = frame_count / elapsed_time
            #print(f"FPS: {fps:.2f}")
            start_time = current_time
            frame_count = 0
            app.FPS_label.configure(text = str(int(fps)) + " FPS")
        app.after(1000, calculate_fps)



    ani = animation.FuncAnimation(fig, animate_sine_wave, frames=60, fargs=(line1, x), interval=var, blit=True)
    ani2 = animation.FuncAnimation(fig, animate_square_wave, frames=60, fargs=(line2, x), interval=var, blit=True)

    app.after(1000, calculate_fps)
    app.mainloop() 



if __name__ == "__main__":
    var = 10
    GUI(var)
    #app = customtkinter.CTk()
    #app.mainloop() 