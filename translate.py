import math
from typing import Callable
import os
import itertools

#CONFIG

INPUT_FILE = "beemovie.txt"


#UTILITY

def writeAll(s:str, path:str):
    with open(path, "w") as f:
        f.write(s)


#ENCODINGS

def encodeTerrible(text:str)->str:
    buffer = "".join(["+"*ord(c)+"."+"-"*ord(c) for c in text])
    return buffer;

def encodeNaive(text:str)->str:
    buffer = "".join(["+"*ord(c)+"."+"[-]" for c in text])
    return buffer;

def makeNumber(num:int, right:bool = True)->str:
    """Returns a brainfuck snippet creating the requested number in the current cell
    with as little characters of code as possible.

    The "right" argument specifies whether the cell to the left or right of the
    current cell is used to store one of the factors - that cell should be empty"""
    #use multiplicative loop, find factors that are as close to one another as
    #possible to minimize characters used, add the rest
    root = math.floor(num**(.5))

    #create the loop
    shift       = ">" if right else "<"
    rev_shift   = "<" if right else ">"
    res = ""
    res += shift
    res += "+"*root
    res += "[" + rev_shift + "+"*root + shift + "-]" + rev_shift
    if root**2 < num:
        res += "+"*(num-root**2)
    return res

def encodeLoop(text:str)->str:
    root = 9
    buffer = ""
    for c in text:
        val = ord(c)
        #INCREMENT
        buffer += makeNumber(val, right = True)
        #OUTPUT
        buffer += "."
        #DECREMENT
        buffer += "[-]"
    return buffer

def copyToNext(numberOfCells:int)->str:
    """Returns a brainfuck snippet copying the content of the current cell to the
    next numberOfCells cells in a row, then returning to the original cell, eaving it at 0"""
    return "["+">+"*numberOfCells+"<"*numberOfCells+"-]"

def encodePrepCells(text:str)->None:
    #get average value of all chars
    avg = sum([ord(c) for c in text]) // len(text)
    #prep all cells with the average values
    buffer = ""
    buffer += makeNumber(avg, right=True)
    buffer += copyToNext(len(text)) #copy it as many times as there are chars in text
    buffer += ">"

    #add the delta of the actual chars from the average onto the cells and print them
    for c in text:
        if ord(c) > avg:
            buffer += (ord(c)-avg) * "+" + "."
        elif ord(c) < avg:
            buffer += (avg-ord(c)) * "-" + "."
        else:
            buffer += "."
        buffer += ">"

    return buffer

def copyToNextSkip(numberOfCells:int, skipmask:list[bool])->str:
    """Returns a brainfuck snippet copying the content of the current cell to the
    next numberOfCells cells in a row, then returning to the original cell, leaving it at 0

    Expects a list of bools skipmask of length numberOfCells indicating with True
    cells not to copy to in order
    """
    assert len(skipmask) == numberOfCells

    #trailing consecutive skips need not be encoded
    trailing = 0
    for skip in skipmask[::-1]:
        if skip:
            trailing += 1
        else:
            break
    skipmask = skipmask[:-trailing] if trailing else skipmask

    res = "["
    for skip in skipmask:
        res += ">" if skip else ">+"
    res += "<" * (len(skipmask))
    res += "-]"
    return res


def encodePrepLowercase(text:str)->None:
    #get average value of all chars, grouped by lowercase and uppercase
    cutoff = 0x61 #hex code of lower case a
    lower  = [ord(c) for c in text if ord(c) < cutoff]
    higher = [ord(c) for c in text if ord(c) >= cutoff]
    avg_low  = sum(lower) // len(lower)
    avg_high = sum(higher) // len(higher)
    #prep all cells with the average values
    skipmask = [ ord(c)>=cutoff for c in text]
    buffer = ">"
    buffer += makeNumber(avg_low, right=False)
    buffer += copyToNextSkip(len(text), skipmask)

    buffer += makeNumber(avg_high, right=False)
    buffer += copyToNextSkip(len(text), [(not a) for a in skipmask] )
    buffer += ">"

    #add the delta of the actual chars from the average onto the cells and print them
    for c in text:
        avg = avg_low if ord(c)<cutoff else avg_high
        if ord(c) > avg:
            buffer += (ord(c)-avg) * "+" + "."
        elif ord(c) < avg:
            buffer += (avg-ord(c)) * "-" + "."
        else:
            buffer += "."
        buffer += ">"

    return buffer


