import datetime
import re
from google.cloud import speech_v1 as speech
# from google.cloud import speech_v1 storage
# from google.cloud import speech

import pyaudio
import queue
import wave
from pykakasi import kakasi
import csv_pyobjc

# DEVICE_INDEX  = 2
# 使用可能なデバイスインデックスがプリントする方法
# line180e前後の stream._print_deviceList() のコメントアウトを外す
# 自身の実行環境で以下のインデックス番号を変更すると良い(デフォルトは1)
# おそらくだが「既定のマイク」->　DEVICE_INDEX = 1
# 「既定の通信マイク」->　DEVICE_INDEX = 2

# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms
# pyAudiosample
FORMAT = pyaudio.paInt16
kakasi = kakasi()
co = csv_pyobjc.csv_pyobjc()

class _MicrophoneStream(object):
    """Opens a recording stream as a generator yielding the audio chunks."""

    def __init__(self, rate, chunk, device_index,AUDIO_FILE_PATH, save_audio):
        self._rate = rate 
        self._chunk = chunk
        self._DEVICE_INDEX  = device_index
        self._WAVE_OUTPUT_FILENAME = AUDIO_FILE_PATH

        # Create a thread-safe buffer of audio data
        self._buff = queue.Queue()
        self.closed = True
        # Save Audio Buff
        self._frames = []
        self._save_audio = save_audio
        self._DEVICE_NAME = "none"

        self.USERINDEX = 0
        self.PCINDEX = 0

    # _MicrophoneStream開始したら実行される:default
    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        # 接続されたデバイスの表示
        for x in range(0, self._audio_interface.get_device_count()):
            if x==self._DEVICE_INDEX:
                self._DEVICE_NAME ="接続デバイス【index"+str(x)+":"+self._audio_interface.get_device_info_by_index(x).get("name")+"】"
                print(self._DEVICE_NAME)
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            # The API currently only supports 1-channel (mono) audio
            # https://goo.gl/z757pE
            channels=1,
            rate=self._rate,
            input=True,
            frames_per_buffer=self._chunk,
            # デバイスのマイク設定する
            input_device_index=self._DEVICE_INDEX,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't

            # overflow while the calling thread makes network requests, etc.
            stream_callback=self._fill_buffer,
        )
        self.closed = False

        return self

    #_MicrophoneStream が終了したら実行される:default
    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self._buff.put(None)
        self._audio_interface.terminate()
        def _save_audio():
            # save wav failes
            wf = wave.open(self._WAVE_OUTPUT_FILENAME, 'wb')
            wf.setnchannels(1)
            wf.setsampwidth(self._audio_interface.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(self._frames))
            wf.close()
        if(self._save_audio):
            _save_audio()
            # t1 = threading.Thread(target=_save_audio, daemon=True)
            # t1.start()
            
    # :default
    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """Continuously collect data from the audio stream, into the buffer."""
        self._buff.put(in_data)
        return None, pyaudio.paContinue
    # :default
    def generator(self):
        
        while not self.closed:
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            # Now consume whatever other data's still buffered.
            while True:
                try:
                    # Add Audio file
                    self._frames.append(chunk)
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b"".join(data)
    
    # 音声の保存先を指定:create
    def _set_audio_file_path(self, file_name):
        self._WAVE_OUTPUT_FILENAME = file_name
    
    # 発話前の無音部分をカットしておく:create
    def clear_audio_file(self):
        
        if(len(self._frames)-7>0):
            del self._frames[:len(self._frames)-7]
        else:
            self._frames.clear()
    
    # 音声に関係するデバイスを一覧表示する（必ずしもinput側がでるとは限らない）:create
    def print_connected_deviceList(self):# 
        audio = pyaudio.PyAudio()
        print("【オーディオデバイス一覧】")
        for x in range(0, audio.get_device_count()):
            devicename = audio.get_device_info_by_index(x).get("name")  
            
            if("VoiceMeeter Aux Output (VB-Audi"==devicename):
                print("☆PCインデックス"+str(x)+":"+devicename)
                self.USERINDEX = int(x)
                
            elif("VoiceMeeter Output (VB-Audio Vo"==devicename):
                print("☆USERインデックス"+str(x)+":"+devicename)
                self.PCINDEX = int(x)
                
            else:
                print("index"+str(x)+":"+devicename )
                

    # _MicrophoneStreamに接続している音声デバイスを取得する:create
    def get_connected_device(self):
        return self._DEVICE_NAME 

