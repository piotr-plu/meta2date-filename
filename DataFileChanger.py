# Author: Piotr Pluta
# Date: 28.12.2022

import os
from datetime import datetime
import time as t
import tkinter as tk
from tkinter import filedialog

default_path_dir = ""
default_extension = "*"
default_file_name = "%Y-%m-%d_%H-%M-%S"


help_text_file = ("%a	Abbreviated weekday name.	Sun, Mon, ...\n \
%A	Full weekday name.	Sunday, Monday, ...\n \
%w	Weekday as a decimal number.	0, 1, ..., 6\n \
%d	Day of the month as a zero-padded decimal.	01, 02, ..., 31 \n \
%-d	Day of the month as a decimal number.	1, 2, ..., 30\n \
%b	Abbreviated month name.	Jan, Feb, ..., Dec\n \
%B	Full month name.	January, February, ...\n \
%m	Month as a zero-padded decimal number.	01, 02, ..., 12\n \
%-m	Month as a decimal number.	1, 2, ..., 12\n \
%y	Year without century as a zero-padded decimal number.	00, 01, ..., 99\n \
%-y	Year without century as a decimal number.	0, 1, ..., 99\n \
%Y	Year with century as a decimal number.	2013, 2019 etc.\n \
%H	Hour (24-hour clock) as a zero-padded decimal number.	00, 01, ..., 23\n \
%-H	Hour (24-hour clock) as a decimal number.	0, 1, ..., 23\n \
%I	Hour (12-hour clock) as a zero-padded decimal number.	01, 02, ..., 12\n \
%-I	Hour (12-hour clock) as a decimal number.	1, 2, ... 12\n \
%p	Locale’s AM or PM.	AM, PM\n \
%M	Minute as a zero-padded decimal number.	00, 01, ..., 59\n \
%-M	Minute as a decimal number.	0, 1, ..., 59\n \
%S	Second as a zero-padded decimal number.	00, 01, ..., 59\n \
%-S	Second as a decimal number.	0, 1, ..., 59\n \
%f	Microsecond as a decimal number, zero-padded on the left.	000000 - 999999\n \
%z	UTC offset in the form +HHMM or -HHMM.	\n \
%Z	Time zone name.	\n \
%j	Day of the year as a zero-padded decimal number.	001, 002, ..., 366\n \
%-j	Day of the year as a decimal number.	1, 2, ..., 366\n \
%U	Week number of the year (Sunday as the first day of the week). \n \
%W	Week number of the year (Monday as the first day of the week). \n \
%c	Locale’s appropriate date and time representation.	Mon Sep 30 07:06:05 2013\n \
%x	Locale’s appropriate date representation.	09/30/13\n \
%X	Locale’s appropriate time representation.	07:06:05\n \
%%	A literal '%' character.	%\n")



