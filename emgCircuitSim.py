import matplotlib.pyplot as plt
import numpy as np
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *
import math
from scipy.integrate import quad

circuit = Circuit('EMG Circuit')

circuit.include('INA128.LIB')
circuit.include('TL072.LIB')

positive_input_pwl_data = np.loadtxt('emg_positive_input.pwl')
positive_input_pwl_values = [tuple(row) for row in positive_input_pwl_data]

negative_input_pwl_data = np.loadtxt('emg_negative_input.pwl')
negative_input_pwl_values = [tuple(row) for row in negative_input_pwl_data]

# circuit.X(Name, Model, In+, In-, V+, V-, Out, Ref, RG1, RG2)
circuit.X('U1', 'INA128', 'ina_in_pos', 'ina_in_neg', 'ina_vcc', 'ina_vee', 'ina_out', circuit.gnd, 'ina_gain_node_1', 'ina_gain_node_2')

# circuit.X(Name, Model, In+, In-, V+, V-, Out)
circuit.X('U2', 'TL072', 'tl_in_pos','tl_in_neg','tl_vcc','tl_vee','tl_out')
circuit.X('U3', 'TL072', 'notch_in_pos','notch_out','tl_vcc','tl_vee','notch_out')
circuit.X('U4', 'TL072', 'notch_feedback_in_pos','notch_feedback_out','tl_vcc','tl_vee','notch_feedback_out')

# Grounding the subject
circuit.SinusoidalVoltageSource('V_BONE', 'electrode', circuit.gnd, amplitude=0.05@u_V, frequency=50@u_Hz) # type: ignore

# First Stage INA128 intsrumentation amplifier

# Gain Resistor 
circuit.R('RG', 'ina_gain_node_1', 'ina_gain_node_2', 505@u_Ohm) # type: ignore

# IC Supply
circuit.V('INA_VCC','ina_vcc',circuit.gnd,10@u_V) # type: ignore
circuit.V('INA_VEE','ina_vee',circuit.gnd,-10@u_V) # type: ignore
circuit.V('TL_VCC','tl_vcc',circuit.gnd,10@u_V) # type: ignore
circuit.V('TL_VEE','tl_vee',circuit.gnd,-10@u_V) # type: ignore

# IC Input
circuit.PieceWiseLinearVoltageSource('ina_vminus', 'ina_in_neg', circuit.gnd, values=negative_input_pwl_values)
circuit.PieceWiseLinearVoltageSource('ina_vplus', 'ina_in_pos', 'electrode', values=positive_input_pwl_values)

# Notch Filter
circuit.C('notch_c1','ina_out','c_middle',0.1@u_uF) # type: ignore
circuit.C('notch_c2','c_middle','notch_network_out',0.1@u_uF) # type: ignore
circuit.R('notch_r1','c_middle',circuit.gnd,15.91@u_kOhm) # type: ignore 

circuit.R('notch_r2','ina_out','r_middle',31.83@u_kOhm) # type: ignore 
circuit.R('notch_r3','r_middle','notch_network_out',31.83@u_kOhm) # type: ignore 
circuit.C('notch_c3','r_middle',circuit.gnd,0.2@u_uF) # type: ignore 

circuit.R('tie_notch_to_amp','notch_network_out','notch_in_pos',1@u_Ohm) # type: ignore 

# Notch Feedback

circuit.R('notch_feedback_r1','notch_out','notch_feedback_middle',10@u_kOhm) # type: ignore
circuit.R('notch_feedback_r2','notch_feedback_middle',circuit.gnd,90@u_kOhm) # type: ignore

# High Pass Filter
circuit.C('high_pass_c', 'notch_out', 'tl_in_pos', 0.8@u_uF) # type: ignore
circuit.R('high_pass_r','tl_in_pos',circuit.gnd,10@u_kOhm) # type: ignore
circuit.R('tl_rminus','tl_in_neg',circuit.gnd, 1@u_kOhm)# type: ignore

# TL072 Output
circuit.R('RF','tl_out','tl_in_neg', 10@u_kOhm)# type: ignore

# Low Pass Filter
circuit.R('low_pass_r','tl_out','circuit_out',10@u_kOhm) # type: ignore
circuit.C('low_pass_c','circuit_out',circuit.gnd,0.031@u_uF) # type: ignore

simulator = circuit.simulator(temperature=25, nominal_temperature=25)
simulator.options(
    reltol=0.01,
    gmin=1e-10,
    chgtol=1e-13,
    itl1=1000,
    itl2=1000
)

try:
    analysis = simulator.transient(step_time=10@u_us, end_time=2@u_s) # type: ignore

    # 2. Updated DFT Function for Isolation
    def get_dft(node_name):
        voltages = np.array(analysis[node_name])
        N = len(voltages)
        fft_values = np.fft.rfft(voltages)
        freqs = np.fft.rfftfreq(N, d=10e-6)
        mags = np.abs(fft_values) * (2 / N)
        return freqs, mags

    f_pre, m_pre = get_dft('ina_out')     # Input to Notch
    f_post, m_post = get_dft('notch_out')    # Output of Notch Buffer
    f_final, m_final = get_dft('circuit_out') # Final System Output

    target_hz = 50.0 
    idx_50 = np.argmin(np.abs(f_pre - target_hz))

    hum_before = 20 * np.log10(m_pre[idx_50] + 1e-9)
    hum_after = 20 * np.log10(m_post[idx_50] + 1e-9)
    rejection = hum_before - hum_after

    print(f"\n--- TWIN-T NOTCH VERIFICATION (STAGE ISOLATION) ---")
    print(f"Target Frequency:       {target_hz} Hz")
    print(f"Magnitude Pre-Notch:    {hum_before:.2f} dBV")
    print(f"Magnitude Post-Notch:   {hum_after:.2f} dBV")
    print(f"Isolated Notch Depth:   {rejection:.2f} dB")

    # --- PLOTS ---
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

    ax1.plot(analysis.time, analysis['ina_out'], color='gray', alpha=0.4, label='Raw INA Out (With Hum)')
    ax1.plot(analysis.time, analysis['notch_out'], color='blue', label='Post-Notch (Cleaned)')
    ax1.set_xlim(0.5, 0.6) 
    ax1.set_title('Time Domain: 50Hz Hum Removal (Zoomed View)')
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Voltage (V)')
    ax1.legend()
    ax1.grid(True)

    ax2.plot(f_pre, 20*np.log10(m_pre + 1e-9), color='gray', alpha=0.3, label='Input to Notch')
    ax2.plot(f_post, 20*np.log10(m_post + 1e-9), color='blue', linewidth=1.5, label='Notch Output (Isolated)')
    ax2.plot(f_final, 20*np.log10(m_final + 1e-9), color='red', linewidth=2, label='Total System Output')

    f_low = 19.9
    f_high = 513.4
    ax2.axvspan(f_low, f_high, color='green', alpha=0.1, label='EMG Passband (20Hz-500Hz)')

    ax2.set_xlim(5, 600) 
    ax2.set_ylim(-100, 20) # Elevated ceiling to accommodate the final 11x gain
    ax2.axvline(x=target_hz, color='purple', linestyle='--', alpha=0.7, label=f'Notch @ {target_hz}Hz')
    ax2.set_title('Frequency Response: Full Chain Bandwidth & Notch Performance')
    ax2.set_xlabel('Frequency (Hz)')
    ax2.set_ylabel('Magnitude (dBV)')
    ax2.legend(loc='upper right')
    ax2.grid(True, which='both')

    plt.tight_layout()
    plt.show()


except Exception as e:
    print(f"Simulation failed: {e}")