def encodePrepGroups(text:str, cutoffs:list[int] = [62,112])->None:
    """
    Groups characters by ASCII order according to cutoffs, preparing average values for
    the group in their memory cells before incrementing or decrementing the average to the exact char.
    Groups must not be empty.

    This increases compression as copying cells is generally more efficient than building new numbers.
    Parameterization of cutoffs makes it easy to find their optimal configuration.
        Edit: turns out only one cutoff at 47 is optimal for most texts
    """
    #create cutoff at max ascii hex
    cutoffs += [0x80]
    cutoffs = list(dict.fromkeys(cutoffs))

    groups = [ [] for cutoff in cutoffs ]
    for c in text:
        minim = 999
        for i, cut in enumerate(cutoffs):
            if ord(c) < cut:
                minim = min(i,minim)
        groups[minim] += [ord(c)]

    averages = [ sum(g) // len(g) for g in groups]

    #prep all cells with the average values
    buffer = ">"
    for i,g in enumerate(groups):
        skipmask = [not ord(c) in g for c in text]
        buffer += makeNumber(averages[i], right=False)
        buffer += copyToNextSkip(len(text), skipmask)

    buffer += ">"


    #add the delta of the actual chars from the average onto the cells and print them
    for c in text:
        avg = 0
        for i,g in enumerate(groups):
            if ord(c) in g:
                avg = averages[i]

        if ord(c) > avg:
            buffer += (ord(c)-avg) * "+" + "."
        elif ord(c) < avg:
            buffer += (avg-ord(c)) * "-" + "."
        else:
            buffer += "."
        buffer += ">"

    return buffer

#utility function for encodePrepGroups
def findOptimalCutoffs():
    min = 9999999
    mintup = (0,0)
    #for x in range(5):
        #for l in itertools.combinations([x for x in range(32,126, 10)], x):
    for x in range(57, 67):
        for y in range(117, 127):
            try:
                length = len(encodePrepGroups(trytext, list( (x,y) )))
                if length < min:
                    min = length
                    mintup = (x,y)
                print(length, x,y ,"min: ", mintup)
            except Exception as e:
                print(e)




def setNext(factors:tuple[int], val:int)->str:
    """
    Make BF snippet to shift right by 6, then put val into the next factor1*factor2*factor3 cells
    Returns pointing to the first number.

    e.g: 1x2x3=6 cells of 2x1=2

    >+ fac1 [>>++ fac2 [[>>+++fac3  [[>]    makeNumber here >+[<++>-]< to here     [<]<>>-]]<<-]<<-]>>>>>
    """


    res =  ">"
    res += makeNumber(factors[0], right = False)
    res += "[>>"
    res += makeNumber(factors[1], right = False)
    res += "[[>>"
    res += makeNumber(factors[2], right = False)
    res += "[[>]" + makeNumber(val, right=True) + "[<]<>>-]"
    res += "]<<-]<<-]>>>>>"
    return res

def factorizeLength(text:str):
    """"To tell setNext how many times the average shall be set, 3 factors of 1 byte adressing space
    each can be used (256**3 max file size).
    If the length of the text cannot be properly factorized (large prime factors), cheat by appending spaces until
    it can be"""
    facs = (0,0,0)
    for cheating in range(100):
        for x,y,z in itertools.combinations(range(255),3):
            if x*y*z == int(len(text))+1:
                facs = x,y,z
                return text, cheating, x,y,z
        text += " "

def makeNumberWrap(num:int, right:bool = True)->str:
    """Like makeNumber, but uses wraparound if num >= 64
    e.g. - results in char 255"""
    if num < 64:
        return makeNumber(num, right)
    else:
        parts = [part+"[" for part in makeNumber(num, right).split("[") if part]
        return parts[0] + "".join(parts[1:]).replace("+","-")

def addNumberConditional(d:int, ispositive:bool)->str:
    """Uses either makeNumberWrap, clearing necessary cells or simple +++... / ---... depending on what is shorter"""
    if ispositive:
        alt = ("+"*d)
    else:
        alt = ("-"*d)
    alt2 = "<[-]<[-]>" + makeNumber(d, right=False) + (("[>+<-]>") if ispositive else ("[>-<-]>"))
    return alt if len(alt)<len(alt2) else alt2

def findTwoAverages(text:str)->tuple[int]:
    """Given a text, returns two values a<b such that the variance of any char in the text
    to either a or b is as low as possible"""
    histogram = {}
    for c in text:
        if ord(c) in histogram:
            histogram[ord(c)] += 1
        else:
            histogram[ord(c)] = 1

    minvar = 99999999999
    best_tuple = (0,0)
    for x in range(0x7f):
        for y in range(0x7f):
            if x<y:
                variance = sum([ min(val * abs(key-x), val * abs(key-y)) for key,val in histogram.items() ])
                if variance < minvar:
                    minvar = variance
                    best_tuple = x,y
    return best_tuple

def copyToNextSkipEff(numberOfCells:int, skipmask:list[bool])->str:
    """Like CopyToNextSkip but returns the pointer with a loop in
    3 chars instead of len(text) chars
    """
    assert len(skipmask) == numberOfCells

    #trailing consecutive skips need not be encoded
    trailing = 0
    for skip in skipmask[::-1]:
        if skip:
            trailing += 1
        else:
            break
    skipmask = skipmask[:-trailing] if trailing else skipmask

    res = "["
    for skip in skipmask:
        res += ">" if skip else ">+"
    res += "[<]>"
    res += "-]"
    return res

def encodeBetterAverage(text:str)->None:
    buffer = ""

    text,cheat,x,y,z = factorizeLength(text)
    #prep all cells with the avg[0] value
    avgs = findTwoAverages(text)
    buffer += setNext((x,y,z), avgs[0])
    #then add the delta to avg[1] to the cells closer to avg[1]
    skipmask = [abs(ord(c)-avgs[0]) < abs(ord(c)-avgs[1]) for c in text]
    buffer += "<" + makeNumber(avgs[1]-avgs[0],right = False)
    buffer += copyToNextSkipEff(len(text), skipmask)
    buffer += ">"

    #add the delta of the actual chars from the average onto the cells and print them
    if cheat:
        text = text[:-cheat]
    for i,c in enumerate(text):
        avg = avgs[0] if skipmask[i] else avgs[1]
        if ord(c) > avg:
            buffer += addNumberConditional(ord(c)-avg, True) + "."
        elif ord(c) < avg:
            buffer += addNumberConditional(avg-ord(c), False) + "."
        else:
            buffer += "."
        buffer += ">"


    return buffer



#TEST THE FUNCTIONS

helloworld = """Hello World"""
lorem = """Lorem ipsum dolor sit amet, consectetur adipiscing elit. Proin accumsan vel lacus quis rutrum. Maecenas congue dui nunc, ut ultricies risus egestas ut. Nunc accumsan, quam vitae vulputate commodo, risus neque imperdiet augue, eu tempus mauris mi vel purus. Etiam elementum nulla nec consequat lacinia. Suspendisse tincidunt ipsum nec leo efficitur imperdiet. Suspendisse potenti. Sed tempus ligula consectetur metus placerat, nec aliquet nisl pharetra. Nam accumsan consectetur dolor, quis finibus leo tincidunt sed. Nunc at mollis massa. Proin urna sem, suscipit finibus fermentum non, suscipit eu nunc. Pellentesque gravida tincidunt magna, in tempus velit mattis a. Morbi sagittis neque a augue tristique hendrerit id congue erat.

Morbi sed ante mollis, ultricies lectus eget, hendrerit eros. Morbi malesuada tellus eu urna luctus cursus. Aliquam vulputate interdum velit, lobortis ultrices nunc interdum sed. Aliquam facilisis nulla ut purus bibendum, sed mattis ipsum bibendum. Aliquam venenatis est id lacinia interdum. Praesent in diam leo. Duis condimentum mattis convallis. Sed eget justo augue. Nullam ipsum lorem, scelerisque sodales ultricies id, fringilla sit amet libero. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Pellentesque vehicula sem at ex rhoncus blandit. Sed metus est, ornare sed leo a, pharetra rhoncus ante.

Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Duis sed diam sit amet nunc venenatis viverra. Integer fermentum, nunc ut semper porta, neque lacus suscipit quam, id dapibus lorem orci maximus lorem. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vestibulum dapibus tristique commodo. Nullam efficitur rhoncus libero, at consectetur dolor volutpat id. Suspendisse efficitur nunc sed neque tincidunt, volutpat suscipit ex gravida.

Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Quisque sed quam sit amet lacus dapibus posuere id a dolor. Mauris finibus dapibus nisl, sed imperdiet turpis scelerisque molestie. Nulla quis tellus a neque accumsan interdum. Donec vitae ante mauris. Sed eu erat neque. Mauris pretium, massa quis molestie volutpat, enim neque mattis lorem, vel egestas leo libero ut urna. Cras bibendum lobortis neque, vitae ultrices magna vulputate vitae. Quisque at justo eget libero pellentesque egestas.

Cras volutpat sodales mi, at cursus purus vehicula eu. Duis tempor ligula magna, at sollicitudin risus auctor eu. Ut at metus iaculis, ornare urna at, pharetra magna. Aenean viverra odio eget consectetur viverra. Mauris rutrum arcu placerat est volutpat, ac tempus dolor facilisis. Maecenas vitae nisl leo. Curabitur et mollis lectus. Maecenas suscipit imperdiet pretium.
"""

def bufferPrint(s:str, b:int)->str:
    return s+" "*(b-len(s))

def benchmark(lf:list[Callable], text:str)->None:
    for f in lf:
        print(bufferPrint(f.__name__ + ":", 25), end="")
        print(bufferPrint(str(len(f(text))) + " Byte", 15), end="")
        print(bufferPrint("Score: " +  str(round(int(str(len(f(text)))) / int(str(len(text))),3)) , 15), end="\n")

    print(bufferPrint("Original Length"+ ":", 25), end="")
    print(bufferPrint(str(len(text)) + " Byte", 15), end="\n")

def run(f:Callable, text:str)->None:
    brainfuck_file = "encoded.b"
    writeAll(f(text), brainfuck_file)
    cmd = "py \""+os.getcwd()+"\interpreter.py\" " + brainfuck_file
    os.system(cmd)


trytext = lorem #helloworld
with open(INPUT_FILE,"r") as file:
    trytext = file.read().replace('\n', '')

benchmark(
    [encodeTerrible, encodeNaive, encodeLoop, encodePrepCells, encodePrepLowercase,
    #encodePrepGroups,
    encodeBetterAverage]
    ,trytext)
run(encodeBetterAverage, trytext)
