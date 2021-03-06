
import wave, struct, math
import sounddevice as sd
from scipy import signal as sg
from scipy.fftpack import fft, ifft
import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf
from itertools import zip_longest 

'''
- Mensagem :
    - ler dois arquivos .wav, essas serão as mensagens (m1(t), m2(t)) a serem transmitidas.
- Portadoras :
    - receber como parâmetro as frequências das portadoras (f1, f2)
- Modulação :
    - modular em AM (ou FM) as mensagens m1 e m2 nas frequências f1 e f2
- Transmissão :
    - transmitir o sinal modulado em áudio resultante de m1,f1 e m2,f2
- Exibir :
    - os sinais (mensagens) a serem transmitidas no tempo
    - os Fourier dos sinais (frequência)
    - as portadoras no tempo
    - as mensagens moduladas no tempo
    - os Fourier das mensagens moduladas (frequência)
'''

class Transmitter:
    def __init__(self):
        self.fcut = 4000
        self.fs = 44100
        self.m1 = "trabson.wav"
        self.m2 = "raphorba.wav"
        self.fc1 = 5000
        self.fc2 = 15000

    def calcFFT(self, signal):
        N  = len(signal)
        T  = 1/self.fs
        xf = np.linspace(0.0, 1.0/(2.0*T), N//2)
        yf = fft(signal)
        return(xf, yf[0:N//2])
    
    def make_plot(self, x, y, title):
        # y_db = []
        fig = plt.figure()
        # ymax = 20000
        # for value in y:
        #     new_value = 10*math.log(value/ymax)
        #     y_db.append(new_value)

        # plt.plot(x, y_db)
        plt.plot(x, y)
        # plt.axis([0,self.fcut+100,0,max(y)+10])
        plt.grid(True)
        plt.ylabel("")
        plt.xlabel("")
        plt.title(title)
        plt.show()

    def make_carrier_plot(self, x, y, j, k):
            # y_db = []
        fig = plt.figure()
        # ymax = 20000
        # for value in y:
        #     new_value = 10*math.log(value/ymax)
        #     y_db.append(new_value)

        # plt.plot(x, y_db)
        plt.plot(x, y)
        plt.plot(j, k)
        # plt.axis([0,self.fcut+100,0,max(y)+10])
        plt.grid(True)
        plt.ylabel("Decibéis (dB)")
        plt.xlabel("Frequência (Hz)")
        plt.title("Modulação AM")
        plt.show()

    def LPF(self, signal, cutoff_hz, fs):
        #####################
        # Filtro
        #####################
        # https://scipy.github.io/old-wiki/pages/Cookbook/FIRFilter.html
        nyq_rate = fs/2
        width = 5.0/nyq_rate
        ripple_db = 60.0 #dB
        N , beta = sg.kaiserord(ripple_db, width)
        taps = sg.firwin(N, cutoff_hz/nyq_rate, window=('kaiser', beta))
        return(sg.lfilter(taps, 1.0, signal))

    def play(self, audio, samplerate):
        sd.play(audio, samplerate)
        sd.wait()

    def sumTwoLists (self, a, b):
        soma = [x + y for x, y in zip_longest(a, b, fillvalue=0)]
        return soma

    def main(self):
        #Importando e lendo os arquivos de áudio
        m1, m1_samplerate = sf.read(self.m1)
        m2, m2_samplerate = sf.read(self.m2)
        m1 = m1[:,0]
        m2 = m2[:,0]
        print("Áudio 1: " + self.m1)
        print("Tamanho do áudio: ", len(m1))
        print("Sample rate do áudio: ", m1_samplerate)
        print("Áudio 2: " + self.m2)
        print("Tamanho do áudio: ", len(m2))
        print("Sample rate do áudio: ", m2_samplerate)
        
        # Reproduzindo os audios a serem transmitidos
        # self.play(m1, m1_samplerate)
        # self.play(m2, m2_samplerate)


        #Aplicando o filtro passa baixa
        m1_filtrado = self.LPF(m1, self.fcut, m1_samplerate)
        m2_filtrado = self.LPF(m2, self.fcut, m2_samplerate)

        #Aplicando o Fourier nos sinais filtrados
        # m1_fftx, m1_ffty = self.calcFFT(m1_filtrado)
        # m2_fftx, m2_ffty = self.calcFFT(m2_filtrado)

        #Plotando o Fourier dos sinais
        # self.make_plot(m1_fftx, np.abs(m1_ffty))
        # self.make_plot(m2_fftx, np.abs(m2_ffty))

        #Reproduzindo os novos audios
        # self.play(m1_filtrado, m1_samplerate)
        # self.play(m2_filtrado, m2_samplerate)

        #-------------------------------------------------
        #Gerando a primeira portadora
        t1 = np.linspace(0, len(m1_filtrado)/self.fs, len(m1_filtrado))
        # self.make_plot(t1, m1)
        port1 = np.sin(2*np.pi*self.fc1*t1)
        port1x, port1y = self.calcFFT(port1)
        # self.make_plot(t1, port1, "Portadora 1 no tempo")

        #Gerando a modulação do primeiro áudio
        am1 = m1_filtrado*port1
        Xam1, am1_fft = self.calcFFT(am1)

        #-------------------------------------------------
        #Gerando a segunda portadora
        t2 = np.linspace(0, len(m2_filtrado)/self.fs, len(m2_filtrado))
        # self.make_plot(t2, m2)
        port2 = np.sin(2*np.pi*self.fc2*t2)
        port2x, port2y = self.calcFFT(port2)
        # self.make_plot(t2, port2, "Portadora 2 no tempo")

        #Gerando a modulação do segundo áudio
        am2 = m2_filtrado*port2
        Xam2, am2_fft = self.calcFFT(am2)
        self.make_plot(t2, am2, "Mensagem 2 modulada no tempo")

        # self.make_carrier_plot(port1x, np.abs(port1y), port2x, np.abs(port2y))
        #-------------------------------------------------
        # self.make_carrier_plot(Xam1, np.abs(am1_fft), Xam2, np.abs(am2_fft))

        #Gerando a soma dos áudios mmodulados
        am = self.sumTwoLists(am1, am2)
        Xam, am_fft = self.calcFFT(am)
        # self.make_plot(Xam, np.abs(am_fft))
        #-------------------------------------------------
        # self.play(am2, self.fc2)
        # self.play(am, self.fs)
        # self.make_plot(Xam2, np.abs(am2_fft))
        

        
        # self.make_plot(X, np.abs(fft_port1))
        # self.make_plot(len(m2), port2)

        


if __name__ == "__main__":
    Transmitter().main()
