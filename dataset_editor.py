import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
import glob
from PIL import Image,ImageTk

filepath = ''
photos = []
onEdge = False

def resizeImage(image,width,height):
    imageWidth = ImageTk.PhotoImage(image).width()
    imageHeight = ImageTk.PhotoImage(image).height()

    image = image.resize((width,int((width/imageWidth)*imageHeight)) if imageWidth>imageHeight else (int((height/imageHeight)*imageWidth),height),Image.LANCZOS)
    # image = image.resize((width,height),Image.LANCZOS)
    return ImageTk.PhotoImage(image)

def loadImages():
    global photos
    if filepath:
        filetype = ('/*.jpg', '/*.jpeg', '/*.png', '/*.webp')
        photoFiles = []
        for _type in filetype:
            photoFiles.extend(glob.glob(filepath + _type))
        photos = [Image.open(pic) for pic in photoFiles]

# 1 root
root = tk.Tk()
root.geometry('1280x720+100+100')
root.title('dataset editor')
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)
root.iconbitmap("icon.ico")

bg = ImageTk.PhotoImage(Image.open('bg.jpg'))

root.resizable(True,True)
root_sizegrip = ttk.Sizegrip(root)
root_sizegrip.pack(side=tk.RIGHT, anchor=tk.SE)

border = 10
# main_frame = tk.Frame(root)
# main_frame.pack(fill='both',expand=True)

# 1.1 overview
initial_width = 192
overview_frame = tk.Frame(root,width=initial_width,relief=tk.SUNKEN,borderwidth=border)
overview_frame.pack(side=tk.LEFT,anchor=tk.W,fill='y')
overview_frame.pack_propagate(False)

# 1.1.1 label
overview_label = tk.Label(overview_frame,relief=tk.RAISED,text='overview')
overview_label.pack(side=tk.TOP, anchor=tk.NW,fill='x')

# 1.1.2 close folder?



# 1.2 frame sizegrip
sizegrip_frame = tk.Frame(root,width=border,bg='grey')
sizegrip_frame.pack(side=tk.LEFT,anchor=tk.W,fill='y')

# 1.3 working bay
working_bay_frame = tk.Frame(root,relief=tk.SUNKEN,borderwidth=border)
working_bay_frame.pack(side=tk.LEFT,anchor=tk.W,fill='both',expand=True) # expand可对fill扩充；xfill-top/bottom，yfill-left/right；此处expand override xfill

# 1.3.1 display photo
# photos = selectFile() # select photo
current_photo_no = 0

display_width = 900
display_height = 600
if len(photos):
    current = resizeImage(photos[current_photo_no],display_width,display_height) # must be, don't know why, maybe calc order
photo_label = tk.Label(working_bay_frame,image=current if len(photos) else bg,width=display_width,height=display_height) #photos[current_photo_no] #
photo_label.pack(side=tk.TOP,anchor=tk.CENTER,expand=True)

# 1.3.2 info bar
number_var = tk.StringVar()
number_var.set(str(current_photo_no+1 if len(photos) else 0) + ' of ' + str(len(photos)))
tk.Label(working_bay_frame,textvariable=number_var, bd=1,anchor=tk.CENTER).pack(fill=tk.X)
# 1.3.3 buttons
button_frame = tk.Frame(working_bay_frame)
button_frame.pack()

prev_pic = tk.Button(button_frame,text='last')
update_pic = tk.Button(button_frame,text='update')
next_pic = tk.Button(button_frame,text='next')

prev_pic.pack(side=tk.LEFT,anchor=tk.CENTER)
update_pic.pack(side=tk.LEFT,anchor=tk.CENTER)
next_pic.pack(side=tk.RIGHT,anchor=tk.CENTER)






# widget function

#------------------------------------------

def mousedown(event):
    global border,onEdge
    frame_width = sizegrip_frame.winfo_width()
    onEdge = (0 <= event.x) and (event.x< frame_width)
    if onEdge:
        root.config(cursor="sizing")
    else:
        root.config(cursor="arrow")

def mouseleave(event):
    root.config(cursor="arrow")
    sizegrip_frame.bind("<Enter>", mouseenter)
def mouseenter(event):
    root.config(cursor="sizing")
    sizegrip_frame.bind("<Leave>", mouseleave)

def mousemove(event):
    global onEdge
    if onEdge:
        root.config(cursor="sizing")
        overview_frame.config(width=event.x_root-root.winfo_x()-border*1.5) # x_root: screen coord; winfo_x: win coord
        # overview_label.config(width=overview_frame.winfo_width())

def mouseup(event):
    global onEdge,overview_frame
    root.config(cursor="arrow")
    if onEdge:
        # overview_label.config(width=overview_frame.winfo_width())
        onEdge = False

#------------------------------------------

def changPic(next_no):
    global current_photo_no, current
    current_photo_no += next_no
    current_photo_no = 0 if not len(photos) else ((len(photos)-1) if current_photo_no<0 else (0 if current_photo_no==len(photos) else current_photo_no))
    number_var.set(f'{current_photo_no+1 if len(photos) else 0 } of {len(photos)}')
    if len(photos):
        current = resizeImage(photos[current_photo_no],display_width,display_height)
    photo_label.configure(image=current if len(photos) else bg)

def update():
    global current_photo_no, current
    number_var.set(f'... of ...')
    # photos = selectFile()
    loadImages()
    current_photo_no = 0
    if len(photos):
        current = resizeImage(photos[current_photo_no],display_width,display_height)
    photo_label.configure(image=current if len(photos) else bg)

#------------------------------------------

def newCommand():
    pass
def openFileCommand():
    pass
def openFolderCommand():
    global filepath
    filepath = fd.askdirectory(initialdir='D:/Downloads')
    update()
def closeAllCommand():
    global filepath, photos
    filepath = ''
    photos = []
    update()

# binding
file_menu = tk.Menu(menu_bar);menu_bar.add_cascade(label="File",menu=file_menu)

file_menu.add_command(label="New(N/A)",command=newCommand)
file_menu.add_command(label="Open folder",command=openFolderCommand)
file_menu.add_command(label="Open files(N/A)",command=openFileCommand)
file_menu.add_command(label="close all",command=closeAllCommand)

sizegrip_frame.bind('<Enter>', mouseenter)
sizegrip_frame.bind('<Button-1>', mousedown)
sizegrip_frame.bind('<B1-Motion>', mousemove)
sizegrip_frame.bind('<ButtonRelease-1>', mouseup)

prev_pic.config(command=lambda: changPic(-1))
update_pic.config(command=lambda: update())
next_pic.config(command=lambda: changPic(1))



root.mainloop()

# def print_hi(name):
#     # 在下面的代码行中使用断点来调试脚本。
#     print(f'Hi, {name}')  # 按 Ctrl+F8 切换断点。
#
#
# # 按间距中的绿色按钮以运行脚本。
# if __name__ == '__main__':
#     print_hi('PyCharm')
