import tkinter 
from sqlalchemy import null

class label_ob(object):
    def __init__(self, root=null, teV="",fontSize=1, place=null,label_w=0, fontcolour = "black", backcolour="#fafad2"):
        self.x= self.y= 0
        self.label_fontsize =  [20,15,9]
        self.label_fontsize =  [5,5,5]
        self.label_textsize =  [13,31,int(len(teV))]
        self.label_textsize =  [300,300,300]
        self.mic_progress_text_Value = [tkinter.StringVar(),tkinter.StringVar(),tkinter.StringVar()]
        self.mix_progress_text_Value = [tkinter.StringVar(),tkinter.StringVar(),tkinter.StringVar()]
        place_y = [100,145,175]
        self.label_place = place
        self.mic_label = [null,null,null]
        # self.mix_label_place = [(0,place_y[0]+200),(0,place_y[1]+200),(0,place_y[2]+200)]
        hh = 26
        y = 0
        # self.call
        for i in range(3):
            self.mic_progress_text_Value[i].set(str(i)+"aiu")
            self.mic_label[i] = tkinter.Label(
                root,
                # text=self.mic_progress_text_Value[i],
                text = teV,
                wraplength=label_w,
                # wraplength=50,
                # font=("メイリオ", self.label_fontsize[i], "bold"),
                font=("メイリオ", fontSize, "bold"),
                # foreground=self.fontcolour,
                foreground=fontcolour,
                background= backcolour, #'#fafad2', #red
                # anchor=tkinter.W,
                justify="right"
                )
            # hh = self.mic_label[i].winfo_height()
            # y = self.mic_label[i].winfo_y( )
            # print(self.gethh())
            # self.mic_label[i].place(x=self.label_place[i][0],y=hh+y)
            # self.mic_label[i].place(x=0,y=hh+y)
            # hh = self.mic_label[i].winfo_height()
            # y = self.mic_label[i].winfo_y( )
            # print(hh,y)
            self.mic_label[i].pack(side = 'top', anchor = tkinter.E)

    def pp(self, x=0,y=10):
        # self.m_label.place(x=20,y=10)
        self.x=x
        self.y=y
        for la in self.mic_label:
            la.place(x=x,y=y)
            # self.mic_label[i].place(x=10,y=self.label_place[i][1]+100)
            # self.mic_label[i].pack(side = 'top', anchor = tkinter.E)

    def get(self):
        return self.mic_label
    def gethh(self):
        return self.mic_label[0].winfo_height()

    #ラベルウィジェットを削除
    def label_destroy(self):
        for la in self.mic_label:
            la.destroy()
    
    def move_label(self, y=20):
        for la in self.mic_label:
            # self.y = self.y-y
            la.place_configure(y=y)
            # la.config(winfo_y = self.y)s

    def set_text_value(self,text):
        self.mic_label[0].config(text=text[0:self.label_textsize[1]])
        self.mic_label[1].config(text=text[self.label_textsize[0]:self.label_textsize[1]])
        self.mic_label[2].config(text=text[self.label_textsize[1]:])