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

def remap(value, initialMin, initialMax, newMin, newMax):
    return newMin + (value - initialMin) * (newMax - newMin) / (initialMax - initialMin)

class Knob:
    def __init__(self, x, y, r, minValue, maxValue, startValue, sensitivity, minRotation, maxRotation):
        self.x = x
        self.y = y
        self.r = r
        self.startValue = startValue
        self.minValue = minValue
        self.maxValue = maxValue
        self.sensitivity = sensitivity
        self.minRotation = minRotation
        self.maxRotation = maxRotation
        self.range = self.maxValue - self.minValue
        self.color = 'black'
        self.knobAngle = remap(self.startValue, self.minValue, self.maxValue, maxRotation, minRotation)
        self.pointerX = self.x + self.r * math.cos(self.knobAngle)
        self.pointerY = self.y - self.r * math.sin(self.knobAngle)
        self.currValue = startValue
        
        self.prevY = self.y
        self.yOffset = remap(self.knobAngle, self.maxRotation, self.minRotation, -self.sensitivity, self.sensitivity)
        self.yDiff = self.prevY + self.yOffset




    
    def turnKnob(self, mouseX, mouseY):
        
        self.yDiff = self.prevY - mouseY + self.yOffset
        
        if self.yDiff > self.sensitivity:
            self.yDiff = self.sensitivity
        if self.yDiff < -self.sensitivity:
            self.yDiff = -self.sensitivity

        self.knobAngle = remap(self.yDiff, -self.sensitivity, self.sensitivity, self.minValue, self.maxValue)
        self.knobAngle = remap(self.yDiff, -self.sensitivity, self.sensitivity, self.maxRotation, self.minRotation)
        self.pointerX = self.x + self.r * math.cos(self.knobAngle)
        self.pointerY = self.y - self.r * math.sin(self.knobAngle)
        self.currValue = int(remap(self.knobAngle, self.maxRotation, self.minRotation, self.minValue, self.maxValue))

    def testSelection(self, mouseX, mouseY):
        if distance(self.x, self.y, mouseX, mouseY) < self.r:
            return True


class floatKnob(Knob):
    def __init__(self, x, y, r, minValue, maxValue, startValue, sensitivity, minRotation, maxRotation):
        super().__init__(x, y, r, minValue, maxValue, startValue, sensitivity, minRotation, maxRotation)

    def turnKnob(self, mouseX, mouseY):
        
        self.yDiff = self.prevY - mouseY + self.yOffset
        
        if self.yDiff > self.sensitivity:
            self.yDiff = self.sensitivity
        if self.yDiff < -self.sensitivity:
            self.yDiff = -self.sensitivity

        self.knobAngle = remap(self.yDiff, -self.sensitivity, self.sensitivity, self.minValue, self.maxValue)
        self.knobAngle = remap(self.yDiff, -self.sensitivity, self.sensitivity, self.maxRotation, self.minRotation)
        self.pointerX = self.x + self.r * math.cos(self.knobAngle)
        self.pointerY = self.y - self.r * math.sin(self.knobAngle)
        self.currValue = remap(self.knobAngle, self.maxRotation, self.minRotation, self.minValue, self.maxValue)
        self.currValue = pythonRound(self.currValue, 2)



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
            
        elif self.status == False:

            self.status = True

# class squareButton(Button):
#     def __init__(self, name, x, y, width, height, onColor, offColor, border):
#         super().__init__(name, x, y, onColor, offColor, border)
#         self.width = width
#         self.height = height
#         self.currColor = self.offColor
    
        



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
        self.ySpace = self.y + self.height + 30
        self.attackKnob = Knob(self.x + 25, self.ySpace, 20, 1, 1000, 20, 50, -math.pi / 4, 5 * math.pi / 4)
        self.decayKnob = Knob(self.x + 75, self.ySpace, 20, 1, 500, 20, 50, -math.pi / 4, 5 * math.pi / 4)
        self.sustainKnob = Knob(self.x + 125, self.ySpace, 20, 0, self.height, 0, 50, -math.pi / 4, 5 * math.pi / 4)
        self.releaseKnob = Knob(self.x + 175, self.ySpace, 20, 1, 500, 20, 50, -math.pi / 4, 5 * math.pi / 4)
        self.knobList = [self.attackKnob, self.decayKnob, self.sustainKnob, self.releaseKnob]
        

    def lineCords(self):
        self.attack = self.attackKnob.currValue
        self.decay = self.decayKnob.currValue
        self.sustain = self.sustainKnob.currValue
        self.release = self.releaseKnob.currValue
        cordList = [(self.x, self.height + self.y), (self.attack + self.x, self.y), (self.decay, self.sustain + self.y), (40, self.sustain + self.y), (self.release, self.height + self.y)]
        return cordList

