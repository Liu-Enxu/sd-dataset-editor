import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
# import customtkinter as ctk

import glob
from PIL import Image,ImageTk
import threading as th



class dataset_editor:

    class FrameCards(tk.Frame):
        def __init__(self, imgsize, img: tk.PhotoImage, filepath, idx, app):
            tk.Frame.__init__(self, app.overview_scroll_frame, relief=tk.RAISED, borderwidth=5)
            self.app = app
            self.idx = idx

            self.photoLabel = tk.Label(self, image=img)
            self.photoLabel.photo = img
            self.photoLabel.pack(side=tk.TOP, anchor=tk.N)

            self.textLabel = tk.Label(self, text=filepath, wraplength=imgsize)  #
            self.textLabel.pack(side=tk.TOP, anchor=tk.CENTER, fill='x')

            self.photoLabel.bind("<Button-1>", self.mousedown)
            self.textLabel.bind("<Button-1>", self.mousedown)

        def changeFramePic(self, img: tk.PhotoImage, imgsize):
            self.photoLabel.configure(image=img)
            self.photoLabel.photo = img
            self.textLabel.configure(wraplength=imgsize)

        def mousedown(self, event):
            self.configure(relief=tk.GROOVE)
            self.app.current_photo_no = self.idx
            self.app.loadCurrent()
            self.photoLabel.bind("<ButtonRelease-1>", self.mouseup)
            self.textLabel.bind("<ButtonRelease-1>", self.mouseup)

        def mouseup(self, event):
            self.configure(relief=tk.RAISED)

    def __init__(self):
        self.filepath = ''
        self.photos = {}
        # self.onEdge = False
        self.overview_sub_frames = []
        self.threads = []

        self.display_width = 900
        self.display_height = 600
        self.border = 10 # all borders
        self.current_photo_no = 0
        self.overview_frame_width = self.display_width//4 # working bay width

        self.root = tk.Tk()
        # self.root = ctk.CTk()
        self.create_widgets()
        self.root.mainloop()

    def create_widgets(self):
        """"""""""""""""""""
        """widget declare"""
        """"""""""""""""""""
        self.temp = Image.open('bg.jpg')
        self.bg = ImageTk.PhotoImage(Image.open('bg.jpg'))
        self.current = self.bg
        # 1 root

        self.root.geometry('1280x720+100+100')
        self.root.title('dataset editor')
        self.root.iconbitmap("icon.ico")
        self.root.attributes('-alpha', 0.9)  # 透明度
        self.root.resizable(True, True)
        self.root_sizegrip = ttk.Sizegrip(self.root)
        self.root_sizegrip.pack(side=tk.RIGHT, anchor=tk.SE)
        self.panedwindow = tk.PanedWindow(relief=tk.SUNKEN,bd=self.border,sashrelief=tk.RAISED, sashwidth=self.border, showhandle=False)
        self.panedwindow.pack(fill='both', expand=True)
        # self.panedwindow.bind('<B1-Motion>', self.resizeOverview)

        # 1.1 menu bar
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)
        self.file_menu = tk.Menu(self.menu_bar)

        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="New(N/A)", command=self.newCommand)
        self.file_menu.add_command(label="Open folder", command=self.openFolderCommand)
        self.file_menu.add_command(label="Open files(N/A)", command=self.openFileCommand)
        self.file_menu.add_command(label="close all", command=self.closeAllCommand)

        # 1.2 overview_frame
        self.overview_frame = tk.Frame(self.panedwindow, width=self.overview_frame_width, relief=tk.SUNKEN)
        self.panedwindow.add(self.overview_frame)
        self.overview_frame.pack_propagate(False)


        # 1.2.1 label
        self.overview_label = tk.Label(self.overview_frame, relief=tk.RAISED, text='overview')
        self.overview_label.pack(side=tk.TOP, anchor=tk.NW, fill='x')

        # 1.2.2 scrollable overviews
        self.overview_scrollbar = tk.Scrollbar(self.overview_frame, orient=tk.VERTICAL, width=self.border*2)
        self.overview_scrollbar.pack(side=tk.RIGHT, fill='y')

        self.overview_canvas = tk.Canvas(self.overview_frame)
        self.overview_canvas.configure(yscrollcommand=self.overview_scrollbar.set) # bg='red',
        self.overview_canvas.pack(side=tk.TOP, fill='both', expand=True)

        self.overview_scrollbar.configure(command=self.overview_canvas.yview)

        # 1.2.2.1 scrollable frame
        self.overview_scroll_frame = tk.Frame(self.overview_canvas)
        self.overview_canvas.create_window((0, 0), window=self.overview_scroll_frame, anchor=tk.NW)
        # self.overview_canvas.bind("<Configure>", self.on_frame_configure) # is it needed?on_canvas_configure
        self.overview_scroll_frame.bind("<Configure>", self.on_frame_configure)

        self.overview_canvas.bind('<Configure>',self.resizeOverview)
        self.root.bind('<ButtonRelease-1>',self.clearThreads)
        # self.overview_frame.bind('<B1-Motion>', self.resizeOverview)

        # 1.3 working bay
        self.working_bay_frame = tk.Frame(self.panedwindow, relief=tk.SUNKEN)
        self.panedwindow.add(self.working_bay_frame)

        # 1.3.1 display photo
        # self.photos = selectFile() # select photo
        self.photo_label = tk.Label(self.working_bay_frame, image=self.bg, width=self.display_width, height=self.display_height)
        self.photo_label.pack(side=tk.TOP, anchor=tk.CENTER, expand=True)

        # 1.3.2 info bar
        self.number_var = tk.StringVar()
        self.number_var.set(str(self.current_photo_no + 1 if len(self.photos) else 0) + ' of ' + str(len(self.photos)))
        tk.Label(self.working_bay_frame, textvariable=self.number_var, bd=1, anchor=tk.CENTER).pack(fill=tk.X)
        # 1.3.3 buttons
        self.button_frame = tk.Frame(self.working_bay_frame)
        self.button_frame.pack()

        self.prev_pic = tk.Button(self.button_frame, text='last',command=lambda: self.changPic(-1))
        self.update_pic = tk.Button(self.button_frame, text='update',command=lambda: self.update())
        self.next_pic = tk.Button(self.button_frame, text='next',command=lambda: self.changPic(1))

        self.prev_pic.pack(side=tk.LEFT, anchor=tk.CENTER)
        self.update_pic.pack(side=tk.LEFT, anchor=tk.CENTER)
        self.next_pic.pack(side=tk.RIGHT, anchor=tk.CENTER)

    """"""""""""""""""""""""""""""""""""""""""""""""
    """other method (widget realization excluded)"""
    """"""""""""""""""""""""""""""""""""""""""""""""
    def resizeImage(self,image,width,height):
        imageWidth, imageHeight = image.size
        img = ImageTk.PhotoImage(image.resize((width,int((width/imageWidth)*imageHeight)) if imageWidth>=imageHeight else (int((height/imageHeight)*imageWidth),height),Image.LANCZOS))
        return img
        # return ImageTk.PhotoImage(img)

    def resizePerOverview(self,pic,imgsize,frame):
        img = self.resizeImage(pic, imgsize, imgsize)
        # frame.changeFramePic(img, imgsize)
        self.root.after(0, frame.changeFramePic, img, imgsize)

    def threading(self,pic,imgsize,frame):
        t = th.Thread(target=self.resizePerOverview, args=(pic,imgsize,frame))
        self.threads.append(t)
        t.start()

    def clearThreads(self,event):
        if self.threads:
            for t in self.threads:
                t.join()
            self.threads.clear()

    def resizeOverview(self,event):
        self.overview_frame_width = event.width # slow
        if self.overview_sub_frames:
            # self.overview_frame_width = event.x
            # self.overview_frame_width = event.x_root - self.root.winfo_x() - self.border * 1.5
            imgsize = int(self.overview_frame_width - self.border * 2)

            for i,frame in enumerate(self.overview_sub_frames):
                # img = self.resizeImage(list(self.photos.values())[i],imgsize,imgsize)
                # frame.changeFramePic(img,imgsize)
                self.threading(list(self.photos.values())[i],imgsize,frame)
                # self.root.after(0, self.resizePerOverview, list(self.photos.values())[i], imgsize, frame)

    def destroyFrames(self):
        for frame in self.overview_sub_frames:
            frame.photoLabel.pack_forget()
            # frame.photoLabel.photo.destroy()
            frame.photoLabel.destroy()

            frame.textLabel.pack_forget()
            frame.textLabel.destroy()

            frame.pack_forget()
            frame.destroy()
        self.overview_sub_frames.clear()

    def loadImages(self):
        if self.filepath:
            filetype = ('/*.jpg', '/*.jpeg', '/*.png', '/*.webp')
            # delete all frame cards?
            if self.overview_sub_frames:
                self.destroyFrames()

            frameidx = 0
            for _type in filetype:
                for picfilepath in glob.glob(self.filepath + _type):
                    self.photos[picfilepath] = Image.open(picfilepath) # extend add pixels, use append

                    imgsize = int(self.overview_frame_width-self.border*2)
                    img = self.resizeImage(self.photos[picfilepath], imgsize, imgsize)

                    new_frame = self.FrameCards(imgsize,img,picfilepath,frameidx,self)
                    new_frame.pack(side=tk.TOP, anchor=tk.CENTER, expand=True)
                    self.overview_sub_frames.append(new_frame)
                    frameidx+=1



    def loadCurrent(self):
        self.current = self.resizeImage(list(self.photos.values())[self.current_photo_no], self.display_width, self.display_height) if len(self.photos) else self.bg
        self.photo_label.configure(image=self.current)
    def changPic(self,next_no):
        self.current_photo_no += next_no
        self.current_photo_no = 0 if not len(self.photos) else ((len(self.photos)-1) if self.current_photo_no<0 else (0 if self.current_photo_no==len(self.photos) else self.current_photo_no))
        self.number_var.set(f'{self.current_photo_no+1 if len(self.photos) else 0 } of {len(self.photos)}')
        # self.loadCurrent(self.current_photo_no)
        self.loadCurrent()
    def update(self):
        self.number_var.set(f'... of ...')
        self.loadImages()
        self.current_photo_no = 0 # need to change, dont start over again
        self.loadCurrent()
        self.number_var.set(f'{self.current_photo_no + 1 if len(self.photos) else 0} of {len(self.photos)}')
        # changPic(0)

    """""""""""""""""""""""
    """"widget function""""
    """""""""""""""""""""""

    # tool bar------------------------------------------

    def newCommand(self):
        pass

    def openFileCommand(self):
        pass

    def openFolderCommand(self):
        self.filepath = fd.askdirectory(initialdir='D:/Downloads')
        self.update()

    def closeAllCommand(self):
        self.destroyFrames()
        self.filepath = ''
        self.photos = {}
        self.update()

    # overview------------------------------------------

    def on_frame_configure(self,event):
        self.overview_canvas.configure(scrollregion=self.overview_canvas.bbox("all"))

    def on_canvas_configure(self,event):
        self.overview_canvas.itemconfig('frame', width=event.width)

    # drag bar------------------------------------------

    # def mousedown(self,event):
    #     width = self.sizegrip_frame.winfo_width()
    #     self.onEdge = (0 <= event.x) and (event.x< width)
    #     if self.onEdge:
    #         self.root.config(cursor="sizing")
    #     else:
    #         self.root.config(cursor="arrow")
    #
    # def mouseleave(self,event):
    #     self.root.config(cursor="arrow")
    #     self.sizegrip_frame.bind("<Enter>", self.mouseenter)
    # def mouseenter(self,event):
    #     self.root.config(cursor="sizing")
    #     self.sizegrip_frame.bind("<Leave>", self.mouseleave)
    #
    # def mousemove(self,event):
    #     if self.onEdge:
    #         self.root.config(cursor="sizing")
    #         self.overview_frame_width = event.x_root-self.root.winfo_x()-self.border*1.5
    #         self.overview_frame.config(width=self.overview_frame_width) # x_root: screen coord; winfo_x: win coord
    #
    #
    # def mouseup(self,event):
    #     self.root.config(cursor="arrow")
    #     if self.onEdge:
    #         # overview_label.config(width=overview_frame.winfo_width())
    #         self.onEdge = False



dataset_editor()












