import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt

#global parameters
Mpl = 1
G = 1./(8*np.pi*Mpl**2)
m1 = 10**-6*Mpl
m2 = 10**-2*Mpl
phipk = 8*Mpl #the location of the peak of the additional gaussian potential
mu = 4*Mpl**2 # sigma^2 of the additional gaussian potential
alpha = 0

def V(phi,chi):
    return 1./2*m1**2*phi**2*(1 + alpha*np.tanh(m2*chi/Mpl**2)*np.exp(-(phi - phipk)**2/(2*mu)))

def V_phi(phi,chi):
    eps = 10**-6*Mpl
    return (V(phi+eps/2,chi) - V(phi-eps/2,chi))/eps

def V_chi(phi,chi):
    eps = 10**-6*Mpl
    return (V(phi,chi+eps/2) - V(phi,chi-eps/2))/eps

def d_dlna(var,lna,paras):
    H,phi,psi,chi,xi = var
    m1,m2 = paras
    return [(8*np.pi*G/(3*H))*(V(phi,chi) - H**2*(psi**2 + xi**2)) - H,
            psi,
            -2*psi - V_phi(phi,chi)/H**2 - (8*np.pi*G*psi/3)*(V(phi,chi)/H**2 - psi**2 - xi**2),
            xi,
            -2*xi - V_chi(phi,chi)/H**2 - (8*np.pi*G*xi/3)*(V(phi,chi)/H**2 - psi**2 - xi**2)]

def thirdH(phi,psi,chi,xi):
    return np.sqrt(2*V(phi,chi)/(3/(4*np.pi*G) - (psi**2 + xi**2)))

phi0 = 20
psi0 = 0
chi0 = 0
xi0 = 0
H0 = thirdH(phi0,psi0,chi0,xi0)
paras = [m1,m2]
var0 = [H0,phi0,psi0,chi0,xi0]

lnaStop = 100
num_of_pts = 100000
lnavals = np.linspace(0,lnaStop,num_of_pts)

sol = odeint(d_dlna,var0,lnavals,args=(paras,))
Hvals = sol[:,0]
phivals = sol[:,1]
psivals = sol[:,2]
chivals = sol[:,3]
xivals = sol[:,4]


plt.plot(lnavals,phivals)
plt.plot(lnavals,chivals)
plt.plot(lnavals,Hvals)
plt.show()

# perturbation fields
epsvals = 0.5*(psivals**2 + xivals**2)

def V_phi_phi(phi,chi):
    eps = 10**-6*Mpl
    return (V_phi(phi+eps/2,chi) - V_phi(phi-eps/2,chi))/eps

def V_phi_chi(phi,chi):
    eps = 10**-6*Mpl
    return (V_phi(phi,chi+eps/2) - V_phi(phi,chi-eps/2))/eps

def V_chi_chi(phi,chi):
    eps = 10**-6*Mpl
    return (V_chi(phi,chi+eps/2) - V_chi(phi,chi-eps/2))/eps


c_11_vals = V_phi_phi(phivals,chivals)/Hvals**2 + (1./Hvals**2)*(2*psivals*V_phi(phivals,chivals)) + (3 - epsvals)*psivals**2

c_12_vals = V_phi_chi(phivals,chivals)/Hvals**2 + (1./Hvals**2)*(psivals*V_chi(phivals,chivals)
                                                          + xivals*V_phi(phivals,chivals))+ (3 - epsvals)*psivals*xivals

c_21_vals = c_12_vals

c_22_vals = V_chi_chi(phivals,chivals)/Hvals**2 + (1./Hvals**2)*(2*xivals*V_chi(phivals,chivals)) + (3 - epsvals)*xivals**2

pert_start = num_of_pts//200    # start calculate perturbation at lnavals[pert_start]
avals = np.exp(lnavals)
dotavals = np.exp(lnavals)*Hvals
mk = 50   # k = mk*a*H
k = mk*Hvals[pert_start]*avals[pert_start]

# get_val_for_given_lna, return arr(lna)


def get_val(arr,x):
    return np.interp(x,lnavals,arr)


