
#%%
import os
import re
import pandas as pd

parameter_list = ('Zero-point correction',
                  'Thermal correction to Energy',
                  'Thermal correction to Enthalpy',
                  'Thermal correction to Gibbs Free Energy',
                  'Sum of electronic and zero-point Energies',
                  'Sum of electronic and thermal Energies',
                  'Sum of electronic and thermal Enthalpies',
                  'Sum of electronic and thermal Free Energies')

properties_list = ['Total',
                   'Electronic',
                   'Translational',
                   'Rotational',
                   'Vibrational']

Freaks_global = []
Freaks_current = []
Total_E, Electronic_E, Translational_E, Rotational_E, Vibrational_E = [],[],[],[],[]
Total_S, Electronic_S, Translational_S, Rotational_S, Vibrational_S = [],[],[],[],[]
D_freaks_rev_sm = {}

file_vec = []
file_vec_new = []
for root, dirs, files in os.walk(os.getcwd()):
    for file in files:
        if file.endswith(".log"):
            current_way = os.path.join(root, file)
            file_vec.append(current_way)
print (file_vec, sep = '\n')


D_main = {properties:[] for properties in parameter_list}
    
for file in file_vec:
    file_name = str(file)
    with open(file_name, "r") as f:
        #print (f.readlines().index(' - Thermochemistry -\n'))
        lines_vector = f.readlines()
        if " - Thermochemistry -\n" in lines_vector:
            file_vec_new.append(file_name)
            for line in lines_vector:
                Armageddez = re.search ('(\w+)\s\-\-\s*([-\d.]+)\s*([-\d.]+)\s*([-\d.]+)', line)
                if Armageddez:
                    if (Armageddez.group(1)) == 'Frequencies':
                        #print (Armageddez.group(2), Armageddez.group(3), Armageddez.group(4))
                        for i in range (2,5):
                            Freaks_current.append(Armageddez.group(i))
                        
                for i in parameter_list:
                    Nechto = re.search ('(-?[0-9]{1,4}\.[0-9]{6})', line)
                    if Nechto:
                        if i in line:
                            D_main[i].append(Nechto.group(1))
                            #print (D_main)
                for k in properties_list:
                    Nerd = re.search('([0-9]{1,4}\.[0-9]{3})\s{2,15}([0-9]{1,4}\.[0-9]{3})\s{2,15}([0-9]{1,4}\.[0-9]{3})', line)
                    if Nerd:
                        if k in line:
                            current_E_Thermal = k + '_E'
                            current_S = k + '_S'
                            globals()[current_E_Thermal].append(line.split()[1])
                            globals()[current_S].append(line.split()[3])
    Freaks_global.append(Freaks_current)
    Freaks_current = []
#print(Freaks_global)
print (file_vec_new)

 


#%%
D_properties = {'Total_E':Total_E, 'Electronic_E':Electronic_E, 'Translational_E':Translational_E, 'Rotational_E': Rotational_E, 'Vibrational_E':Vibrational_E,
               'Total_S':Total_S, 'Electronic_S':Electronic_S, 'Translational_S':Translational_S, 'Rotational_S': Rotational_S, 'Vibrational_S':Vibrational_S}
table_Gaus_properties = pd.DataFrame(D_properties)
table_Gaus_properties.index = file_vec_new
print (table_Gaus_properties)


#%%
table_Gaus_main = pd.DataFrame(D_main)
table_Gaus_main.index = file_vec_new


#%%
D_freaks_rev_sm = dict(zip(file_vec,Freaks_global))
print (D_freaks_rev_sm)


#%%
table_Gaus_global = pd.concat([table_Gaus_main, table_Gaus_properties], axis = 1)
table_Gaus_global.to_csv('Gaussian_Vica.csv', sep='\t')
print (table_Gaus_global)


#%%



