import module_manager
module_manager.review()

from cmu_graphics import * 
import math 

from pydub import AudioSegment
from pydub.playback import play
import struct
import random


def distance(x1, y1, x2, y2):
    return (((x1-x2)**2 + (y1-y2)**2)**0.5)


class Knob:

    def __init__(self, name, minValue, maxValue, startValue, x, y, r):
        self.name = name
        self.max = maxValue
        self.min = minValue
        self.startValue = startValue
        self.currValue = startValue
        self.range = ((self.max - self.min) // 2)
        self.color = 'white'
        self.x = x
        self.y = y
        self.r = r
        self.knobAngle = 0
        self.pointerX = x
        self.pointerY = self.y + self.r * math.cos(self.knobAngle - math.pi)
        
        
    def turnKnob(self, mouseX, mouseY):
        yDiff = self.y - mouseY
        yDiffMag = abs(self.y - mouseY)

        angle = math.atan(yDiffMag/self.r)
        if abs(angle) > 1.17:
            angle = 3 * math.pi / 8 

        if angle < 0.1 and angle > -0.1 :
            angle = 0
            self.currValue = self.startValue
        
        if yDiff < 0:
            angle = angle

        if yDiff > 0:
            angle = -angle

        self.pointerY = self.y + self.r * math.cos(self.knobAngle + angle - math.pi)
        
        self.pointerX = self.x + self.r * math.sin(self.knobAngle + angle - math.pi)
    
        self.knobAngle = angle

        self.currValue = int(self.startValue - (self.knobAngle / (3 * math.pi / 8)) * self.range)
            


    def testSelection(self, mouseX, mouseY):
        if distance(self.x, self.y, mouseX, mouseY) < self.r + 10:
            return True

class Button:
    def __init__(self, name, x, y, r, onColor, offColor, border):
        self.name = name
        self.x = x
        self.y = y
        self.r = r
        self.border = border
        self.onColor = onColor 
        self.offColor = offColor



    def testSelection(self, mouseX, mouseY):
        if distance(self.x, self.y, mouseX, mouseY) < self.r:
            return True
    
    def statusChange(self):
        if self.status == True:
            self.status = False
            self.currColor = self.offColor
        elif self.status == False:
            self.currColor = self.onColor
            self.status = True
            

class startOn(Button):
    def __init__(self, name, x, y, r, onColor, offColor, border):
        super().__init__(name, x, y , r, onColor, offColor, border)
        self.currColor = self.onColor
        self.status = True

class startOff(Button):
    def __init__(self, name, x, y, r, onColor, offColor, border):       
        super().__init__(name, x, y , r, onColor, offColor, border)
        self.currColor = self.offColor
        self.status = False

class Envelope:

    def __init__(self, x, y, height, width):
        self.x = x
        self.y = y
        self.height = height
        self.width = width
        
        self.attackKnob = Knob('attack', 1, 50, 20, self.x + 25, self.y + self.height + 30, 20)
        self.decayKnob = Knob('decay', 1, 50, 20, self.x + 75, self.y + self.height + 30, 20)
        self.sustainKnob = Knob('sustain', 0, self.height, 40, self.x + 125, self.y + self.height + 30, 20)
        self.releaseKnob = Knob('release', 1, 50, 20, self.x + 175, self.y + self.height + 30, 20)
        self.knobList = [self.attackKnob, self.decayKnob, self.sustainKnob, self.releaseKnob]
        

    def lineCords(self):
        self.attack = self.attackKnob.currValue
        self.decay = self.decayKnob.currValue
        self.sustain = self.sustainKnob.currValue
        self.release = self.releaseKnob.currValue
        cordList = [(self.x, self.height + self.y), (self.attack + self.x, self.y), (self.decay, self.sustain + self.y), (40, self.sustain + self.y), (self.release, self.height + self.y)]
        return cordList

class Oscillator:
    def __init__(self, vol, voices, detune):
        self.vol = vol
        self.voices = voices
        self.detune = detune
    


class Sine(Oscillator):
    def __init__(self, vol, voices, detune):
        super().__init__(vol, voices, detune)


    def playSound(self, freqList):
        sampleRate = 44100
        duration = 3000
        masterVolume = 0.02
        qLevels = 16
        sampleList = []

        for frequency in freqList:
            currFreq = []
            

            for sampleIndex in range(int(duration / 1000 * sampleRate)):
                currSample = 0

                for i in range(self.voices):
                    currAmplitude = math.sin(2 * math.pi * (frequency + i * self.detune * frequency) * (sampleIndex / sampleRate))

                    currSample += currAmplitude

                currFreq.append(int(currSample * masterVolume * (2**qLevels / 2)))
            
            sampleList.append(currFreq)


        byteData = b''           

        # Generate singular audio data from combinding all
        for sampleIndex in range(len(sampleList[0])):
            currSample = 0
            for frequency in sampleList:
                currSample += frequency[sampleIndex]
                amplitudeData = struct.pack('<h', currSample)
            
            byteData += amplitudeData


        sineChord = AudioSegment(
            data=byteData,
            sample_width=2,
            frame_rate=sampleRate,
            channels=1

        )

        play(sineChord)


class Saw(Oscillator):
    pass


class Square(Oscillator):
    pass




def onAppStart(app):
    # list containing free knobs
    app.knobList = [Knob('volume', 0, 100, 50, app.width - 30, 60, 20),
                    Knob('detune', 0, 16, 0, 420, 70, 20),
                    Knob('voices', 0, 100, 50, 420, 140, 20),]

    # list containing all buttons on board
    app.buttonList = [startOn('sine', 320, 60, 10, 'red', rgb(112, 16, 16), 'black'),
                      startOff('saw', 320, 85, 10, 'red', rgb(112, 16, 16), 'black'),
                      startOff('square', 320, 110, 10, 'red', rgb(112, 16, 16), 'black'),
                      startOff('triangle', 320, 135, 10, 'red', rgb(112, 16, 16), 'black')]
    


    app.selectedButton = None

    app.envelope1 = Envelope(20, 80, 125, 200)
    
    app.envelopeList = []
    app.envelopeList.append(app.envelope1)
    

    app.envelopeKnob = False
    app.selectedKnob = None
    app.currOsc = 'sine'
    app.notes = ''

    # x, y, length, title
    app.labelCords = [(20, 50, 200, 'Filter'), (300, 10, 100, 'Oscillator')]
def redrawAll(app):
    
    # draw buttons
    for button in app.buttonList:
        drawCircle(button.x, button.y, button.r, fill=button.currColor, border=button.border, borderWidth=1.5)
        drawLabel(f'{button.name}', button.x + button.r + 5, button.y, align='left')

    # draw free knobs    
    for knob in app.knobList:
        drawCircle(knob.x, knob.y, knob.r, fill=knob.color, border='black')

        drawLine(knob.x, knob.y, knob.pointerX, knob.pointerY)
        
        drawLabel(f'{knob.currValue}', knob.x, knob.y + 35)
    
    # draw envelopes 
    for envelope in app.envelopeList:
        drawRect(envelope.x, envelope.y, envelope.width, envelope.height, fill='white', border='black', align='top-left')
        
        # use envelope method to get list of line chords 
        cordList = envelope.lineCords()
        

        prevXDisplace = 0
        xDisplace = 0
        for i in range(1, len(cordList)):

            # get raw coordinates for each point position
            prevX, prevY = cordList[i-1][0], cordList[i-1][1]
            x, y = cordList[i][0], cordList[i][1]
            
            # draw ADSR line using displacement values
            drawLine(prevX + prevXDisplace, prevY, x + xDisplace, y, lineWidth=5)

            # generate/update correct spacings between lines
            prevXDisplace = xDisplace
            xDisplace += x
    
        # draw Knobs related to an envelope
        for knob in envelope.knobList:
        
            drawCircle(knob.x, knob.y, knob.r, fill=knob.color, border='black')

            drawLine(knob.x, knob.y, knob.pointerX, knob.pointerY)
            
            drawLabel(f'{knob.currValue}', knob.x, knob.y + 40)

    # Title
    drawLabel('Synth 112', 20, 20, align='left', font='arial', bold=True, size=30, italic=True)
    drawLabel('Digital Synthesizer', 170, 20, align='left', font='arial', opacity=60)

    # Synthesizer Sections
    for x, y, length, title in app.labelCords:
        drawRect(x, y, length, 30, align='top-left', fill='black', opacity=75)
        drawLabel(f'{title}', x + 5, y + 5, fill='white', align='top-left', size=20)



    drawLabel(f'Current Notes: {app.notes}', 350, 300, align='left-top', size=16)
    drawLabel('Press Enter to Play', 350, 330, align='left-top', size=16)
    

def onMousePress(app, mouseX, mouseY):
    for i in range(len(app.knobList)):
        if app.knobList[i].testSelection(mouseX, mouseY):
            app.selectedKnob = i
            return 

    for envelope in app.envelopeList:
        for i in range(len(envelope.knobList)):
            if envelope.knobList[i].testSelection(mouseX, mouseY):
                app.envelopeKnob = True
                app.selectedKnob = i
                return 

    for button in app.buttonList:
        if button.testSelection(mouseX, mouseY):

            button.statusChange()

def playNotes(app, freqList):
    osc = Sine(0.05, 4, 0.002)
    osc.playSound(freqList)



def noteToFreq(app):
    noteDict = {'C' : 16.35, 'D' : 18.35, 
                'E' : 20.60, 'F' : 21.83,
                'G' : 24.50, 'A' : 27.50,
                'B' : 30.87}
    freqList = []
    text = app.notes.upper()
    noteList = text.split()
    for i in range(len(noteList)):
        note = noteList[i][0]
        
        if note in noteDict:

            octave = int(noteList[i][1])
            freqList.append(noteDict[note] * 2 ** octave)


    app.notes = ''
    return freqList

def onKeyPress(app, key):

    if key == 'backspace':
        app.notes = app.notes[:-1]
    elif key == 'enter':
        freqList = noteToFreq(app)
        playNotes(app, freqList)
    elif key == 'space':
        app.notes += ' '
    else:
        app.notes += key
    


def onMouseRelease(app, mouseX, mouseY):
    app.selectedKnob = None
    app.envelopeKnob = False

def onMouseDrag(app, mouseX, mouseY):
    if app.selectedKnob != None:
        if app.envelopeKnob:
            app.envelopeList[0].knobList[app.selectedKnob].turnKnob(mouseX, mouseY)
        else:
            app.knobList[app.selectedKnob].turnKnob(mouseX, mouseY)
            print(app.knobList[app.selectedKnob].knobAngle)



def main():
    runApp(width=800, height=600)

main()

