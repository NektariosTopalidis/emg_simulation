import numpy as np
import matplotlib.pyplot as plt
from motorUnitActionPotentials import MUAP

def create_sequence(t, fs):
    mvc_seq = np.zeros_like(t)
    
    def add_movement(start_t, duration, peak=50, steepness=100):
        start_idx = int(start_t * fs)
        end_idx = int((start_t + duration) * fs)
        if start_idx >= len(t): return
        
        chunk_t = t[start_idx:end_idx]
        
        onset = peak / (1 + np.exp(-steepness * (chunk_t - (start_t + 0.05))))
        release = (1 - 1 / (1 + np.exp(-steepness * (chunk_t - (start_t + duration - 0.05)))))
        mvc_seq[start_idx:end_idx] = onset * release

    # --- DEFINE YOUR CHAIN HERE ---
    add_movement(start_t=0.4, duration=0.1, peak=70) 
    add_movement(start_t=0.6, duration=0.1, peak=80)
    add_movement(start_t=0.9, duration=0.5, peak=60, steepness=5)
    add_movement(start_t=1.5, duration=0.4, peak=85)
    
    baseline_noise = np.random.normal(0, 0.2, len(t))
    mvc_seq += baseline_noise
    mvc_seq += np.random.normal(0, 1.2, len(t))
    return np.clip(mvc_seq, 0, 100)

def save_for_pyspice(t, signal, filename):
    """Exports time and voltage for PySpice (scales uV to Volts)."""
    signal_volts = signal * 1e-6 
    data = np.column_stack((t, signal_volts))
    np.savetxt(filename, data, fmt='%1.6e %1.6e')
    print(f"File saved: {filename}")

def emg_signal_sim():
    fs = 10000
    duration = 2.0 
    t = np.arange(0, duration, 1/fs)

    emg_engine = EMGSignal(t_vector=t, x0=10, y0=0, z0=0, num_units=200)

    mvc_profile = create_sequence(t, fs)

    biological_signal = emg_engine.simulate(mvc_profile)

    hum_50hz = 5.0 * np.sin(2 * np.pi * 50 * t)
    random_noise = np.random.normal(0, 1.5, len(t))

    dirty_pos = biological_signal + hum_50hz + random_noise
    dirty_neg = (np.roll(biological_signal, 20) * 0.95) + (hum_50hz * 0.85) + random_noise

    save_for_pyspice(t, dirty_pos, "emg_positive_input.pwl")
    save_for_pyspice(t, dirty_neg, "emg_negative_input.pwl")

    plt.figure(figsize=(12, 6))
    plt.subplot(2, 1, 1)
    plt.plot(t, mvc_profile)
    plt.title("Squeeze Effort (% MVC)")
    plt.ylabel("Intensity")

    plt.subplot(2, 1, 2)
    plt.plot(t, dirty_pos, color='purple')
    plt.title("Synthetic FDS EMG Signal (Interference Pattern)")
    plt.xlabel("Time (s)")
    plt.ylabel("Potential (uV)")
    plt.tight_layout()
    plt.show()


class EMGSignal:
    def __init__(self, t_vector, x0=10, y0=0, z0=0, num_units=20):
        self.t_vector = t_vector
        self.dt = t_vector[1] - t_vector[0]
        self.num_units = num_units
        self.x0, self.y0, self.z0 = x0, y0, z0

        indices = np.arange(num_units)
        self.fiber_counts = (50 * np.exp(np.log(800/50) * indices / (num_units - 1))).astype(int)

        self.thresholds = 90 * (indices / (num_units - 1))**1.5

        self.muap_pool = []
        self._build_pool()

    def _build_pool(self):
        for i in range(self.num_units):
            print(f"Iteration: {i+1}/{self.num_units}")

            u_velocity = 3.0 + (2.0 * (i / self.num_units))
            
            unit = MUAP(
                t_vector=self.t_vector, 
                u_fiber_mean=u_velocity, 
                x0=self.x0, y0=self.y0, z0=self.z0, 
                num_fibers=self.fiber_counts[i]
            )
            self.muap_pool.append(unit.generate_signal())

    def simulate(self, mvc_profile):
        full_signal = np.zeros_like(self.t_vector)
        num_samples = len(self.t_vector)

        for i, muap_signature in enumerate(self.muap_pool):
            threshold = self.thresholds[i]
            
            t_idx = 0
            while t_idx < num_samples:
                current_mvc = mvc_profile[t_idx]
                
                if current_mvc > threshold:
                    hz = 8 + 0.4 * (current_mvc - threshold)
                    hz = min(hz, 35)
                    
                    start_idx = t_idx
                    end_idx = min(num_samples, start_idx + len(muap_signature))
                    full_signal[start_idx:end_idx] += muap_signature[:(end_idx - start_idx)]
                    
                    interval = int((1 / hz) / self.dt)
                    jitter = int(np.random.normal(0, 0.1 * interval))
                    t_idx += max(1, interval + jitter) # Move to next pulse
                else:
                    t_idx += 1
        
        return full_signal
    

emg_signal_sim()