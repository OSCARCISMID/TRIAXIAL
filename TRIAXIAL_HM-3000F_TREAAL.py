import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from screeninfo import get_monitors
import pandas as pd
from datetime import datetime
import time

# Crendo funcion para graficar ensayos terminados.

def proces_data(ruta, sigma3, H0, D0, DH0, DV0, PP0):
    #lectura de archivo segun la ruta
    df = pd.read_csv(ruta)

    V0 = D0**2*np.pi/4*H0   # Volumen inicial del especimen
    H_C = H0-DH0/10         # Altura del especimen al final de la consolidación
    A_C = (V0-DV0)/H_C      # Área del especimen al final de la consolidación

    deformacion = df[' DEV 1 INPUT 2']
    fuerza = df[' DEV 1 INPUT 1']
    poros = df[' DEV 1 INPUT 4']

    e_1 = 0.1*deformacion/H_C         # Deformacion unitaria axial
    A = A_C/(1-e_1)                   # Área del especimen durante el corte

    esf_desv = fuerza/A*10000   # Esfuerzo Fesviador durante la etapa de corte
    u = poros - PP0             # Variación de la presión de poros durante el corte
    sigma1 = esf_desv + sigma3  # Esfuerzo principal
    sigma1_e = sigma1 - u       # Esfuerzo principal efectivo
    sigma3_e = sigma3 - u       # Esfuerzo de confinamiento efectivo
    p = (sigma1 + sigma3)/2     
    q = (sigma1 - sigma3)/2
    p_e = (sigma1_e + sigma3_e)/2
    q_e = (sigma1_e - sigma3_e)/2
    q_p = q/p                   

    # Creación del dataframe al final del corte del especimen
    tabla = pd.DataFrame()
    tabla['Presion de confinamiento'] = sigma3
    tabla['Deformacion'] = deformacion
    tabla['Esfuerzo desviador'] = esf_desv
    tabla['Presion de Poros'] = u
    tabla['sigma3_efectivo'] = sigma3_e
    tabla['sigma1_efectivo'] = sigma1_e
    tabla['p_e'] = p_e
    tabla['q_e'] = q_e
    tabla['q/p'] = q_p

    return tabla


# Definir el nombre del archivo que contiene los datos
filename0 = 'LG24_PRACTICANTES_LL_CNF_2.txt'   # Archivo para lectura actual en tiempo real
filename1 = 'LG24_PRACTICANTES_LL_CNF_1.txt'   # Primer especimen ensayado
filename2 = '0_000KPA.txt'   # Segundo especimen ensayado

#filename3x = 'LG23-060_CL-PRHu-09_M-01_150KPA.txt'
#filename4x = 'LG23-060_CL-PRHu-09_M-01_300KPA.txt'
#filename5x = 'LG23-060_CL-PRHu-09_M-01_600KPA.txt'

#def proces_data(ruta, sigma3, H0, D0, DH0, DV0, PP0):
sigma3 = 200 # PARA EL ENSAYO EN TIEMPO REAL
muesta1 = proces_data(filename1,400, 20.000, 10.095, 0.00, 0.00, 0.00)
muesta2 = proces_data(filename2,200, 20.000, 10.095, 0.00, 0.00, 0.00)

#muestra3x = proces_data(filename3x,150, 20.000, 10.095, 0.00, 0.00, 0.00)
#muestra4x = proces_data(filename4x,300, 20.000, 10.095, 0.00, 0.00, 0.00)
#muestra5x = proces_data(filename5x,600, 20.000, 10.095, 0.00, 0.00, 0.00)

#variables para legendas en graficas de matplotlib, el archivo debe terminar en x...100KPA
Test1 = filename1[-10:-7] 
Test2 = filename2[-10:-7]
Test0 = filename0[-10:-7]

#Test3x = filename3x[-10:-7]
#Test4x = filename4x[-10:-7]
#Test5x = filename5x[-10:-7]