class Oscillator:
    def __init__(self, vol, voices, detune, duration):
        self.vol = vol
        self.voices = voices
        self.detune = detune
        self.duration = duration

        # default sampling and quantization settings
        self.sampleRate = 44100
        self.qLevels = 16
        
        self.detuneSign = -1
    # byte equation left empty because no specific type of oscillator
    def byteEquation(self, freq, sampleIndex, sampleRate, currVoice):
        pass
    
    # add duration modifier 
    def generateSound(self, freqList):
        # sampleRate = 44100
        # duration = 3000
        # masterVolume = 0.02
        qLevels = 16

        sampleList = []


        for frequency in freqList:
            currFreq = [0] * int((self.duration * self.sampleRate / 1000))
            
            for i in range(self.voices):
                randomOffset = random.random() * (self.sampleRate / frequency)
                
                for sampleIndex in range(int(self.duration / 1000 * self.sampleRate)):

                    currSample = self.byteEquation(frequency, sampleIndex, self.sampleRate, randomOffset, i * self.detuneSign)

                    currFreq[sampleIndex] += currSample
                
                self.detuneSign *= -1

            
            sampleList.append(currFreq)

        byteData = b''           

        # min and max amplitude values used for normalizing the audio
        minValue = 0
        maxValue = 0

        for sampleIndex in range(len(sampleList[0])):
            currSample = 0
            for frequency in sampleList:
                currSample += frequency[sampleIndex]

            if currSample > maxValue:
                maxValue = currSample
            elif currSample < minValue:
                minValue = currSample
        
        print(minValue, maxValue)


        # Generate singular audio data from combinding all
        for sampleIndex in range(len(sampleList[0])):
            currSample = 0
            for frequency in sampleList:
                currSample += frequency[sampleIndex]

            # remap the sample along the calculated min and max value range            
            remapedSample = remap(currSample, minValue, maxValue, -1, 1)

            remapedSample = int(remapedSample * self.vol * (2 ** qLevels / 2))
            
            amplitudeData = struct.pack('<h', remapedSample)
            
            byteData += amplitudeData


        sound = AudioSegment(
            data=byteData,
            sample_width=2,
            frame_rate=self.sampleRate,
            channels=1
        )
        return sound



class Sine(Oscillator):
    def __init__(self, vol, voices, detune, duration):
        super().__init__(vol, voices, detune, duration)
    
    def byteEquation(self, freq, sampleIndex, sampleRate, randomOffset, currVoice):
        return math.sin(2 * math.pi * (freq + currVoice * self.detune * freq) * (sampleIndex / sampleRate) + randomOffset)



class Saw(Oscillator):
    def __init__(self, vol, voices, detune, duration):
        super().__init__(vol, voices, detune, duration)

    def byteEquation(self, freq, sampleIndex, sampleRate, randomOffset, currVoice):
        return math.atan(math.tan(2 * math.pi * (freq + currVoice * self.detune * freq) * (sampleIndex / sampleRate) + randomOffset))

class Square(Oscillator):
    def __init__(self, vol, voices, detune, duration):
        super().__init__(vol, voices, detune, duration)
    
    def byteEquation(self, freq, sampleIndex, sampleRate, randomOffset, currVoice):

        cycle = int(sampleRate / (freq + currVoice * self.detune * freq))
        if (sampleIndex + randomOffset) % cycle < cycle / 2:
            return 1
        else:
            return -1