guard = 0
done_counter = 0
def change_name(dir_path, extensions, date_orgin, name_stucture, name_template):
    global done_counter
    done_counter = 0
    repeat_done_counter = 0
    dt_list=""

    # Iterates over each file
    for(dir_path, dir_names, file_names) in os.walk(dir_path):
        for name in file_names:
            
            # Get name and file extension
            file_name = name.split(".",1)[0]
            file_extension = name.split(".",1)[1]

            if date_orgin == "Modify date":
                m_time = os.path.getmtime( dir_path + "\\" + name)
            
            elif date_orgin == "Create date":
                m_time = os.path.getctime( dir_path + "\\" + name)  
            
            elif date_orgin == "File name":

                for var in ['Y', 'M', 'D', 'h', 'm', 's', 'f']:

                        pos = [pos for pos, char in enumerate(name_structure) if char == var]

                        part = ''
                        for x in pos:
                            part += str((file_name[x]))
                        
                        if part == "":
                            part = "00"

                        dt_list += part

                dt_list_format = (dt_list[0:4]+"-"+dt_list[4:6]+"-"+dt_list[6:8]+
                                    " "+dt_list[8:10]+":"+dt_list[10:12]+":"+dt_list[12:14]+
                                    "."+dt_list[14:])
                dt_list = ""
                        
                try:
                    m_time = (t.mktime(datetime.strptime(dt_list_format, "%Y-%m-%d %H:%M:%S.%f").timetuple()))
                except ValueError:
                    log_window.insert(tk.END, "Error - Data does not match format\nCheck the filed \"Point the date\"\n")
                    break

            dt_string = datetime.fromtimestamp(m_time)
            new_file_name = dt_string.strftime(name_template)          
            
            # dt_list.append(file_name)
            # tags = { r'{Y}':dt_list[0], 
            #          r'{M}':dt_list[1], 
            #          r'{D}':dt_list[2], 
            #          r'{h}':dt_list[3], 
            #          r'{m}':dt_list[4], 
            #          r'{s}':dt_list[5], 
            #          r'{f}':dt_list[6],
            #          r'{N}':dt_list[7]}

            # new_file_name = name_template
            # for key in tags:
            #     new_file_name = new_file_name.replace(key, tags[key])

            # Rename the file
            if (file_extension in extensions) or ("*" in extensions):
                try:
                    os.rename(dir_path + "\\" + name, dir_path + "\\" + new_file_name + "." + file_extension)
                    log_window.insert(tk.END, f"{name} -> {new_file_name}.{file_extension}\n")

                except FileExistsError:
                    #rror_name = (dir_path + "\\" + name, dir_path + "\\" + new_file_name + "." + file_extension)
                    repeat_done_counter += 1
                    os.rename(dir_path + "\\" + name, dir_path + "\\" + new_file_name + "_" + f"({repeat_done_counter})" +"." + file_extension)
                    log_window.insert(tk.END, f"{name} -> {new_file_name}_({repeat_done_counter}).{file_extension}\n")

                except:
                    log_window.insert(tk.END, "Error - File exist\n")
                    repeat_done_counter+=1
                    continue
                


                # Counting how many files have been renamed

                done_counter+=1
    log_window.insert(tk.END, "\n")


# GUI
root = tk.Tk()
root.title('Change Name To Modify Date')

# Menu bar
menubar = tk.Menu(root)
root.config(menu=menubar)

# Set frames
settings_frame = tk.LabelFrame(root, text='Settings', padx=10, pady=10)
settings_frame.grid(row=0, column=0, padx=15, pady=15, )

date_get_frame = tk.LabelFrame(root, text="Get date from:", padx=10, pady=10)
date_get_frame.grid(row=1, column=0, padx=15, pady=15)

name_template_frame = tk.LabelFrame(root, text="Name Template", padx=10, pady=10)
name_template_frame.grid(row=2, column=0, padx=15, pady=15, )

log_window_frame = tk.LabelFrame(root, text="Logs", padx=10, pady=10)
log_window_frame.grid(row=0, column=1, padx=15, pady=15, rowspan=3)

# Help Menu

def open_help():
    global help_text_file

    help_window = tk.Toplevel()
    help_window.title('Help')

    help_label = tk.Label(help_window, text="Help for Name Template tags:", padx=10, pady=10)
    help_label.pack(padx=10, pady=10)

    # Add a Scrollbar

    help_scrollbar = tk.Scrollbar(help_window, orient='vertical')
    help_text = tk.Text(help_window, height=20, width=90, padx=15, pady=15, yscrollcommand=help_scrollbar.set )
    help_scrollbar.config(command=help_text.yview)
    help_scrollbar.pack(side='right', fill='y')

    help_text.pack(padx=30, pady=20)
    help_text.insert(tk.END, help_text_file)
    help_text.config(state='disabled')


menubar.add_cascade(label='Help', command=open_help)

# Entering Path filed
tk.Label(settings_frame, text='Location:').grid(row=0, column=0, sticky='W')
dir_path_field = tk.Entry(settings_frame, width=40, border=2)
dir_path_field.grid(row=0, column=1)
dir_path_field.insert(0, default_path_dir)

