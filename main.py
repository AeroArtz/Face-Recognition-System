import os.path
import subprocess
import tkinter as tk
import util
import cv2
from PIL import Image,ImageTk
import datetime
import os
import mysql.connector

dataBase = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="admin",
    database="damac"
)

# preparing a cursor object
cursorObject = dataBase.cursor()

class App:
    def __init__(self):
        self.main_window = tk.Tk()
        self.main_window.geometry('1200x520+350+100')
        self.login_button_main_window = util.get_button(self.main_window,
                                                        'login','green',self.login)
        self.login_button_main_window.place(x=750,y=300)
        self.register_button_main_window = util.get_button(self.main_window,
                                                           'register', 'gray',
                                                           self.register_new_user,fg='black')

        self.register_button_main_window.place(x=750, y=400)

        self.webcam_label = util.get_img_label(self.main_window)

        self.webcam_label.place(x=10,y=0,width = 700,height = 500)
        self.add_webcam(self.webcam_label)

        self.db_dir = './db'
        if not os.path.exists(self.db_dir):
            os.mkdir(self.db_dir)

        self.log_path = './log.txt'
    def start(self):
        self.main_window.mainloop()

    def login(self):
        unknown_img_path = './.tmp.jpg'
        cv2.imwrite(unknown_img_path,self.most_recent_capture_arr)
        output = str(subprocess.check_output(['face_recognition', self.db_dir, unknown_img_path]))
        name = output.split(',')[-1][:-5]
        print(name)
        if name in ['uknown_person','no_persons_found']:
            util.msg_box('Error','User not found, Please register or try again')
        else:
            util.msg_box('Successful Login',f'Welcome back, {name}')
            with open(self.log_path,'a') as f:
                f.write(f'{name}, {datetime.datetime.now()}\n')
        os.remove(unknown_img_path)

    def register_new_user(self):
        self.register_new_user_window = tk.Toplevel(self.main_window)
        self.register_new_user_window.geometry('1200x920+370+120')

        self.accept_button_register_new_user_window = util.get_button(self.register_new_user_window,
                                                        'Confirm', 'green', self.confirm_register_new_user)
        self.accept_button_register_new_user_window.place(x=750, y=400)

        self.tryagain_button_register_new_user_window = util.get_button(self.register_new_user_window,
                                                                      'try again', 'red', self.tryagain_register_new_user)
        self.tryagain_button_register_new_user_window.place(x=750, y=500)

        self.capture_label = util.get_img_label(self.register_new_user_window)

        self.capture_label.place(x=10, y=0, width=700, height=500)

        self.add_img_to_label(self.capture_label)

        self.name_input = util.get_entry_text(self.register_new_user_window)
        self.name_input.place(x=750,y=90)

        self.name_input_label = util.get_text_label(self.register_new_user_window,'Enter name: ')
        self.name_input_label.place(x=750,y=30)

        self.cluster_input = util.get_entry_text(self.register_new_user_window)
        self.cluster_input.place(x=750, y=210)

        self.cluster_input_label = util.get_text_label(self.register_new_user_window, 'Enter cluster: ')
        self.cluster_input_label.place(x=750, y=150)

        self.villa_input = util.get_entry_text(self.register_new_user_window)
        self.villa_input.place(x=750, y=330)

        self.villa_input_label = util.get_text_label(self.register_new_user_window, 'Enter villa number: ')
        self.villa_input_label.place(x=750, y=270)

    def confirm_register_new_user(self):
        name = self.name_input.get(1.0,"end-1c")
        cluster = self.cluster_input.get(1.0, "end-1c")
        villa_number = self.villa_input.get(1.0, "end-1c")

        registered = self.user_already_registered(name,cluster,villa_number)
        if registered:

            util.msg_box('ERROR','User has already been registered, Please login')
            self.register_new_user_window.destroy()
            return

        self.add_usertoDB(name,cluster,villa_number)

        cv2.imwrite(os.path.join(self.db_dir,f'{name}.jpg'),self.register_new_user_capture)

        util.msg_box('Success','The user has been registered successfully')

        self.register_new_user_window.destroy()

    def user_already_registered(self,name,cluster,villa_number):
        query = f"SELECT * FROM users where name='{name}' and cluster='{cluster}' and villa_no={villa_number} "
        cursorObject.execute(query)

        myresult = cursorObject.fetchall()
        if myresult:
            return True
        return False

    def add_usertoDB(self,name,cluster,villa_number):
        sql = "INSERT INTO users (name, cluster, villa_no)\
        VALUES (%s, %s, %s)"
        val = (name,cluster,villa_number)

        cursorObject.execute(sql, val)
        dataBase.commit()
    def tryagain_register_new_user(self):
        self.register_new_user_window.destroy()

    def add_img_to_label(self,label):
        imgtk = ImageTk.PhotoImage(image=self.most_recent_capture_pil)

        label.imgtk = imgtk
        label.configure(image=imgtk)

        self.register_new_user_capture = self.most_recent_capture_arr.copy()


    def add_webcam(self,label):
        if 'cap' not in self.__dict__:
            self.cap = cv2.VideoCapture(0)
        self._label = label
        self.process_webcam()

    def process_webcam(self):
        ret ,frame = self.cap.read()
        self.most_recent_capture_arr = frame

        img_ = cv2.cvtColor(self.most_recent_capture_arr, cv2.COLOR_BGR2RGB)
        self.most_recent_capture_pil = Image.fromarray(img_)

        imgtk = ImageTk.PhotoImage(image=self.most_recent_capture_pil)

        self._label.imgtk = imgtk
        self._label.configure(image=imgtk)
        self._label.after(20, self.process_webcam)


if __name__=='__main__':
    app = App()
    app.start()
    dataBase.close()
