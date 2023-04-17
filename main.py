from cmu_graphics import * 
import math 


def distance(x1, y1, x2, y2):
    return (((x1-x2)**2 + (y1-y2)**2)**0.5)


class Knob:

    def __init__(self, minValue, maxValue, startValue, x, y, r):
        self.max = maxValue
        self.min = minValue
        self.startValue = startValue
        self.currValue = startValue
        self.range = ((self.max - self.min) // 2)
        self.color = 'white'
        self.x = x
        self.y = y
        self.r = r
        self.pointerX = x
        self.pointerY = self.y - self.r
        self.knobAngle = 0
        

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


class Envelope:

    def __init__(self, x, y, height, width):
        self.x = x
        self.y = y
        self.height = height
        self.width = width
        
        self.attackKnob = Knob(1, 50, 20, self.x + 25, self.y + 200, 20)
        self.decayKnob = Knob(1, 50, 20, self.x + 75, self.y + 200, 20)
        self.sustainKnob = Knob(0, 150, 40, self.x + 125, self.y + 200, 20)
        self.releaseKnob = Knob(1, 50, 20, self.x + 175, self.y + 200, 20)
        self.knobList = [self.attackKnob, self.decayKnob, self.sustainKnob, self.releaseKnob]
        


    def lineCords(self):
        self.attack = self.attackKnob.currValue
        self.decay = self.decayKnob.currValue
        self.sustain = self.sustainKnob.currValue
        self.release = self.releaseKnob.currValue
        cordList = [(self.x, self.height + self.y), (self.attack + self.x, self.y), (self.decay, self.sustain + self.y), (40, self.sustain + self.y), (self.release, self.height + self.y)]
        return cordList





def onAppStart(app):
    app.knobList = []
   
    app.envelope1 = Envelope(100, 50, 150, 200)
    
    app.envelopeList = []
    app.envelopeList.append(app.envelope1)

    app.selectedKnob = None

def redrawAll(app):
    

    for knob in app.knobList:
        drawCircle(knob.x, knob.y, knob.r, fill=knob.color, border='black')

        drawLine(knob.x, knob.y, knob.pointerX, knob.pointerY)
        
        drawLabel(f'{knob.currValue}', knob.x, knob.y + 40)
    
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
            drawLine(prevX + prevXDisplace, prevY, x + xDisplace, y)

            # generate/update correct spacings between lines
            prevXDisplace = xDisplace
            xDisplace += x
    
            



        for knob in envelope.knobList:
        
            drawCircle(knob.x, knob.y, knob.r, fill=knob.color, border='black')

            drawLine(knob.x, knob.y, knob.pointerX, knob.pointerY)
            
            drawLabel(f'{knob.currValue}', knob.x, knob.y + 40)

    drawLabel('Synth 112', 20, 20, align='left-top', font='arial', bold=True, size=30, italic=True )
    

def onMousePress(app, mouseX, mouseY):
    for i in range(len(app.knobList)):
        if app.knobList[i].testSelection(mouseX, mouseY):
            app.selectedKnob = i

    for envelope in app.envelopeList:
        for i in range(len(envelope.knobList)):
            if envelope.knobList[i].testSelection(mouseX, mouseY):
                app.selectedKnob = i


def onMouseRelease(app, mouseX, mouseY):
    app.selectedKnob = None

def onMouseDrag(app, mouseX, mouseY):
    if app.selectedKnob != None:
        app.envelopeList[0].knobList[app.selectedKnob].turnKnob(mouseX, mouseY)



def main():
    runApp(width=600, height=600)

main()