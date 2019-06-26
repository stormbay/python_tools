import sys, os.path
import re

import Tkinter as tk

OUTPUT_FORMAT  = "r.s {0:s} 0x{1:s}\n"

class RegMeta():
    def __init__(self, name, pattern):
        self.name = name
        self.pattern = re.compile(pattern)
        self.data = 0

class RegsContext():

    def __init__(self):
        self.reglist = []
        self.reglist.append(RegMeta("sp", r'sp : [0-9a-zA-Z]+'))
        self.reglist.append(RegMeta("cpsr", r'pstate : [0-9a-zA-Z]+'))
        self.reglist.append(RegMeta("x29", r'x29: [0-9a-zA-Z]+'))
        self.reglist.append(RegMeta("x28", r'x28: [0-9a-zA-Z]+'))
        self.reglist.append(RegMeta("x27", r'x27: [0-9a-zA-Z]+'))
        self.reglist.append(RegMeta("x26", r'x26: [0-9a-zA-Z]+'))
        self.reglist.append(RegMeta("x25", r'x25: [0-9a-zA-Z]+'))
        self.reglist.append(RegMeta("x24", r'x24: [0-9a-zA-Z]+'))
        self.reglist.append(RegMeta("x23", r'x23: [0-9a-zA-Z]+'))
        self.reglist.append(RegMeta("x22", r'x22: [0-9a-zA-Z]+'))
        self.reglist.append(RegMeta("x21", r'x21: [0-9a-zA-Z]+'))
        self.reglist.append(RegMeta("x20", r'x20: [0-9a-zA-Z]+'))
        self.reglist.append(RegMeta("x19", r'x19: [0-9a-zA-Z]+'))
        self.reglist.append(RegMeta("x18", r'x18: [0-9a-zA-Z]+'))
        self.reglist.append(RegMeta("x17", r'x17: [0-9a-zA-Z]+'))
        self.reglist.append(RegMeta("x16", r'x16: [0-9a-zA-Z]+'))
        self.reglist.append(RegMeta("x15", r'x15: [0-9a-zA-Z]+'))
        self.reglist.append(RegMeta("x14", r'x14: [0-9a-zA-Z]+'))
        self.reglist.append(RegMeta("x13", r'x13: [0-9a-zA-Z]+'))
        self.reglist.append(RegMeta("x12", r'x12: [0-9a-zA-Z]+'))
        self.reglist.append(RegMeta("x11", r'x11: [0-9a-zA-Z]+'))
        self.reglist.append(RegMeta("x10", r'x10: [0-9a-zA-Z]+'))
        self.reglist.append(RegMeta("x9", r'x9 : [0-9a-zA-Z]+'))
        self.reglist.append(RegMeta("x8", r'x8 : [0-9a-zA-Z]+'))
        self.reglist.append(RegMeta("x7", r'x7 : [0-9a-zA-Z]+'))
        self.reglist.append(RegMeta("x6", r'x6 : [0-9a-zA-Z]+'))
        self.reglist.append(RegMeta("x5", r'x5 : [0-9a-zA-Z]+'))
        self.reglist.append(RegMeta("x4", r'x4 : [0-9a-zA-Z]+'))
        self.reglist.append(RegMeta("x3", r'x3 : [0-9a-zA-Z]+'))
        self.reglist.append(RegMeta("x2", r'x2 : [0-9a-zA-Z]+'))
        self.reglist.append(RegMeta("x1", r'x1 : [0-9a-zA-Z]+'))
        self.reglist.append(RegMeta("x0", r'x0 : [0-9a-zA-Z]+'))
        self.regcnt = len(self.reglist)

    def translate(self, inputlog):
        linelist = inputlog.split('\n')
        linecnt = len(linelist)

        regid = 0
        data_pattern = re.compile(r'[0-9a-zA-Z]+$')
        for line in range(linecnt):
            output1 = self.reglist[regid].pattern.findall(linelist[line])
            if len(output1) == 0:
                continue
            self.reglist[regid].data = data_pattern.findall(output1[0])
            output1 = self.reglist[regid+1].pattern.findall(linelist[line])
            self.reglist[regid+1].data = data_pattern.findall(output1[0])

            regid += 2
            if regid >= self.regcnt:
                break

        ret_string = ""
        for regid in range(self.regcnt):
            #print("r.s "+self.reglist[regid].name+" 0x"+self.reglist[regid].data[0])
            ret_string += OUTPUT_FORMAT.format(self.reglist[regid].name, self.reglist[regid].data[0])

        return ret_string


def startTranslate(event):
    text_out.delete(0.0, tk.END)

    input_log = text_in.get(0.0, tk.END)

    regcxt = RegsContext()
    ret_str = regcxt.translate(input_log)

    output_string = "r.s pc 0x-1\n" + "r.s x20 0x-1\n" + ret_str
    text_out.insert(0.0, output_string)

def selectTextIn(event):
    text_in.tag_add('sel', '1.0', 'end')
    return 'break'

def selectTextOut(event):
    text_out.tag_add('sel', '1.0', 'end')
    return 'break'

if __name__ == "__main__":

    window = tk.Tk()

    window.title("Translator 1.0")
    window.geometry("526x948")
    window.resizable(width=False, height=False)

    text_in = tk.Text(window, width=64, height=24, borderwidth=2)
    text_in.place(x=4, y=2)
    text_in.bind("<Return>", startTranslate)
    text_in.bind("<Control-Key-a>", selectTextIn)

    text_out = tk.Text(window, width=64, height=36, borderwidth=2, background='gray')
    text_out.place(x=4, y=360)
    text_out.bind("<Control-Key-a>", selectTextOut)

    window.mainloop()