class Triangle(Oscillator):
    def __init__(self, vol, voices, detune, duration):
        super().__init__(vol, voices, detune, duration)

    def byteEquation(self, freq, sampleIndex, sampleRate, randomOffset, currVoice):
        return math.asin( math.sin(2 * math.pi * (freq + currVoice * self.detune * freq) * (sampleIndex / sampleRate) + randomOffset))

def onAppStart(app):
    app.background = rgb(165, 195, 216)
    # list containing free knobs
    app.knobList = [Knob(650, 75, 20, 0, 100, 50, 50, -math.pi / 4, 5 * math.pi / 4),
                    floatKnob(238, 90, 20, 0, 1, 0, 50, -math.pi / 4, 5 * math.pi / 4),
                    Knob(183, 90, 20, 1, 16, 1, 50, -math.pi / 4, 5 * math.pi / 4),
                    Knob(650, 150, 20, 100, 3000, 1000, 50, -math.pi / 4, 5 * math.pi / 4),
                    Knob(404, 97, 20, 8, 22050, 7000, 50, -math.pi / 4, 5 * math.pi / 4)]

    app.volumeIndex = 0
    app.detuneIndex = 1
    app.voiceIndex = 2
    
    # app.squareButtonList = [squareButton('Export', 612, 18, 76, 16, 'blue', 'grey', 'black')]
    # list containing all buttons on board
    app.osc1 = [startOn('sine', 44, 76, 10, 'red', rgb(112, 16, 16), 'black'),
                startOff('saw', 94, 76, 10, 'red', rgb(112, 16, 16), 'black'),
                startOff('square', 44, 110, 10, 'red', rgb(112, 16, 16), 'black'),
                startOff('triangle', 94, 110, 10, 'red', rgb(112, 16, 16), 'black')]
    
    app.filter = [startOff('LP1', 327, 76, 10, 'red', rgb(112, 16, 16), 'black'),
                startOff('LP2', 327, 111, 10, 'red', rgb(112, 16, 16), 'black'),
                startOff('HP1', 327, 145, 10, 'red', rgb(112, 16, 16), 'black'),
                startOff('HP2', 327, 180, 10, 'red', rgb(112, 16, 16), 'black')]


    app.buttonList = []
    app.buttonList.append(app.osc1)
    app.buttonList.append(app.filter)
    app.selectedButton = None

    app.envelope1 = Envelope(37, 244, 124, 241)
    
    app.envelopeList = []
    app.envelopeList.append(app.envelope1)
    

    app.envelopeKnob = False
    app.selectedKnob = None
    app.currOsc = 'sine'
    app.notes = ''

    # x, y, length, title
    app.labelCords = [(20, 41, 264, 'Oscillator'), (20, 217, 264, 'Envelope'), (303, 41, 137, 'Filter')]
def redrawAll(app):
    
    # for squareButton in app.squareButtonList:
    #     drawRect(squareButton.x, squareButton.y, squareButton.width, squareButton.height, fill='')

    # draw buttons
    for buttonGroup in app.buttonList:
        for button in buttonGroup:
            if button.status == True:
                button.currColor = button.onColor
            else:
                button.currColor = button.offColor
            
            drawCircle(button.x, button.y, button.r, fill=button.currColor, border=button.border, borderWidth=1.5)
            drawLabel(f'{button.name}', button.x + button.r + 5, button.y, align='left')

    # draw free knobs    
    for knob in app.knobList:
        drawCircle(knob.x, knob.y, knob.r, fill=knob.color, border='black',)

        drawLine(knob.x, knob.y, knob.pointerX, knob.pointerY, fill='red')
        
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

            drawLine(knob.x, knob.y, knob.pointerX, knob.pointerY, fill='red')
            
            drawLabel(f'{knob.currValue}', knob.x, knob.y + 40)

    # Title
    drawLabel('Synth 112', 20, 20, align='left', font='arial', bold=True, size=30, italic=True)
    drawLabel('Digital Synthesizer', 170, 20, align='left', font='arial', opacity=60)

    # Synthesizer Sections
    for x, y, length, title in app.labelCords:
        drawRect(x, y, length, 18, align='top-left', fill='black', opacity=75)
        drawLabel(f'{title}', x + 5, y + 5, fill='white', align='top-left', size=11)
        drawLine(x, y + 18, x, y + 120)



    drawLabel(f'Current Notes: {app.notes}', 350, 300, align='left-top', size=16)
    drawLabel('Press Enter to Play', 350, 330, align='left-top', size=16)
    