# Inicializar matrices vacías para guardar los datos
x_data, y1_data, y2_data = [], [], []
p_data, q_data, p_e_data, q_e_data = [], [], [], []

colorfondo1 = "#dfe2ea"
colorfondo2 = "#f1f5fb"
colorfondo3 = "#d2d4dc"
colorlabel = "black"
color1 = "#3B7FD9"
color2 = "#64BF39"
color3 = "#F25749"
color4 = "#400A05"
color3x = "#530A8F"  #morado
color4x = "#018F63"   #verde
color5x =   "#8F8317" #mostasa



# Obtener el ancho y la altura de la pantalla
monitor = get_monitors()[0]
width = monitor.width
height = monitor.height
ancho1 = int(0.994 * width / 2)
ancho2 = width - ancho1
alto1 = int(0.93 * height)
alto2 = int(0.65 * height)
posy2 = int(alto1 - alto2)

# Crear dos subplots utilizando el método "subplots" de Matplotlib
fig, (ax1, ax2) = plt.subplots(2, 1, facecolor=colorfondo1)

# Establecer la geometría de la ventana de fig en la mitad izquierda de la pantalla
fig_manager = plt.get_current_fig_manager()
window = fig_manager.window
window.wm_geometry(f"{ancho1}x{alto1}+3+3")
# Crear dos subplots utilizando el método "subplots" de Matplotlib
fig_pq, ax3 = plt.subplots(facecolor=colorfondo3)

# Establecer la geometría de la ventana de fig_pq en la mitad derecha de la pantalla
fig_pq_manager = plt.get_current_fig_manager()
fig_pq_manager.window.wm_geometry(f"{ancho1-15}x{alto2+3}+{ancho2}+{posy2}")

plt.subplots_adjust(wspace=0.4)


