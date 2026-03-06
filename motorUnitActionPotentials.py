import numpy as np
import matplotlib.pyplot as plt
from actionPotential import ActionPotential

class MUAP:
    def __init__(self, t_vector, u_fiber_mean, x0, y0, z0, num_fibers = 400):
        self.t_vector = t_vector
        self.num_fibers = num_fibers
        self.muap_signal = np.zeros_like(t_vector)
        self.fibers = []

        mu_center_y = 10.0 
        mu_center_z = 0.0
        mu_radius = 5.0 

        for _ in range(num_fibers):
            u_fiber = np.random.normal(u_fiber_mean, 0.2)
            sigma_L_median_value = (0.33 + 0.80) / 2
            sigma_L_spread = (0.80 - sigma_L_median_value) / 3
            sigma_L = np.random.normal(sigma_L_median_value,sigma_L_spread)
            sigma_T_median_value = (0.04 + 0.15) / 2
            sigma_T_spread = (0.15 - sigma_T_median_value) / 3
            sigma_T = np.random.normal(sigma_T_median_value,sigma_T_spread)
            anisotropy = sigma_L/sigma_T

            angle = np.random.uniform(0, 2 * np.pi)
            r = mu_radius * np.sqrt(np.random.uniform(0, 1))
            yi_pos = mu_center_y + r * np.cos(angle)
            zi_pos = mu_center_z + r * np.sin(angle)
            
            delay_s = np.random.normal(0.002, 0.0002)

            fiber_length = np.random.uniform(40, 96)
            
            fiber = ActionPotential(
                t_vector=t_vector, 
                x0=x0, y0=y0, u=u_fiber,
                yi=yi_pos, zi=zi_pos,
                mu_sigma_L=sigma_L, 
                mu_sigma_T=sigma_T, 
                mu_anisotropy=anisotropy, 
                z0=z0,
                total_length=fiber_length,
                firing_delay_s=delay_s
            )
            self.fibers.append(fiber)

    def generate_signal(self):
        print(f"Calculating superposition for {self.num_fibers} fibers...")
        for fiber in self.fibers:
            fiber_signal = fiber.phi() 
            self.muap_signal += fiber_signal
            
        return self.muap_signal
