import numpy as np

class ActionPotential:
    phi_array = np.array([])

    def __init__(self,t_vector,x0,y0, yi, zi,u,mu_sigma_L,mu_sigma_T,mu_anisotropy,z0=0,total_length=96, firing_delay_s=0.002):
        self.t_vector = t_vector
        self.dt = self.t_vector[1] - self.t_vector[0]
        self.x0 = x0
        self.y0 = y0
        self.z0= z0

        # Fiber Properties
        self.yi = yi
        self.zi = zi
        self.u = u
        self.mu_anisotropy = mu_anisotropy
        self.sigma_T = mu_sigma_T
        self.sigma_L = mu_sigma_L
        self.total_length = total_length
        self.firing_delay_s = firing_delay_s

        self.x_ep = (total_length / 2) + np.random.uniform(-5, 5)
        self.L1 = self.x_ep
        self.L2 = total_length - self.x_ep
        
        self.phi_array = np.zeros_like(t_vector)
 
    def vm(self,t):
        z = self.u * t * 1000
        return 96 * (z**3) * np.exp(-z) - 90

    def impulse_response(self,t):
        vt = self.u * t * 1000

        pos1 = self.x_ep - vt
        pos2 = self.x_ep + vt

        c1 = (pos1 >= 0).astype(float)
        c2 = (pos2 <= (self.L1 + self.L2)).astype(float)

        radial_gap_sq = (self.y0 - self.yi)**2 + (self.z0 - self.zi)**2
        radial_term = self.mu_anisotropy * radial_gap_sq

        denom1 = np.sqrt((self.x0 - pos1)**2 + radial_term)
        denom2 = np.sqrt((self.x0 - pos2)**2 + radial_term)

        ir = (1 / (4 * np.pi * self.sigma_T)) * ((c1 / denom1) + (c2 / denom2))
        return np.nan_to_num(ir)

    def phi(self):
        t_active = np.maximum(0, self.t_vector - self.firing_delay_s)

        vm_values = self.vm(t_active)
        dVm_dt = np.gradient(vm_values, self.dt)
        d2Vm_dt2 = np.gradient(dVm_dt, self.dt)

        d = 0.05
        cable_scale = (self.sigma_T * np.pi * (d**2)) / 4
        transmembrane_current = cable_scale * d2Vm_dt2

        ir_values = self.impulse_response(self.t_vector)

        full_convolution = np.convolve(transmembrane_current,ir_values,mode='full') * self.dt
        convolution_values = full_convolution[:len(self.t_vector)]

        self.phi_array = (self.mu_anisotropy / self.u) * convolution_values

        return self.phi_array