# Función para actualizar los gráficos
def update_plots():
    global root, text_box1, text_box2, text_box3, text_box4
    # Inicializar la ventana y el cuadro de texto si es la primera vez
    if not 'root' in globals() or not 'text_box1' in globals():
        root = tk.Tk()

        # Crear la ventana y ubicarla en la esquina supperior derecha
        root.geometry(f"{ancho1-15}x{posy2-40}+{width-ancho1}+{0+3}")

        # Crear los widgets y ubicarlos en la ventana
        label1 = tk.Label(root, text="Deformación:")
        label1.grid(row=0, column=0, sticky='w')

        text_box1 = tk.Text(root, height=1, width=10)
        text_box1.grid(row=1, column=0)
        text_box1.configure(font=("Arial", 63), bg=colorfondo2, fg="#BD2A2E")
        text_box1.tag_add("centered", "1.0", "end")
        text_box1.tag_configure("centered", justify="center")

        label2 = tk.Label(root, text="Fuerza:")
        label2.grid(row=0, column=1, sticky='w')

        text_box2 = tk.Text(root, height=1, width=10)
        text_box2.grid(row=1, column=1)
        text_box2.configure(font=("Arial", 63), bg=colorfondo2, fg="#f7b924")
        text_box2.tag_add("centered", "1.0", "end")
        text_box2.tag_configure("centered", justify="center")

        label3 = tk.Label(root, text="Presión de Poros:")
        label3.grid(row=2, column=0, sticky='w')

        text_box3 = tk.Text(root, height=1, width=10)
        text_box3.grid(row=3, column=0)
        text_box3.configure(font=("Arial", 63), bg=colorfondo2, fg="#058768")
        text_box3.tag_add("centered", "1.0", "end")
        text_box3.tag_configure("centered", justify="center")

        label4 = tk.Label(root, text="N° de Labortorio")
        label4.grid(row=2, column=1, sticky='w')

        text_box4 = tk.Text(root, height=1, width=30)
        text_box4.grid(row=3, column=1)
        text_box4.configure(font=("Arial Black", 15), bg=colorfondo2, fg="#164773")
        text_box4.tag_add("centered", "1.0", "end")
        text_box4.tag_configure("centered", justify="center")      

    # Borrar el contenido anterior de los subplots
    ax1.clear()
    ax1.set_facecolor(colorfondo2)
    ax1.grid(color=colorlabel, linestyle='--', linewidth=0.5, alpha=0.3)
    ax1.set_xlabel('Deformación, mm', color=colorlabel)
    ax1.set_ylabel('Esfuerzo, kPa',color=colorlabel)
    ax1.tick_params(axis='x', colors=colorlabel)
    ax1.tick_params(axis='y', colors=colorlabel)
    ax1.set_title('Esfuerzo - Deformación')

    # Dibujar la gráfica actualizada para el primer subplot
    ax1.plot(muesta1['Deformacion'], muesta1['Esfuerzo desviador'], ':s', color=color2, markersize=3, alpha=1, label=Test1+' kPa')
    ax1.plot(muesta2['Deformacion'], muesta2['Esfuerzo desviador'], ':^', color=color3, markersize=3, alpha=1, label=Test2+' kPa')

    #ax1.plot(muestra3x['Deformacion'], muestra3x['Esfuerzo desviador'], ':^', color=color3x, markersize=3, alpha=1, label=Test3x+' kPa')
    #ax1.plot(muestra4x['Deformacion'], muestra4x['Esfuerzo desviador'], ':^', color=color4x, markersize=3, alpha=1, label=Test4x+' kPa')
    #ax1.plot(muestra5x['Deformacion'], muestra5x['Esfuerzo desviador'], ':^', color=color5x, markersize=3, alpha=1, label=Test5x+' kPa')

    ax1.plot(x_data, y1_data, ':o', color=color1, markersize=5, label=Test0+' kPa')
    ax1.legend(loc="upper left", framealpha=0.4)

    # Borrar el contenido anterior del segundo subplot
    ax2.clear()
    ax2.set_facecolor(colorfondo2)
    ax2.grid(color=colorlabel, linestyle='--', linewidth=0.5, alpha=0.2)
    ax2.set_xlabel('Deformación, mm', color=colorlabel)
    ax2.set_ylabel('Presión de poros, kPa', color=colorlabel)  
    ax2.tick_params(axis='x', colors=colorlabel)
    ax2.tick_params(axis='y', colors=colorlabel)
    ax2.set_title('Presion de Poros')

    # Dibujar la gráfica actualizada para el segundo subplot
    ax2.plot(muesta1['Deformacion'], muesta1['Presion de Poros'], ':s', color=color2, markersize=3, alpha=1, label=Test1+' kPa')
    ax2.plot(muesta2['Deformacion'], muesta2['Presion de Poros'], ':^', color=color3, markersize=3, alpha=1, label=Test2+' kPa')

    #ax2.plot(muestra3x['Deformacion'], muestra3x['Presion de Poros'], ':^', color=color3x, markersize=3, alpha=1, label=Test3x+' kPa')
    #ax2.plot(muestra4x['Deformacion'], muestra4x['Presion de Poros'], ':^', color=color4x, markersize=3, alpha=1, label=Test4x+' kPa')
    #ax2.plot(muestra5x['Deformacion'], muestra5x['Presion de Poros'], ':^', color=color5x, markersize=3, alpha=1, label=Test5x+' kPa')
    ax2.plot(x_data, y2_data, ':o', color=color1, markersize=5, label=Test0+' kPa')    
    ax2.legend(loc="upper left", framealpha=0.5, facecolor=colorfondo2)

    # Borrar el contenido anterior del tercer subplot
    ax3.clear()
    ax3.set_facecolor(colorfondo2)
    ax3.grid(color=colorlabel, linestyle='--', linewidth=0.5, alpha=0.1)
    ax3.set_xlabel('p, kPa')
    ax3.set_ylabel('q, kPa')
    ax3.set_title('Trayectoria de tensiones')

    # Dibujar la gráfica actualizada para el tercer subplot
    ax3.plot(muesta1[['p_e']],muesta1[['q_e']], ':o', markersize=3, color= color2)
    ax3.plot(muesta2[['p_e']], muesta2[['q_e']], ':o', markersize=3, color= color3)

    #ax3.plot(muestra3x[['p_e']], muestra3x[['q_e']], ':o', markersize=3, color= color3x)
    #ax3.plot(muestra4x[['p_e']], muestra4x[['q_e']], ':o', markersize=3, color= color4x)
    #ax3.plot(muestra5x[['p_e']], muestra5x[['q_e']], ':o', markersize=3, color= color5x)

    ax3.plot(p_e_data, q_e_data, ':o', markersize=3, color= color1)
    
    # Actualizar la ventana y mostrar el gráfico actualizado
    fig.canvas.draw()
    fig_pq.canvas.draw()
    plt.tight_layout()
    root.update_idletasks()
    root.update()

