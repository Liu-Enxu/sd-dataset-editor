"""
ver-1.3

En:
-single working page, double linkedlist
-update does not change current display
-still cannot pan and zoom
-need notebook

Ch-Zh:
-单页双链表
-更新不再会重置当前展示
-图片不能放大缩小/拖动
-需要notebook
"""

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
# import customtkinter as ctk

import glob
from PIL import Image,ImageTk
import threading as th

class dataset_editor:

    class ImgDisplay:
        # todo: append current crop settings onto the image
        def __init__(self,img):
            pass

    class FrameCards(tk.Frame):
        def __init__(self, imgsize, img, filepath,linkedImg,app):
            tk.Frame.__init__(self, app.overview_scroll_frame, relief=tk.RAISED, borderwidth=5)
            self.linkedImg = linkedImg
            self.app = app
            self.imgdisplay = self.app.ImgDisplay(img) # todo: class further define needed

            imgTK_Resized = self.app.resizeImage(img,imgsize,imgsize)

            # right click menu
            self.menu = tk.Menu(self,tearoff=False)
            self.menu.add_command(label="open tab(N/A)",command=self.open_tab)
            self.menu.add_command(label="delete(N/A)", command=self.delete)
            self.menu.add_separator()
            self.menu.add_command(label="clear cropping(N/A)", command=self.clear_crop)
            # image
            self.photoLabel = tk.Label(self, image=imgTK_Resized)
            self.photoLabel.photo = imgTK_Resized
            self.photoLabel.pack(side=tk.TOP, anchor=tk.N)
            # txt
            self.textLabel = tk.Label(self, text=filepath, wraplength=imgsize)
            self.textLabel.pack(side=tk.TOP, anchor=tk.CENTER, fill='x')

            # function binding-------------------------------------------------
            self.bind("<MouseWheel>", self.app.on_mousewheel)
            self.photoLabel.bind("<Button-1>", self.mousedown)
            self.photoLabel.bind("<MouseWheel>", self.app.on_mousewheel)
            self.photoLabel.bind("<Button-3>",self.pop_up)
            self.textLabel.bind("<Button-1>", self.mousedown)
            self.textLabel.bind("<MouseWheel>", self.app.on_mousewheel)
            self.textLabel.bind("<Button-3>", self.pop_up)

        # menu functions-----------------------------------------
        def open_tab(self):
            pass
        def delete(self):
            pass
        def clear_crop(self):
            pass
        def pop_up(self,event):
            self.menu.post(event.x_root,event.y_root)

        def mousedown(self, event):
            # set style
            self.configure(relief=tk.GROOVE)
            # set current
            self.app.display_currents = self.linkedImg
            self.app.loadCurrent()
            # release
            self.photoLabel.bind("<ButtonRelease-1>", self.mouseup)
            self.textLabel.bind("<ButtonRelease-1>", self.mouseup)

        def mouseup(self, event):
            self.configure(relief=tk.RAISED)

        def changeFramePic(self, img: tk.PhotoImage, imgsize): # resize overview
            self.photoLabel.configure(image=img)
            self.photoLabel.photo = img
            self.textLabel.configure(wraplength=imgsize)

    class LinkedImages:
        def __init__(self,imgsize,img,filepath,app):
            self.app = app
            self.img = img
            self.filepath = filepath

            self.prev = None
            self.next = None

            if filepath:
                self.frameCard = self.app.FrameCards(imgsize,img,filepath,self,self.app)
                self.frameCard.pack(side=tk.TOP, anchor=tk.N, expand=True)

    # notebook --------------------------------------------
    class DisplayCards:
        def __init__(self,app):
            self.app = app

            self.displayframe = tk.Frame(self.app.working_bay_tags,bg='blue') # multiple of these
            self.displayframe.pack(side=tk.TOP,anchor=tk.CENTER, fill='x', expand=True)
            self.app.working_bay_tags.add(self.displayframe,text="")

            self.warking_bay_vbar = tk.Scrollbar(self.app.warking_bay_display, orient=tk.VERTICAL, width=self.app.border * 2)
            self.warking_bay_vbar.pack(side=tk.RIGHT, fill='y')
            self.warking_bay_hbar = tk.Scrollbar(self.app.warking_bay_display, orient=tk.HORIZONTAL, width=self.app.border * 2)
            self.warking_bay_hbar.pack(side=tk.BOTTOM, fill='x')

            self.photo_label = tk.Label(self.displayframe, image=self.app.bgTK, width=self.app.display_width,height=self.app.display_height)
            self.photo_label.pack(side=tk.TOP, fill='both', expand=True)
        def delete_tab(self):
            pass

        # 1.3.1.1 image scroll bars
        # self.warking_bay_vbar = tk.Scrollbar(self.warking_bay_display, orient=tk.VERTICAL, width=self.border * 2)
        # self.warking_bay_vbar.pack(side=tk.RIGHT, fill='y')
        # self.warking_bay_hbar = tk.Scrollbar(self.warking_bay_display, orient=tk.HORIZONTAL, width=self.border * 2)
        # self.warking_bay_hbar.pack(side=tk.BOTTOM, fill='x')

        # self.warking_bay_canvas = tk.Canvas(self.warking_bay_display, highlightthickness=0,xscrollcommand=self.warking_bay_hbar.set, yscrollcommand=self.warking_bay_vbar.set)
        # self.warking_bay_canvas.pack(side=tk.TOP, fill='both', expand=True)
        # self.warking_bay_vbar.configure(command=self.warking_bay_canvas.yview)
        # self.warking_bay_hbar.configure(command=self.warking_bay_canvas.xview)



    def __init__(self):
        # parameters
        self.display_width = 900
        self.display_height = 600
        self.border = 10 # all borders
        self.overview_frame_width = self.display_width // 4  # working bay width

        #--------------------------------------------------

        # images loading
        self.filepath = ''
        self.files = []

        # overview
        self.threads = []

        # displays
        # self.display_currents = []
        # todo: notebook; list of currents

        #-------------------------------------------------------

        self.root = tk.Tk()

        self.create_widgets()
        self.bg = Image.open('bg.jpg')

        self.DummyHead = self.LinkedImages(0, Image.open('bg.jpg'), None, self)
        self.LinkedListEnd = self.DummyHead
        self.display_currents = self.DummyHead
        self.display_currentsTK = None
        self.loadCurrent()

        self.root.mainloop()

    def create_widgets(self):
        """"""""""""""""""""
        """widget declare"""
        """"""""""""""""""""

        # 1 root

        self.root.geometry('1280x720+100+100')
        self.root.title('dataset editor')
        self.root.iconbitmap("icon.ico")
        self.root.attributes('-alpha', 0.9)  # 透明度
        self.root.resizable(True, True)
        self.root_sizegrip = ttk.Sizegrip(self.root)
        self.root_sizegrip.pack(side=tk.RIGHT, anchor=tk.SE)
        self.panedwindow = tk.PanedWindow(relief=tk.SUNKEN,bd=self.border,sashrelief=tk.RAISED, sashwidth=self.border//2, showhandle=False)
        self.panedwindow.pack(fill='both', expand=True)

        # 1.1 menu bar
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)

        self.file_menu = tk.Menu(self.menu_bar,tearoff=False)
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

        self.overview_bottom = tk.Label(self.overview_frame,relief=tk.RAISED,text='things to be added')
        self.overview_bottom.pack(side=tk.BOTTOM, anchor=tk.SW, fill='x')

        # 1.2.2 scrollable overviews
        self.overview_scrollbar = tk.Scrollbar(self.overview_frame, orient=tk.VERTICAL, width=self.border*2)
        self.overview_scrollbar.pack(side=tk.RIGHT, fill='y')

        self.overview_canvas = tk.Canvas(self.overview_frame)
        self.overview_canvas.configure(yscrollcommand=self.overview_scrollbar.set)
        self.overview_canvas.pack(side=tk.TOP, fill='both', expand=True)

        self.overview_scrollbar.configure(command=self.overview_canvas.yview)

        # 1.2.2.1 scrollable frame
        self.overview_scroll_frame = tk.Frame(self.overview_canvas)
        self.overview_canvas.create_window((0, 0), window=self.overview_scroll_frame, anchor=tk.NW)
        self.overview_scroll_frame.bind("<Configure>", self.on_frame_configure)
        # self.overview_canvas.bind("<MouseWheel>", self.on_mousewheel)

        self.overview_canvas.bind('<Configure>',self.resizeOverview)
        self.root.bind('<ButtonRelease-1>',self.clearThreads)
        # self.overview_frame.bind('<B1-Motion>', self.resizeOverview)

        # 1.3 working bay
        self.working_bay_frame = tk.Frame(self.panedwindow, relief=tk.SUNKEN)
        self.panedwindow.add(self.working_bay_frame)

        # 1.3.1 display area

        # todo: placeholder for notebook
        # self.working_bay_tags = ttk.Notebook(self.working_bay_frame)
        # self.working_bay_tags.pack(side=tk.TOP, fill='both', expand=True)

        self.warking_bay_display = tk.Frame(self.working_bay_frame)
        self.warking_bay_display.pack(side=tk.TOP,anchor=tk.CENTER, fill='x', expand=True)

        self.photo_label = tk.Label(self.warking_bay_display, width=self.display_width, height=self.display_height)
        self.photo_label.pack(side=tk.TOP, fill='both', expand=True)



        # 1.3.2 operation area
        self.operation = tk.Frame(self.working_bay_frame,relief=tk.RIDGE,borderwidth=5)
        self.operation.pack(side=tk.TOP, anchor=tk.CENTER, fill='x', expand=True)
        # 1.3.2.1 info bar
        self.number_var = tk.StringVar()
        self.number_var.set("-_-")
        self.info_bar = tk.Label(self.operation, textvariable=self.number_var, bd=1, anchor=tk.CENTER)
        self.info_bar.pack(side=tk.TOP, anchor=tk.CENTER, fill='x', expand=True)
        # 1.3.2.2 buttons
        self.button_frame = tk.Frame(self.operation)
        self.button_frame.pack(side=tk.TOP, anchor=tk.CENTER) # side=tk.TOP, anchor=tk.CENTER, fill='x', expand=True

        self.prev_pic = tk.Button(self.button_frame, text='last',command=lambda: self.changePic(0))
        self.update_pic = tk.Button(self.button_frame, text='update',command=lambda: self.update())
        self.next_pic = tk.Button(self.button_frame, text='next',command=lambda: self.changePic(1))

        self.prev_pic.pack(side=tk.LEFT, anchor=tk.CENTER)
        self.update_pic.pack(side=tk.LEFT, anchor=tk.CENTER)
        self.next_pic.pack(side=tk.RIGHT, anchor=tk.CENTER)

    """"""""""""""""""""""""""""""""""""""""""""""""
    """other method (widget realization excluded)"""
    """"""""""""""""""""""""""""""""""""""""""""""""
    # image loarding --------------------------------------
    def loadImages(self): # todo: how to check for new and deleted images?
        if self.filepath:

            filetype = ('/*.jpg', '/*.jpeg', '/*.png', '/*.webp')

            if not self.DummyHead.next:
                for _type in filetype:
                    for picfilepath in glob.glob(self.filepath + _type):

                        self.files.append(picfilepath)

                        imgsize = int(self.overview_frame_width-self.border*1.5)

                        new_LinkedImg = self.LinkedImages(imgsize,Image.open(picfilepath),picfilepath,self)

                        self.LinkedListEnd.next = new_LinkedImg
                        new_LinkedImg.prev = self.LinkedListEnd
                        self.LinkedListEnd = new_LinkedImg
                # print(self.files)

            else:
                templist = []
                for _type in filetype:
                    for picfilepath in glob.glob(self.filepath + _type):
                        templist.append(picfilepath)

                # Identify elements removed from existing_list
                removed_elements = [elem for elem in self.files if elem not in templist]
                # Identify elements new to similar_list
                new_elements = {templist[templist.index(elem)-1]: elem for elem in templist if elem not in self.files}
                print(new_elements)
                self.files = templist

                curr = self.DummyHead.next
                while curr:
                    if curr.filepath in removed_elements:
                        remove = curr
                        curr = curr.next
                        self.removeNode(remove)
                        del remove
                    elif curr.filepath in list(new_elements.keys()):
                        imgsize = int(self.overview_frame_width - self.border * 1.5)
                        picfilepath = new_elements[curr.filepath]
                        new_LinkedImg = self.LinkedImages(imgsize,Image.open(picfilepath),picfilepath,self)
                        self.addNode(curr,new_LinkedImg)
                        curr = curr.next
                    else:
                        curr = curr.next

                # curr = self.DummyHead.next
                # while curr:
                #     if curr == self.display_currents:
                #         print('detected')
                #     print(curr)
                #     curr = curr.next


    def addNode(self,node:LinkedImages,newnode:LinkedImages):
        newnode.prev = node
        newnode.next = node.next

        if node.next:
            node.next.prev = newnode

        node.next = newnode

    def removeNode(self,node:LinkedImages):
        node.prev.next = node.next
        if node.next:
            node.next.prev = node.prev
        if self.display_currents == node:
            self.display_currents = node.next
        self.destroyPerFrame(node)


    def loadCurrent(self):
        self.display_currentsTK = self.resizeImage(self.display_currents.img, self.display_width, self.display_height)
        self.photo_label.configure(image=self.display_currentsTK)
        self.number_var.set(self.display_currents.filepath)

    def update(self):
        self.number_var.set('... of ...')
        self.loadImages()
        self.loadCurrent()
        self.number_var.set('updated!')

    def changePic(self,next):
        if self.DummyHead.next:
            if next:
                self.display_currents = self.display_currents.next if self.display_currents.next else self.DummyHead.next
            else:
                self.display_currents = self.display_currents.prev if not (self.display_currents.prev == (None or self.DummyHead)) else self.LinkedListEnd

        self.number_var.set(self.display_currents.filepath if self.display_currents.filepath else '-_-')
        self.loadCurrent()



    # image processing ---------------------------------------------------------
    def resizeImage(self,image,width,height):
        imageWidth, imageHeight = image.size
        return ImageTk.PhotoImage(image.resize((width,int((width/imageWidth)*imageHeight)) if imageWidth>imageHeight else (int((height/imageHeight)*imageWidth),height),Image.LANCZOS))

        # return ImageTk.PhotoImage(img)

    def resizePerOverview(self,pic,imgsize,frame): # create resize task for each overview subframe
        imgTK = self.resizeImage(pic, imgsize, imgsize)
        # frame.changeFramePic(img, imgsize)
        self.root.after(0, frame.changeFramePic, imgTK, imgsize)

    def threading(self,pic,imgsize,frame): # start thread of each resize task
        t = th.Thread(target=self.resizePerOverview, args=(pic,imgsize,frame))
        self.threads.append(t)
        t.start()

    def resizeOverview(self,event):
        self.overview_frame_width = event.width # slow
        if self.DummyHead.next:
            imgsize = int(self.overview_frame_width - self.border*1.5)
            curr = self.DummyHead.next
            while curr:
                self.threading(curr.img, imgsize, curr.frameCard)
                curr = curr.next

    def clearThreads(self,event):
        if self.threads:
            for t in self.threads:
                t.join()
            self.threads.clear()

    def destroyFrames(self):
        # todo: Linkedlist auto-destroys? del needed?
        curr = self.DummyHead.next
        self.DummyHead.next = None
        while curr:
            self.destroyPerFrame(curr)

            temp = curr
            curr = curr.next
            del temp

        self.LinkedListEnd = self.DummyHead
        self.display_currents = self.DummyHead
        self.display_currentsTK = None

    def destroyPerFrame(self,curr:LinkedImages):
        curr.frameCard.photoLabel.pack_forget()
        curr.frameCard.photoLabel.destroy()

        curr.frameCard.textLabel.pack_forget()
        curr.frameCard.textLabel.destroy()

        curr.frameCard.pack_forget()
        curr.frameCard.destroy()


    """""""""""""""""""""""
    """"widget function""""
    """""""""""""""""""""""

    # tool bar choices------------------------------------------

    def newCommand(self):
        pass

    def openFileCommand(self):
        pass

    def openFolderCommand(self):
        # todo: changable ini.dir; cancel removes everything
        newpath = fd.askdirectory(initialdir='D:/Downloads')
        if not (newpath == '' or self.filepath == newpath):
            self.filepath = newpath
            self.destroyFrames()
            self.update()

    def closeAllCommand(self):
        # todo: when closed, overview scroll bar still exist, canvas should be deleted?
        self.filepath = ''
        self.destroyFrames()
        self.update()

    # overview scrolling------------------------------------------

    def on_frame_configure(self,event):
        self.overview_canvas.configure(scrollregion=self.overview_canvas.bbox("all"))

    # def on_canvas_configure(self,event):
    #     pass

    def on_mousewheel(self,event):
        self.overview_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")




dataset_editor()












