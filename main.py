import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy

# Window setup
root = tk.Tk()
root.title("Electric motor simulation model")
root.geometry("1600x900")

# Frame for parameters
param_frame = tk.Frame(root)
param_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nw")

# Frame for plots
plot_frame = tk.Frame(root)
plot_frame.grid(row=0, column=1, padx=10, pady=10, sticky="ne")

# Labels and entries font settings
FONT_SIZE = 13
FONT_TYPE = "Arial"

class Plot():
    def __init__(self, title, ylabel, width, height):
        self.title = title
        self.ylabel = ylabel
        self.width = width
        self.height = height

    def plot(self, t, data, plot_row):
        fig = Figure(figsize=(self.width, self.height), dpi=100)
        ax = fig.add_subplot(111)
        ax.grid(True)
        ax.plot(t, data)
        ax.set_title(self.title)
        ax.set_xlabel("Time (s)")
        ax.set_ylabel(self.ylabel)

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        canvas.draw()
        canvas.get_tk_widget().grid(row=plot_row, column=0, columnspan=2, pady=10)

def rectangle_signal(t, freq, amplitude):
    period = 1 / freq
    signal = amplitude * ((t % period) < (period / 2)).astype(float)
    return signal

def triangle_signal(t, freq, amplitude):
    period = 1 / freq
    signal = 2 * amplitude * numpy.abs(((t / period) % 1) - 0.5)
    return signal

def harmonic_signal(t, freq, amplitude):
    signal = amplitude * numpy.sin(2 * numpy.pi * freq * t)
    return signal

def motor_model(R, L, Kt, Ke, J, k, theta0, omega0, t, u_values):
    dt = t[1] - t[0]
    n = len(t)

    i = numpy.zeros(n)
    theta = numpy.zeros(n)
    omega = numpy.zeros(n)
    theta[0] = theta0
    omega[0] = omega0

    for x in range(1, n):
        # Calculating derivatives
        di_dt = (u_values[x-1] - R * i[x-1] - Ke * omega[x-1]) / L
        dtheta_dt = omega[x-1]
        domega_dt = (Kt * i[x-1] - k * theta[x-1]) / J

        # Euler's method
        i[x] = i[x-1] + dt * di_dt
        theta[x] = theta[x-1] + dt * dtheta_dt
        omega[x] = omega[x-1] + dt * domega_dt

    return i, omega
    

def submit_parameters(R_var, L_var, Kt_var, Ke_var, J_var, k_var, theta0_var, omega0_var, signal_type_var, amplitude_var, duration_var, frequency_var):
    R = R_var.get() 
    L = L_var.get()
    Kt = Kt_var.get()
    Ke = Ke_var.get()
    J = J_var.get()
    k = k_var.get()
    theta0 = theta0_var.get()
    omega0 = omega0_var.get()   
    amp = amplitude_var.get()
    duration = duration_var.get()
    freq = frequency_var.get()
    signal_type = signal_type_var.get()

    # Validating inputs
    if L == 0:
        tk.messagebox.showerror("Error", "Inductance (L) cannot be zero.")
        return
    elif J == 0:
        tk.messagebox.showerror("Error", "Inertia (J) cannot be zero.")
        return

    t = numpy.linspace(0, duration, int(duration * 1000))

    # Generating signal based on signal type
    if signal_type == "Rectangle":
        u_values = rectangle_signal(t, freq, amp)
    elif signal_type == "Triangle":
        u_values = triangle_signal(t, freq, amp)
    elif signal_type == "Harmonic":
        u_values = harmonic_signal(t, freq, amp)
    else:
        u_values = numpy.zeros(len(t))

    # Calculating motor model
    i, omega = motor_model(R, L, Kt, Ke, J, k, theta0, omega0, t, u_values)
    
    signal_plot = Plot("Signal plot", "Voltage (V)", 10, 2.5)
    current_plot = Plot("Current plot", "Current (A)", 10, 2.5)
    omega_plot = Plot("Angular velocity plot", "Omega (rad/s)", 10, 2.5)

    signal_plot.plot(t, u_values, 0)
    current_plot.plot(t, i, 1)
    omega_plot.plot(t, omega, 2)

def main():
    # Motor parameters
    R_var = tk.DoubleVar(value=10)
    L_var = tk.DoubleVar(value=0.1)
    Kt_var = tk.DoubleVar(value=1)
    Ke_var = tk.DoubleVar(value=1)
    J_var = tk.DoubleVar(value=1)
    k_var = tk.DoubleVar(value=1)
    theta0_var = tk.DoubleVar(value=0)
    omega0_var = tk.DoubleVar(value=1)

    # Signal parameters
    signal_type_var = tk.StringVar(value="Rectangle")
    amplitude_var = tk.DoubleVar(value=1)
    duration_var = tk.DoubleVar(value=20)
    frequency_var = tk.DoubleVar(value=1)

    labels_and_entries = [
        ("R (Ω):", R_var),
        ("L (H):", L_var),
        ("Kt (Nm/A):", Kt_var),
        ("Ke (V/(rad/s)):", Ke_var),
        ("J (kg*m^2):", J_var),
        ("k (N/m):", k_var),
        ("θ(0) (rad):", theta0_var),
        ("ω(0) (rad/s):", omega0_var),
        ("Signal Type:", signal_type_var),
        ("Amplitude (V):", amplitude_var),
        ("Duration (s):", duration_var),
        ("Frequency (Hz):", frequency_var)
    ]
    n = len(labels_and_entries)

    # Displaying labels and entries
    for i, (label_text, var) in enumerate(labels_and_entries): 
        label = tk.Label(root, text=label_text, font=(FONT_TYPE, FONT_SIZE))

        if label_text == "Signal Type:":
            entry = ttk.Combobox(root, width = 18, textvariable=signal_type_var, font=(FONT_TYPE, FONT_SIZE))
            entry['values'] = ("Rectangle", "Triangle", "Harmonic")
            entry.current(0)
        else:
            entry = tk.Entry(root, textvariable=var, font=(FONT_TYPE, FONT_SIZE))

        label.grid(row=i, column=0, padx=10, pady=10, in_=param_frame)
        entry.grid(row=i, column=1, padx=10, pady=10, in_=param_frame)

    submit_button = tk.Button(root, 
                              text="Submit Parameters",
                              command=lambda: submit_parameters(R_var, L_var, Kt_var, Ke_var, J_var, k_var, theta0_var, omega0_var, signal_type_var, amplitude_var, duration_var, frequency_var),
                              font=(FONT_TYPE, FONT_SIZE))
    submit_button.grid(row=n, column=0, columnspan=2, pady=10, in_=param_frame)

    scheme_img = Image.open("scheme.jpg")
    scheme_img = scheme_img.resize((500, 200))
    photo = ImageTk.PhotoImage(scheme_img)
    scheme_label = tk.Label(root, image=photo)
    scheme_label.grid(row=n+1, column=0, columnspan=2, pady=20, in_=param_frame)

    # Setting up starting parameters
    submit_parameters(R_var, L_var, Kt_var, Ke_var, J_var, k_var, theta0_var, omega0_var, signal_type_var, amplitude_var, duration_var, frequency_var)

    root.mainloop()

main()