class Listen_print(object):
    def __init__(self, deviceindex, deviceNAME, deviceNumber, audio_dir_path, log_dir_path, SAVE_AUDIO):
        self._DEVICE_INDEX =  deviceindex
        self._DEVICENAME_AND_NUMBER = (deviceNAME, deviceNumber)
        self.CONNECTED_DEVICE_NAME =""
        # 確定した認識結果
        self._return_result = "【スタートボタンを押すと認識がはじまります】"
        # 認識を開始した時刻
        self._date = "00/00/00"
        # 認識途中の結果
        self._progress_result = "【スタートボタンを押すと認識がはじまります】"
        # 確定した認識結果の総テキスト量
        self._chrCount = 0
        # 認識途中の総テキスト量
        self._monoChrCount = 0  
        # 認識が リアルタイムに認識中:false OR 認識が確定した瞬間:true
        self.condition = False 
        # 認識が確定する度にsstを終了させるフラグ
        self.stt_status  = True #sstのwhile抜ける用
        self._AUDIO_DIR_PATH = audio_dir_path
        self._LOG_DIR_PATH = log_dir_path
        self._save_audio = SAVE_AUDIO
        self.USERINDEX = 0
        self.PCINDEX = 0
        if(deviceNAME=="PC"):
            b=_MicrophoneStream(RATE, CHUNK, 1, "AUDIO_FILE_PATH", False) 
            b.print_connected_deviceList()
            self.USERINDEX = b.USERINDEX 
            self.PCINDEX = b.PCINDEX
         
        log_file_path = self._LOG_DIR_PATH + datetime.datetime.now().strftime('%Y-%m-%d')+".csv"
 
    def start_recognize(self):
        # See http://g.co/cloud/speech/docs/languages
        # for a list of supported languages.
        # 認識の言語は日本語に変更している
        print("start"+self._DEVICENAME_AND_NUMBER[0])
        language_code = "ja-JP" # a BCP-47 language tag "en-US"

        client = speech.SpeechClient()
        # https://cloud.google.com/speech-to-text/docs/reference/rest/v1/RecognitionConfig
        # if(self._DEVICENAME_AND_NUMBER[0]=="PC"):
        #     MODEL = "latest_long"
        #     print("model:"+MODEL)
        #     # 日本語対応なし -> vido
        # else:
        #     MODEL = "default"
        #     print("model:"+MODEL)
        MODEL = "latest_long"
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=RATE,
            language_code=language_code,
            # enableWordTimeOffsets = True,
            model = MODEL,        
        )

        _streaming_config = speech.StreamingRecognitionConfig(
            config=config, interim_results=True
        )
        # 認識待機が開始された時刻を取得
        now = datetime.datetime.now()
        AUDIO_FILE_NAME = now.strftime('%Y-%m-%d-%H.%M.%S')+self._DEVICENAME_AND_NUMBER[0]+".wav"
        AUDIO_FILE_PATH = self._AUDIO_DIR_PATH + AUDIO_FILE_NAME
        
        while True:
            # 認識待機状態の時一度だけ実行される
            with _MicrophoneStream(RATE, CHUNK, self._DEVICE_INDEX, AUDIO_FILE_PATH, self._save_audio) as stream:
                num_chars_printed = 0
                audio_generator = stream.generator()# 
                requests = (
                    speech.StreamingRecognizeRequest(audio_content=content)
                    for content in audio_generator
                )
                print("..."+self._DEVICENAME_AND_NUMBER[0]+" 認識待機中")
                # print("safaaa"+str(stream.get_connected_device()))
                try:
                    # "認識が開始された瞬間1回だけ実行される To "for response in responses: 
                    responses = client.streaming_recognize(config=_streaming_config, requests=requests)
                    stream.clear_audio_file()# _MicrophoneStream開始から認識が開始されるまでの無音とみなされている音声ストリームを削除
                    # 再度認識が開始された瞬間の時刻を取得
                    now = datetime.datetime.now()
                    self._date = now.strftime('%Y-%m-%d-%H.%M.%S')
                    AUDIO_FILE_NAME = now.strftime('%Y-%m-%d-%H.%M.%S')+self._DEVICENAME_AND_NUMBER[0]+".wav"
                    AUDIO_FILE_PATH = self._AUDIO_DIR_PATH+AUDIO_FILE_NAME
                    # 音声の保存は_MicrophoneStream側なため、そちらでの保存準備
                    stream._set_audio_file_path(AUDIO_FILE_PATH)
                    print(AUDIO_FILE_PATH)
            
                    num_chars_printed = 0
                    max_recognize_text_columns =  0
                    for response in responses:                      
                        if not response.results:                       
                            continue
                        # The `results` list is consecutive. For streaming, we only care about
                        # the first result being considered, since once it's `is_final`, it
                        # moves on to considering the next utterance.
                        result = response.results[0]
                        if not result.alternatives:  
                            continue

                        # Display the transcription of the top alternative.
                        transcript = result.alternatives[0].transcript
                        confidence = result.alternatives[0].confidence
                        overwrite_chars = "*" * (num_chars_printed - len(transcript))

                        if not result.is_final: # リアルタイムでの認識中の処理:is_final = False
                            # sys.stdout.write(transcript + overwrite_chars + "\r")
                            # sys.stdout.flush()
                            num_chars_printed = len(transcript)                                        
                            if max_recognize_text_columns <= len(transcript):#sttからたまに古い情報がかえってくるためそれの回避
                                max_recognize_text_columns = len(transcript)
                                self._progress_result = transcript + overwrite_chars
                                kakasi.setMode('J', 'H') #漢字からひらがなに変換
                                # kaka.setMode("K", "H") #カタカナからひらがなに変換
                                conv = kakasi.getConverter()
                                # 認識途中のテキスト量を保存
                                tmp = self._monoChrCount
                                self._monoChrCount = len(conv.do(transcript))
                                self._chrCount += self._monoChrCount-tmp
                                tmp = self._monoChrCount

                        else:# 認識が確定した瞬間一度だけ実行される:is_final = True
                            # print(result)
                            self.condition = True
                            print(self._DEVICENAME_AND_NUMBER[0]+":確定認識結果："+transcript + overwrite_chars)
                            self._return_result = transcript + overwrite_chars
                            self._progress_result = transcript + overwrite_chars
                            self._chrCount += self._monoChrCount-tmp                      
                            self._monoChrCount = 0
                            
                            kakasi.setMode('J', 'H') #漢字からひらがなに変換
                            # kaka.setMode("K", "H") #カタカナからひらがなに変換
                            conv = kakasi.getConverter()
                            num = len(conv.do(transcript))
                                                    
                            # filename = LOG_DIRECTORY+self.studentNum.get()+datetime.datetime.now().strftime('%Y-%m-%d')+'log.csv'
                            log_file_path = self._LOG_DIR_PATH + datetime.datetime.now().strftime('%Y-%m-%d')+".csv"
                            # CSVファイル形式で確定した認識結果などログの保存
                            co.addwriteCsvTwoContents(AUDIO_FILE_NAME, self._return_result, num, log_file_path, confidence, self.get_deviceName_or_number(0))
                            if re.search(r"\b(exit|quit)\b", transcript, re.I):
                                print("Exiting..")
                                break
                            # breakすることで一度"for分をbresk _MicrophoneStream()"を閉じて音声を保存　Whileで認識を再開する
                            self._init_object()
                            break                            
                        if (self.stt_status==False):
                            break
                            num_chars_printed = 0
                except TimeoutError as e:
                    print(str(e))
                except BaseException as e:
                    print("Exception occurred - {}".format(str(e)))
                    # print("3分間無音の状態だったため認識エンジンをリセットします")
                    AUDIO_FILE_PATH = self._AUDIO_DIR_PATH+AUDIO_FILE_NAME
                    stream._set_audio_file_path(AUDIO_FILE_PATH)
                    self._return_result = ""
                    self._progress_result = ""
                    self._init_object()
                    # 待機時間が305sを超えて無音のまますぎたため，それまでの音声ストリームを削除
                    # stream.clear_audio_file()
            #認識が停止された
            if (self.stt_status==False):
                self._return_result = "【☆スタートボタンを押すと認識がはじまります】"
                self._progress_result = "【☆スタートボタンを押すと認識がはじまります】"
                self.condition = True
                print("確定認識結果："+transcript + overwrite_chars)
                self._return_result = transcript + overwrite_chars
                self._progress_result = transcript + overwrite_chars
                kakasi.setMode('J', 'H') #漢字からひらがなに変換
                # kaka.setMode("K", "H") #カタカナからひらがなに変換
                conv = kakasi.getConverter()
                # self._chrCount += len(conv.do(transcript))
                # 認識文字数を保存
                self._monoChrCount = len(conv.do(transcript))
                break
    def _init_object(self):
        # self._monoChrCount = 0
        self._progress_result = "【・・・】"
        # self._return_result = "【☆☆はじまり】"
        self._date = "00/00/00"
        self.condition = False
        self.stt_status = True

    def get_result(self):# 認識確定した文字起こしデータ
        return self._return_result
    def get_progress_result(self):# リアルタイムに認識されている文字起こしデータ
        return self._progress_result 
    def set_progress_result(self, contents):# リアルタイムに認識されている文字起こしデータ
        self._progress_result = contents
    def get_date(self):
        return self._date
    def get_condition(self):
        return self.condition
    def set_condition(self,bool):
        self.condition = bool
        # self._monoChrCount = 0
    def get_deviceName_or_number(self,int):#デバイスの名前の取り出し：MIC or MIXER
        return self._DEVICENAME_AND_NUMBER[int]
    def get_chrCount(self):#円グラフ用：総発話文字数の取り出し用
        return self._chrCount
    # def set_chrCount(self, chrCount):#円グラフ用：総発話文字数の取り出し用
    #     self._chrCount = chrCount
    def get_monoChrCount(self):#棒グラフ用：都度発話数の取り出し用
        return self._monoChrCount
    def set_stt_status(self, bool):#
        self.stt_status = bool
    def set_stt_device_index(self, index):#
        self._DEVICE_INDEX =  int(index)
    def get_connected_device(self):#
        return self.CONNECTED_DEVICE_NAME
    def _set_connected_device(self, name):
        self.CONNECTED_DEVICE_NAME=name
        
if __name__ == "__main__":
    # Listen_print()は 以下のどちらかを使用
        # deviceNAMEが"mixer"ならdeviceNumber = 0
        # deviceNAMEが"mic"ならdeviceNumber = 1
    # 使用可能なデバイスの表示するには以下2行のコメントアウトを消す
    b=_MicrophoneStream(RATE, CHUNK, 1, "AUDIO_FILE_PATH", False) 
    b.print_connected_deviceList()
    # a = Listen_print(deviceindex=15, deviceNAME="mix", deviceNumber=0, audio_dir_path="", log_dir_path="", SAVE_AUDIO=False)
    # a.start_recognize()

    