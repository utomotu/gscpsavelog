# https://www.odndo.com/posts/1627006679066/
# from logging import root
import threading
import tkinter 
from tkinter import Image, ttk, messagebox
from tkinter.constants import FALSE

import time
import datetime

from sqlalchemy import null
# import schedule
import queue
import os
import logging
from PIL import Image
from PIL import ImageTk

import recognition_for_gcp as stt
import label_object as lo
import csv_pyobjc

import os
import sys

MIC_INDEX = 1#USER側の入力デバイスインデックス
MIXER_INDEX = 2#PC側の入力デバイスインデックス

# 絶対パスを取得
authpath = os.path.abspath('../pythontkinter-332305-a72c4cd62fa2.json')
# returncode = os.system('set GOOGLE_APPLICATION_CREDENTIALS='+authpath)
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = authpath
# print(returncode)

SAVE_AUDIO = False #音源を保存するかしないか（ストレージ対策）
DIR_NAME = "../speech_to_text_2121040"
AUDIO_PATH = DIR_NAME+"/AUDIO_FILE/"
day = datetime.datetime.now().strftime('%Y-%m-%d')+"/"
AUDIO_DIR_PATH = DIR_NAME+"/AUDIO_FILE/"+day#音源を保存する場所
LOG_DIR_PATH = DIR_NAME+"/LOG_FILE/"#ログを保存する場所
SETTING_PATH = DIR_NAME+"/setting.txt"

# ディレクトリが存在しない場合、ディレクトリを作成する
if not os.path.exists(DIR_NAME):
    os.makedirs(DIR_NAME)
if not os.path.exists(AUDIO_PATH): 
    os.makedirs(AUDIO_PATH)
if not os.path.exists(LOG_DIR_PATH):
    os.makedirs(LOG_DIR_PATH)
if not os.path.exists(AUDIO_DIR_PATH):
    os.makedirs(AUDIO_DIR_PATH)
if not os.path.exists(SETTING_PATH):
    # ファイルが存在しなければ作成
    with open(SETTING_PATH, mode='w') as f:
        f.write(str(MIC_INDEX)+'\n'+str(MIXER_INDEX))
    f.close()

co = csv_pyobjc.csv_pyobjc()

ttsMIC = stt.Listen_print(MIC_INDEX,"USER", 1,AUDIO_DIR_PATH,LOG_DIR_PATH,SAVE_AUDIO)
ttsMIXER = stt.Listen_print(MIXER_INDEX,"PC",0,AUDIO_DIR_PATH,LOG_DIR_PATH,SAVE_AUDIO)


a = co.readCsv(SETTING_PATH)
MIC_INDEX = a[0]
MIXER_INDEX = a[1]

MIC_INDEX = ttsMIXER.USERINDEX
MIXER_INDEX = ttsMIXER.PCINDEX