# Path filed button to easli search a directory with files to rename
def browse_button():
    file_path =  filedialog.askdirectory()
    dir_path_field.delete(0, 'end')
    dir_path_field.insert(0, file_path)

tk.Button(settings_frame, text='...', command=browse_button).grid(row=0, column=2)

# Entering field for files extensions
tk.Label(settings_frame, text='Files extensions: ',).grid(row=2, column=0, sticky='W')
file_extension_field = tk.Entry(settings_frame, width=40, border=2)
file_extension_field.insert(0, default_extension)
file_extension_field.grid(row=2, column=1)

# Input field for choosing where to get the date from
choice = tk.StringVar()
choice.set("Modify date")

def enable_field():
    if choice.get() == "File name":
        name_structure_field.config(state='normal')
    else:
        name_structure_field.config(state='disabled')

tk.Radiobutton(date_get_frame, text="Properties: Modify Date", variable=choice, value="Modify date", justify='left', command= enable_field ).grid(row=0, column=0, sticky='w')
tk.Radiobutton(date_get_frame, text="Properties: Create Date", variable=choice, value="Create date", justify='left',command= enable_field ).grid(row=1, column=0, sticky='w')
tk.Radiobutton(date_get_frame, text="File Name", variable=choice, value="File name", justify='left', command= enable_field ).grid(row=2, column=0, sticky='w')
tk.Label(date_get_frame, text='Point the date: ',).grid(row=2, column=1)
name_structure_field = tk.Entry(date_get_frame, width=40, border=2)
name_structure_field.config(state='disable')
name_structure_field.grid(row=2, column=2)

# Name template
tk.Label(name_template_frame, text='Build name template for files: ',).grid(row=1, column=0)
name_template_field = tk.Entry(name_template_frame, width=40, border=2)
name_template_field.grid(row=1, column=1)
name_template_field.insert(0, default_file_name)

# Log window
log_scrollbar = tk.Scrollbar(log_window_frame, orient='vertical')
log_window = tk.Text(log_window_frame, height=20, width=60, yscrollcommand=log_scrollbar.set, state='disabled')
log_window.grid(row=0, column=0)
log_scrollbar.config(command=log_window.yview)
log_scrollbar.grid(row=0, column=1, sticky='nse')



# Buttom to accept entered settings
def apply_button():
    global dir_path, extensions, name_structure, date_orgin, name_template
    global file_extension_field, name_structure_field, name_template_field
    global location_label, file_name_label, extension_label, guard


    dir_path = f"{dir_path_field.get()}"
    extensions = file_extension_field.get().split(",",-1)
    name_structure = str(name_structure_field.get())
    date_orgin = choice.get()
    name_template = name_template_field.get()

    log_window.config(state='normal')
    log_window.insert(tk.END, "----- Set Settings -----\n")
    log_window.insert(tk.END, f"Location: {dir_path}\nFile extensions: {extensions}\nDate orgin: {date_orgin}\nName Template: {name_template}\n\n")
    log_window.see(tk.END)
    log_window.config(state='disabled')
    guard = 1

tk.Button(root, text='Apply', width=20, command=apply_button).grid(row=3, column=0, padx=5, pady=5, columnspan=2)

# Run butoon - start the program
def run_button():
    global done_counter, dir_path, name_structure, name_template, guard
    
    log_window.config(state='normal')
    if guard == 1:
        log_window.insert(tk.END, "----- Start Program -----\n")
        change_name(dir_path=dir_path, extensions=extensions, date_orgin=date_orgin, name_stucture=name_structure, name_template=name_template)
        log_window.insert(tk.END, "----- Done -----\n")
        log_window.insert(tk.END, f"Changed {done_counter} files name\n\n")
        log_window.see(tk.END)

        guard = 0
    else:
        log_window.insert(tk.END, "----- Error -----\n")
        log_window.insert(tk.END, f"First click Apply button \n\n")
        log_window.see(tk.END)

    log_window.config(state='disabled')

tk.Button(root, text='Run', width=20, height=2, command=run_button).grid(row=4, column=0, padx=10, pady=10, columnspan=2 )

root.mainloop()




        