def onMousePress(app, mouseX, mouseY):
    # check for free knob changes
    for i in range(len(app.knobList)):
        if app.knobList[i].testSelection(mouseX, mouseY):
            app.selectedKnob = i
            app.knobList[i].prevY = mouseY
            return 
        
    # chheck for envelope knob changes 
    for envelope in app.envelopeList:
        for i in range(len(envelope.knobList)):
            if envelope.knobList[i].testSelection(mouseX, mouseY):
                app.envelopeKnob = True
                app.selectedKnob = i
                envelope.knobList[i].prevY = mouseY
                return 
    
    # check for button presses
    for buttonGroup in app.buttonList:
        for i in range(len(buttonGroup)):
            if buttonGroup[i].testSelection(mouseX, mouseY):
                if buttonGroup[i] in app.filter:

                    # change state of selected button
                    buttonGroup[i].statusChange()
                    # clear related buttons
                    clearButtonGroup(app, buttonGroup, i)

                # checking for state because always one oscillator must be on
                elif buttonGroup[i].status == False and buttonGroup[i] in app.osc1:
            
                    buttonGroup[i].statusChange()

               
                    clearButtonGroup(app, buttonGroup, i)

                    


def clearButtonGroup(app, buttonList, index):
    for i in range(len(buttonList)):
        if i == index:
            continue 
        else:
            buttonList[i].status = False



def playNotes(app, freqList):
    voices = app.knobList[app.voiceIndex].currValue
    initialDetune = app.knobList[app.detuneIndex].currValue
    volume = app.knobList[app.volumeIndex].currValue / 100
    duration = app.knobList[3].currValue

    # remapping detune from 0-1 to values that produce usable results
    detune = remap(initialDetune, 0, 1, 0, 0.01)


    for button in app.osc1:
        if button.status == True:
            if button.name == 'sine':
                osc = Sine(volume, voices, detune, duration)
            elif button.name == 'saw':
                osc = Saw(volume, voices, detune, duration)
            elif button.name == 'square':
                osc = Square(volume, voices, detune, duration)
            elif button.name == 'triangle':
                osc = Triangle(volume, voices, detune, duration)

    sound = osc.generateSound(freqList)

    attackTime = app.envelope1.knobList[0].currValue
    decayTime = app.envelope1.knobList[1].currValue
    sustainLevel = remap(app.envelope1.knobList[2].currValue, app.envelope1.knobList[2].minValue, app.envelope1.knobList[2].maxValue, 0, -120)
    releaseTime = app.envelope1.knobList[3].currValue


    attack = sound[:attackTime].fade_in(duration=attackTime - 1)
    print(len(attack))
    # print('attack')
    play(attack)
    
    decayRef = sound[attackTime:].fade(start=0, duration=decayTime - 1, to_gain=sustainLevel)
    decay = sound[attackTime: attackTime + decayTime].fade(start=0, duration=decayTime - 1, to_gain=sustainLevel)
    print(len(decay))
    # print('decay')
    


    
    sustainRelease = decayRef[decayTime:].fade_out(duration=releaseTime)
    print(len(sustainRelease))
    # print('release')
    # play(release)

    finalSound = attack + decay + sustainRelease
    # finalSound = decay
    print(len(finalSound))
    play(finalSound)

    

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
    if app.selectedKnob:
        if app.envelopeKnob:
            app.envelopeList[0].knobList[app.selectedKnob].yOffset = app.envelopeList[0].knobList[app.selectedKnob].yDiff
        else:
            app.knobList[app.selectedKnob].yOffset = app.knobList[app.selectedKnob].yDiff

    app.selectedKnob = None
    app.envelopeKnob = False

def onMouseDrag(app, mouseX, mouseY):
    if app.selectedKnob != None:
        if app.envelopeKnob:
            app.envelopeList[0].knobList[app.selectedKnob].turnKnob(mouseX, mouseY)
        else:
            app.knobList[app.selectedKnob].turnKnob(mouseX, mouseY)



def main():
    runApp(width=700, height=500)

main()