def d_dlna_ij(var,lna,paras):
    RP11, RQ11, IP11, IQ11, RP22, RQ22, IP22, IQ22 = var      #P = delta phi   Q = d(delta phi)/dlna
    m1, m2 = paras
    eps = get_val(epsvals,lna)
    a = np.exp(lna)
    H = get_val(Hvals,lna)
    c_11 = get_val(c_11_vals,lna)
    c_22 = get_val(c_22_vals,lna)
    c_12 = get_val(c_12_vals,lna)
    c_21 = get_val(c_21_vals,lna)
    result = [RQ11,
              (eps - 3)*RQ11 - (k**2/(a**2*H**2))*RP11,
              IQ11,
              (eps - 3)*IQ11 - (k**2/(a**2*H**2))*IP11,
              RQ22,
              (eps - 3)*RQ22 - (k**2/(a**2*H**2))*RP22,
              IQ22,
              (eps - 3)*IQ22 - (k**2/(a**2*H**2))*IP22]
    return result


RP11_0 = k/(np.sqrt(2)*avals[pert_start])
IP11_0 = IP22_0 = RP22_0 = 0
RQ11_0 = RQ22_0 = IQ22_0 = 0
IQ11_0 = -mk*k/(np.sqrt(2)*avals[pert_start])

ptb_init = [RP11_0,RQ11_0,IP11_0,IQ11_0,RP22_0,RQ22_0,IP22_0,IQ22_0]

ptb_sol = odeint(d_dlna_ij,ptb_init,lnavals[pert_start:],args=(paras,))

Re_delta_phi = ptb_sol[:,0]
Im_delta_phi = ptb_sol[:,2]
delta_phi = np.sqrt(Re_delta_phi**2 + Im_delta_phi**2)


plt.plot(lnavals[pert_start:],Re_delta_phi)
plt.plot(lnavals[pert_start:],Im_delta_phi)
plt.plot(lnavals[pert_start:],delta_phi)
plt.show()

crit_index = 0
while (avals[pert_start:]*delta_phi)[crit_index] < 5:
    crit_index += 1

plt.plot(lnavals[pert_start:crit_index+pert_start],k/dotavals[pert_start:crit_index+pert_start])
plt.plot(lnavals[pert_start:crit_index+pert_start],avals[pert_start:crit_index+pert_start]*delta_phi[0:crit_index])
plt.show()

crit_index = 0
while k/dotavals[crit_index] > 0.5:
    crit_index += 1


plt.plot(k/(dotavals[pert_start:crit_index]),avals[pert_start:crit_index]*delta_phi[0:crit_index-pert_start])
plt.show()
print(np.interp(1.0,k/(dotavals[pert_start:crit_index]),avals[pert_start:crit_index]*delta_phi[0:crit_index-pert_start]))

check0 = k - dotavals[pert_start:]
check = Hvals[pert_start:]/(delta_phi)
plt.plot(check0,check)
plt.show()

with open('check.txt','w') as fobj:
    for k in range(len(check0)):
        fobj.write(str(check0[k]) +'\t' + str(check[k]) + '\n')


ratio = np.interp(0.000001,check0,check)
print(ratio)

k_aH_vals = k/dotavals
dphi_dt = Hvals*psivals
Vvals = V(phivals,chivals)
V_phi_vals = V_phi(phivals,chivals)

with open('single_pert_late_k' + str(mk) +'.txt','w') as fobj:
    fobj.write('lna\tk/aH\tH\tRe(delta phi)\tIm(delta phi)\tdphi/dt\tV\tdV/dphi\n')
    for k in range((num_of_pts - pert_start) // 100):
        ak = 100*k
        bk = 100*k + pert_start
        fobj.write(str(lnavals[bk]) + '\t' + str(k_aH_vals[bk]) + '\t' + str(Hvals[bk]) + '\t' + str(Re_delta_phi[ak]) + '\t' + str(Im_delta_phi[ak]) + '\t' + str(dphi_dt[bk]) + '\t' +str(Vvals[bk])+'\t'+ str(V_phi_vals[bk]) +'\n')




# checking
'''
ReR = Re_delta_phi/psivals[pert_start:]
ImR = Im_delta_phi/psivals[pert_start:]
AbsR = ReR**2 + ImR**2

check1 = Hvals[pert_start:]**2/(4*np.pi**2*psivals[pert_start]**2*Mpl**4)
epsV_vals = (1./(2*Mpl**2))*(V_phi_vals/Vvals)**2
check2 = Hvals[pert_start:]**2/(8*np.pi**2*(epsV_vals[pert_start:])*Mpl**2)

check0 = AbsR/(2*np.pi**2)


'''

