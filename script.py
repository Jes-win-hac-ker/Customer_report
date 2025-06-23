import tkinter as tk


root = tk.Tk()
root.title("My First GUI")
root.geometry("600x500")

label = tk.Label(root, text="Customer Report")
label.pack(pady = 10)

entry = tk.Entry(root)
entry.insert(0,"Enter your name")
entry.bind("<FocusIn>", lambda e: entry.delete(0, tk.END))
entry.pack(pady = 10)


root.mainloop()