# Función para imprimir los últimos valores de deformación, fuerza y presión de poros
def print_values(x1, y1, y2):
    # Muestra los datos en los cuadros de texto correspondientes
    text_box1.delete(1.0, tk.END)  # Limpiar el cuadro de texto
    text_box1.insert(tk.END, f"{x1} mm", "centered")
    
    text_box2.delete(1.0, tk.END)  # Limpiar el cuadro de texto
    text_box2.insert(tk.END, f"{y1} kN", "centered")
    
    text_box3.delete(1.0, tk.END)  # Limpiar el cuadro de texto
    text_box3.insert(tk.END, f"{y2} kPa", "centered")
    
    text_box4.delete(1.0, tk.END)  # Limpiar el cuadro de texto
    text_box4.insert(tk.END, "LAB-I Triaxial", "centered")



#Valores predeterminados para calculo de esfuerzo y presiones, p-q, etc
#Presio de esfuezo efectivo de confinamiento


#antes de la consolidación
H0 = 20.00
D0 = 10.095
V0 = D0**2*np.pi/4*H0

#Despues de la consolidación
DV_C = 0
DH_0 = 0
H_C = H0-DH_0/10
A_C = (V0-DV_C)/H_C
PP0 = 0.00



# Ciclo infinito para leer continuamente los datos del archivo y actualizar los gráficos
while True:
    # Leer las últimas líneas del archivo
    with open(filename0, 'r') as f:
        last_line = f.readlines()[-1]
    
    # Separar las columnas
    data = last_line.split(",") 
    
    # Convertir las columnas a números
    x = float(data[4])  #Desplazamiento mm
    y1 = float(data[3]) #Fuerza kN
    y2 = float(data[6]) #Presion de poros kPa
     
     
    #calculos para esfuerzo y trayectoria de tensiones
    e_1 = 0.1*x/H_C
    A = A_C/(1-e_1)

    esf_desv = y1/A*10000

    u = y2 - PP0
    u = u

    sigma1 = esf_desv + sigma3
    sigma1_e = sigma1 - u
    sigma3_e = sigma3 - u

    p = (sigma1 + sigma3)/2
    q = (sigma1 - sigma3)/2
    p_e = (sigma1_e + sigma3_e)/2
    q_e = (sigma1_e - sigma3_e)/2

    # Añadir los datos a las matrices
    x_data.append(x)
    y1_data.append(esf_desv)
    y2_data.append(u)
    p_data.append(p)
    q_data.append(q)
    p_e_data.append(p_e)
    q_e_data.append(q_e)    
    
    # Actualizar los gráficos y el cuadro de texto
    update_plots()
    # imprimir los valores en la ventana aparte
    print_values(x, y1, y2)
    
    # Mostrar el gráfico actualizado
    plt.show(block=False)
    
    # Pausa de 0.1 segundos antes de leer la siguiente línea del archivo
    plt.pause(0.05)

# Iniciar el ciclo de eventos de la GUI
root.mainloop()