from math import sin,cos,tan,acos,asin,atan,degrees,sqrt
Pe = 200000  #Potencia mecanica
N = 0.9   #Rendimiento
FP = 0.5  #Factor de potencia
Vs = 230   #Voltaje de alimentación

#Conversión potencia mecanica a potencia eléctrica
#Pe = PM*745.7 #Potencia electrica
Pa = Pe/N    #Potencia activa
Pap= Pa/FP #Potencia aparente
Preact = Pap*sin(acos(FP)) #Potencia reactiva
print("Potencia activa: ", round(Pa,3), "W")
print("Potencia aparente: ", round(Pap,3), "VA")
print("Potencia reactiva: ", round(Preact,3), "VAR")
print("Angulo de desfase: ", round(degrees(acos(FP)),3), "°")

#Corriente
IL = Pe/(sqrt(3)*Vs*FP*N) #Corriente de línea
IA = IL*FP #Corriente activa
IR = IL*sin(acos(FP)) #Corriente reactiva
print("Corriente de línea: ", round(IL,3), "A")
print("Corriente activa: ", round(IA,3), "A")
print("Corriente reactiva: ", round(IR,3), "A")

#Representación fasorial y compleja de la potencia:
Scomp = round(Pa,3) + (round(Preact,3)*1j) #Potencia compleja
print("Potencia compleja: ", Scomp, "VA")
print("Potencia fasorial: ", round(Pap,3),"+" ,round(degrees(acos(FP)),3), "VA")

