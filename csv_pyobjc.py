import csv
import win32gui

# CSV形式でLOG保存関数
#引数(AUDIO_FILE_NAME:nameFormat【2021-01-01-10.10.55】, ResultList:認識結果, num:認識結果文字数, saveFileName:保存するファイルの名前, deviceNUM :MIXER=0,MIC=1)

class csv_pyobjc():
    
    def addwriteCsvTwoContents(self,AUDIO_FILE_NAME, ResultList:list, num, saveFileName,confidence, deviceNUM = 0):    
        month=AUDIO_FILE_NAME[5:7];day=AUDIO_FILE_NAME[8:10];hh=AUDIO_FILE_NAME[11:13];mm=AUDIO_FILE_NAME[14:16];ss=AUDIO_FILE_NAME[17:19]
        audioNameR=audioNameL=AUDIO_FILE_NAME
        CR0=CL0=CR=CL=""
        CR0Len=CL0Len=0
        file = open(saveFileName, 'a', encoding="utf_8", newline="")
        w = csv.writer(file)
        if not ResultList:
            print("R contents is not Recognize")
        else:
            CR0 = ResultList[0]
            CR = ResultList
            if(CR0 != 0):
                # print(conv.do(CR0))
                # CR0Len = int(len(CR0))
                CR0Len = num
        w = w.writerow([month+"/"+day, hh+":"+mm+":"+ss, audioNameR, CR, confidence, CR0Len, deviceNUM,self.get_winObjct()])
        file.close()

    def get_winObjct(self):
        # 実行時に操作されているアプリケーション名の取得
        activeWindowTitle = win32gui.GetWindowText(win32gui.GetForegroundWindow())
        return activeWindowTitle
        # return
    def readCsv(self, openFileName):
        micNUM = 0; mixNUM = 1   
        file = open(openFileName, 'r')
        data = csv.reader(file)
        for i, row in enumerate(data):
            for col in row:              
                if i==0:
                    micNUM = col
                else:
                    mixNUM = col
        file.close()
        DEVIC_NUMBER = (micNUM, mixNUM )
        return DEVIC_NUMBER
    