num = 0 
class Display_result():
    def __init__(self):
        self.fontsize = 10;self.fontcolour = "black"
        self.num_comment = 3;self.alpha = 1;bold = "bold"

        self.root = tkinter.Tk()
        ww = self.root.winfo_screenwidth()
        self.label_window_width = ww/5                            #ラベルの幅
        print(self.label_window_width)

        self.wh = self.root.winfo_screenheight()
        self.root.wm_attributes("-topmost", True)               # ウインドウを最前面へ
        self.root.wm_attributes("-transparentcolor", "white")   # ウインドウを設定
        self.root.attributes("-alpha",self.alpha)               # 全オブジェクトの透過度を設定:1-0
        self.root.title("TranScriptoWindow")   
        # self.root.protocol("WM_DELETE_WINDOW",  lambda: on_closing(self.root))# windowを閉じれないようにする
        self.root.geometry(str(int(self.label_window_width))+"x"+str(int(self.wh))+"+"+str(int((ww-self.label_window_width)))+"+0") 
        f = ttk.Frame(master=self.root, style="TP.TFrame", width=ww, height=self.wh)
         
                     
        self.mic_progres = tkinter.StringVar()
        self.mixer_progres = tkinter.StringVar()
        tmp = ttsMIC.get_progress_result()
        self.mic_progres.set(tmp)
        tmp = ttsMIXER.get_progress_result()
        self.mixer_progres.set(tmp)
        font_size = [0,20,15,9]
        text_size =[0,13,31,int(len(self.mic_progres.get()))]
        self.prog = [null, null, null]
        self.prog [0]= tkinter.StringVar();self.prog [1]= tkinter.StringVar();self.prog [2]= tkinter.StringVar()
        
        self.label_fontsize =  [20,15,9]
        self.label_textsize =  [13,31,int(len(self.mic_progres.get()))]
        self.mic_progress_text_Value = [tkinter.StringVar(),tkinter.StringVar(),tkinter.StringVar()]
        self.mix_progress_text_Value = [tkinter.StringVar(),tkinter.StringVar(),tkinter.StringVar()]
        self.mic_label = [null,null,null]
        self.mix_label = [null,null,null]
        place_y = [100,145,175]
        self.mic_label_place = [(30,place_y[0]),(30,place_y[1]),(30,place_y[2])]
        self.mix_label_place = [(0,place_y[0]+200),(0,place_y[1]+200),(0,place_y[2]+200)]

        self.label_pack = []

        self.micob = lo.label_ob(self.root,"start_for", 12, self.mic_label_place,self.label_window_width,"black",'#fafad2')
        self.mixob = lo.label_ob(self.root,"start_for_mix", 12,self.mix_label_place,self.label_window_width,'#FFFAFA',"darkcyan")
        self.comic=self.comix=0  
        # self.label_pack.append(self.micob )
        # self.label_pack.append(self.mixob )
        def add_label(text="", fontsize=1):
            mxla=self.mixob.get()
            mxhh = mxla[2].winfo_height()
            mxy = mxla[2].winfo_y( )
            global num
            for i, la in enumerate(self.label_pack):
                try:
                    for_label = self.label_pack[i+1]
                    hh = for_label[2].winfo_height()
                    y = for_label[2].winfo_y( )
                    la.move(y+hh)
                except BaseException as e:
                    l = la.get()
                    hh = l[2].winfo_height()
                    y = l[2].winfo_y( )
                    la.move_label(y+hh)
            dd =lo.label_ob(self.root,text,fontsize ,self.mix_label_place,self.label_window_width)
            dd.pp(0,mxy+mxhh)
            self.label_pack.append(dd)

        # self.schedule_s(add_label) 
 
        # backgroundカラーに設定されたオブジェクトを完全透過する
        ttk.Style().configure("TP.TFrame", background="white")
        f.pack() 
    #option_windowの設定        
        self.option_window = tkinter.Tk()
        self.option_window.wm_attributes("-topmost", True)
        self.option_window.geometry("300x300+"+str(int(ww/2-300/2))+"+"+str(int(self.wh/2-300/2)))
        self.option_window.title("Settings")

        # op=lo.setting_gui()
            
        lfontsize = ttk.Label(self.option_window, text="学籍番号", wraplength=ww)
        # lfontsize.pack()
        self.studentNum = tkinter.Entry(self.option_window, width=20)
        self.studentNum.insert(tkinter.END, "b2222000")
        """
        canvas = tkinter.Canvas(self.option_window)
        canvas.pack(expand = True, fill = tkinter.BOTH)
        # キャンバスのサイズを取得
        self.option_window.update() # Canvasのサイズを取得するため更新しておく
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
        # 画像ファイルを開く（対応しているファイルフォーマットはPGM、PPM、GIF、PNG）
        # photo_image = tkinter.PhotoImage(file = 'sys_sound_.png', master=self.option_window)
        
        photo_image = Image.open('sys_sound_.png')
        photo_image.resize((5, 5),Image.ANTIALIAS)
        photo_image = ImageTk.PhotoImage(photo_image, master=self.option_window)
        # canvas.place(x=100, y=350) 
        
        # 画像の描画
        canvas.create_image(10, 10, image=photo_image)#表示画像データ)
    
        def next_img():
            canvas.place(x=0, y=0)
            # photo_image = tkinter.PhotoImage(file = 'sys_sound_.png', master=self.option_window)
            photo_image = Image.open('sound_input_output.png')
            photo_image.resize((5, 5),Image.ANTIALIAS)
            photo_image =  ImageTk.PhotoImage(photo_image, master=self.option_window)
            # photo_image = tkinter.PhotoImage(file = 'sound_input_output.png', master=self.option_window)
            # 画像の描画
            canvas.create_image(canvas_width / 2+100, canvas_height / 2, image=photo_image, anchor=tkinter.N)#表示画像データ)
            # canvas.place(x=300, y=350) 
        # # 「次に」ボタン
        button_draw = tkinter.Button(self.option_window , text=u'消す',width=15)
        button_draw.bind("<Button-1>", next_img)
        button_draw.place(x=350,y=350)
        # # self.studentNum.pack()
        
        """
        # ラベル
        lbl = tkinter.Label(self.option_window,text='USERのデバイスインデックス')
        self.label_m=tkinter.Label(self.option_window,text="接続デバイス")
        
        self.index_mic_box = tkinter.Entry(self.option_window,width=20)
        self.index_mic_box.insert(0,str(MIC_INDEX))
        
        lbl.pack()
        self.index_mic_box.pack()
        self.label_m.pack()

        # ラベル
        lbl = tkinter.Label(self.option_window,text='PCのデバイスインデックス')
        self.txt = tkinter.Entry(self.option_window,width=20)
        self.txt.insert(0,str(MIXER_INDEX))

        self.text_mx = tkinter.StringVar()
        self.text_mx.set("a")
        self.label_mx=tkinter.Label(self.option_window,text='接続デバイス')
        lbl.pack()
        self.txt.pack()
        self.label_mx.pack()
        
        btn = ttk.Button(self.option_window, text="Start Recognize", command=self.start_btn)
        applybtn = ttk.Button(self.option_window, text="Stop", command=self.stop_btn)  
        applybtn.pack(side=tkinter.BOTTOM,anchor=tkinter.W)
        btn.pack(side=tkinter.BOTTOM,anchor=tkinter.W)
        
        # スケールバー～ラベル位置（オプションをいくつか設定）
        self.scale_var = tkinter.IntVar()
        fontsiza_sv = tkinter.Scale(
                    self.option_window, 
                    variable = self.scale_var, 
                    command = self.slider_scroll,
                    # orient=tkinter.HORIZONTAL,   # 配置の向き、水平(HORIZONTAL)、垂直(VERTICAL)
                    length = 100,           # 全体の長さ
                    width = 15,             # 全体の太さ
                    sliderlength = 20,      # スライダー（つまみ）の幅
                    from_ = -50, to = 700, # 最小値（開始の値 # 最大値（終了の値）
                    resolution=1,           # 変化の分解能(初期値:1)
                    tickinterval=0,        # 目盛りの分解能(初期値0で表示なし)
                    showvalue=False,        # スライダー上の値を非表示にする
                    label = "ラベル位置"
                    )
        # fontsiza_sv.pack(side=tkinter.LEFT)
         
        # # スケールバー～ラベル位置２（オプションをいくつか設定）（オプションをいくつか設定）
        self.scale_mic = tkinter.IntVar()
        fontsiza_sv= tkinter.Scale(
                    self.option_window, 
                    variable = self.scale_mic, 
                    command = self.slider_mic,
                    # orient=tkinter.HORIZONTAL,   # 配置の向き、水平(HORIZONTAL)、垂直(VERTICAL)
                    length = 100,           # 全体の長さ
                    width = 15,             # 全体の太さ
                    sliderlength = 20,      # スライダー（つまみ）の幅
                    from_ = -50, to = 700, # 最小値（開始の値 # 最大値（終了の値）
                    resolution=1,           # 変化の分解能(初期値:1)
                    tickinterval=0,        # 目盛りの分解能(初期値0で表示なし)
                    showvalue=False,        # スライダー上の値を非表示にする
                    label = "二つ目",
                    )
        # fontsiza_sv.pack(side=tkinter.LEFT)
        
        # # スケールバー～透過度（オプションをいくつか設定）（オプションをいくつか設定）
        self.scale_alfa = tkinter.DoubleVar()
        self.scale_alfa.set(1.0)
        fontsiza_sv = tkinter.Scale(
                    self.option_window, 
                    variable = self.scale_alfa, 
                    command = self.slider_alfa,
                    # orient=tkinter.HORIZONTAL,   # 配置の向き、水平(HORIZONTAL)、垂直(VERTICAL)
                    length = 100,           # 全体の長さ
                    width = 15,             # 全体の太さ
                    sliderlength = 20,      # スライダー（つまみ）の幅
                    from_ = 0, to = 1, # 最小値（開始の値 # 最大値（終了の値）
                    resolution=0.05,           # 変化の分解能(初期値:1)
                    tickinterval=0.5,        # 目盛りの分解能(初期値0で表示なし)
                    showvalue=False,        # スライダー上の値を非表示にする
                    label = "ラベル透過度"
                    )
        
        # fontsiza_sv.pack(side=tkinter.LEFT)

        # self.pc_sound_setting()
        # self.option_window.mainloop()
        self.root.mainloop()
    """
    def schedule_s(self, event):    
        global num
        num = num +1
        # 定期実行したい操作をまとめた関数
        schedule.every(60).seconds.do(event) # 10分毎  
    """

    def slider_scroll(self, event=0):
        '''スライダーを移動したとき'''
        self.scale_var.set(event)
        
        self.mixer_label.place(x=0, y=(100-self.num_comment*20-self.alpha)+int(self.scale_var.get()))  # -αは下のタスクバーの分
        # for i in range(3):
        #     self.mic_label[i].place(x=self.mic_label_place[i][0],y=self.mic_label_place[i][1]+num*3+int(self.scale_var.get()))
    
    def slider_mic(self, event=0):
        '''スライダーを移動したとき'''
        self.scale_mic.set(event)
        self.mic_label[0].place(x=0, y=(200-self.num_comment*20-self.alpha)+int(self.scale_mic.get()))  # -αは下のタスクバーの分

    def slider_alfa(self, event=0):
        self.scale_alfa.set(event)
        self.root.attributes("-alpha",self.scale_alfa.get())
     
    # リアルタイムに認識結果を可視化させる処理 並列処理されているrecognition_for_gcp.pyから認識に値を取得する
    def update_stt_result(self):
        # tmp = str(ttsMIC.get_connected_device())
        # self.label_m.config(text = tmp)
        # tmp = ttsMIXER.get_connected_device()
        # self.label_mx.config(text =tmp)
        
        #リアルタイムに認識結果を可視化させる
        tmp = ttsMIC.get_progress_result()
        self.micob.set_text_value(tmp)
        tmp = ttsMIXER.get_progress_result()
        self.mixob.set_text_value(tmp)

        #確定した認識結果を追加していくラベル　現在は使用していない
        def display_result_on_textbox(ttsObject, text_color,backcolor):
            mxla=self.mixob.get()
            mxhh = mxla[2].winfo_height()
            mxy = mxla[2].winfo_y( )
            for i, la in enumerate(self.label_pack):
                try:
                    for_label = self.label_pack[i+1]
                    hh = for_label[2].winfo_height()
                    y = for_label[2].winfo_y( )
                    la.move(y+hh)
                except BaseException as e:
                    l = la.get()
                    hh = l[2].winfo_height()
                    y = l[2].winfo_y( )
                    la.move_label(y+hh)
                    # print("Exception occurred - {}".format(str(e)))  
                    # print("on_error_sstupdate")
                    # print(e)
            dd =lo.label_ob(self.root,ttsObject.get_result(),2 ,self.mix_label_place, self.label_window_width,text_color, backcolor)
            dd.pp(0,mxy+mxhh)
            self.label_pack.append(dd)
            
        #リアルタイムに認識していた結果が確定した瞬間処理を行う
        if(ttsMIXER.get_condition()):
            self.comix+=1
            self.mixerttmp = ttsMIXER.get_chrCount()
            # display_result_on_textbox(ttsMIXER,'#FFFAFA',"darkcyan") 

        if(ttsMIC.get_condition()):
            self.comic+=1
            self.mixerttmp = ttsMIC.get_chrCount()
            # self.add_label()
            # display_result_on_textbox(ttsMIC,"black",'#fafad2') # 今回はスルー過去ラベルを可視化していく
            # schedule.run_pending()
        
        # -- def update_stt_result(self)-- 処理をもう一度する．ループ的な役割
        self.root.after(ms=10, func=self.update_stt_result)
    
    # ストップボタンを押したときの処理 -> プログラムを終了させる
    def stop_btn(self):
        ttsMIXER.set_stt_status(False)
        ttsMIC.set_stt_status(False)
        self.option_window.destroy()
        self.root.destroy()
    
    # スタートボタンを押したときの処理 -> 設定されたデバイスで認識を開始する
    def start_btn(self):
        # テキストボックス内の値を取得
        index1=self.index_mic_box.get()
        ttsMIC.set_stt_device_index(index1)
        index2=self.txt.get()
        ttsMIXER.set_stt_device_index(index2)
        with open(SETTING_PATH, mode='w') as f:
            f.write(str(index1)+'\n'+str(index2))
            f.close()
        # sttの初期化
        ttsMIC._init_object()
        ttsMIXER._init_object()

        t1 = threading.Thread(name='USER(MIC)_RECOGNIZE_THREAD', target=ttsMIC.start_recognize, daemon=True)
        t1.start()
        time.sleep(5)#これを入れないとpysimpleGUIのWindowがクラッシュする
        t2 = threading.Thread(name='PC(MIXER)_RECOGNIZE_THREAD', target=ttsMIXER.start_recognize, daemon=True)
        t2.start()
        time.sleep(5)
        
        tmp = str(ttsMIC.get_connected_device())
        # print(tmp+"aaa")
        self.label_m.config(text = tmp)
        tmp2 = str(ttsMIXER.get_connected_device())
        self.label_mx.config(text = tmp2)

        thread_dict=dict()
        error_queue = queue.Queue()
        # thread_dict[name] = ExcThread(error_queue, name)
        ttsMIC.set_progress_result("【・・】")
        ttsMIXER.set_progress_result("【・・】")
        
        self.root.after(1, self.update_stt_result)# self.update_stt_resultに移動する

        # subf.destroy()
        device_INDEX_MIKISER = 0
        device_INDEX_MIC = 2

if __name__ == '__main__':
    # draw_window()
    aa = Display_result()