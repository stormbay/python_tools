import Tkinter as tk



def printInfo(event):
    text_out.delete(0.0, tk.END)
    text_out.insert(0.0, text_in.get(0.0, tk.END))




window = tk.Tk()

window.title("Translator")
window.geometry("546x750")
window.resizable(width=False, height=False)


text_in = tk.Text(window, width=76, height=24, borderwidth=2)
text_in.place(x=4, y=2)
text_in.bind("<Return>", printInfo)

text_out = tk.Text(window, width=76, height=32, borderwidth=2, background='gray')
text_out.place(x=4, y=324)


window.mainloop()
