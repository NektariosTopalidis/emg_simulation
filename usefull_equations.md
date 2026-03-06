## Rosenfalck Equation for Action Potential

$$V_m(z) = 96z^3 e^{-z} - 90$$

- Time Domain:
  $$V_m(t) = 96(u*t)^3 e^{-u*t} - 90$$

### Breakdown of the Rosenfalck Equation Components

| Component             | Mathematical Representation | Description                                                                                                                                      |
| :-------------------- | :-------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------- |
| **Axial Distance**    | $z$                         | The longitudinal distance along the muscle fiber axis, representing the physical space the Action Potential travels from the motor end-plate.    |
| **Resting Potential** | $-90$                       | The stable electrical charge (in mV) of the muscle cell membrane when it is not being stimulated; the "baseline" of the cell.                    |
| **Shaping Function**  | $96z^3 e^{-z}$              | The mathematical "pulse" generator that creates the steep rise and exponential decay, defining the characteristic spike of the Action Potential. |

<br>
<br>
<br>

## Transmembrane Current Density: $i_m(z)$

$$i_m(z) = \frac{\sigma_{in} \pi d^2}{4} \cdot \frac{d^2 V_m(z)}{dz^2}$$

| Variable      | Description                                                                             | Typical Value          |
| :------------ | :-------------------------------------------------------------------------------------- | :--------------------- |
| $i_m(z)$      | **Transmembrane Current Density**: Current per unit length crossing the fiber membrane. | Amperes/meter (A/m)    |
| $\sigma_{in}$ | **Intracellular Conductivity**: Electrical conductivity inside the muscle fiber.        | ~1.01 S/m              |
| $d$           | **Fiber Diameter**: The physical thickness of a single muscle fiber.                    | 20 $\mu$m - 100 $\mu$m |
| $V_m(z)$      | **Transmembrane Potential**: Internal voltage (Rosenfalck model).                       | Millivolts (mV)        |
| $z$           | **Axial Distance**: Coordinate along the fiber length.                                  | Millimeters (mm)       |

<br>
<br>
<br>

## Extracellular Potential: $\phi(z)$ (Anisotropic Model)

$$\phi(z) = \frac{1}{4\pi\sigma_r} \int_{-\infty}^{\infty} \frac{i_m(\zeta)}{\sqrt{(\sigma_z/\sigma_r)r^2 + (z - \zeta)^2}} d\zeta$$

| Variable            | Description                                                                                       | Typical Value      |
| :------------------ | :------------------------------------------------------------------------------------------------ | :----------------- |
| $\phi(z)$           | **Extracellular Potential**: The final voltage detected by the surface electrode at position $z$. | Millivolts (mV)    |
| $i_m(\zeta)$        | **Current Density Source**: The current value at point $\zeta$ along the fiber.                   | Derived from $V_m$ |
| $r$                 | **Radial Distance**: The depth of the muscle fiber beneath the skin/electrode.                    | 2 mm - 15 mm       |
| $\sigma_z$          | **Axial Conductivity**: Electrical conductivity along the fiber direction.                        | ~0.33 S/m          |
| $\sigma_r$          | **Radial Conductivity**: Electrical conductivity perpendicular to the fiber.                      | ~0.04 S/m          |
| $\sigma_z/\sigma_r$ | **Anisotropy Ratio**: The ratio of longitudinal to transverse conductivity.                       | 5:1 to 10:1        |

---

<br>
<br>
<br>

## Fiber diameter

You can certainly use PCSA to work backward toward a diameter, but there is a catch: PCSA represents the area of all the fibers in the muscle added together, while the diameter you need for your code is for one single fiber.To get the individual fiber diameter from the PCSA, you have to divide the total area by the total number of fibers in that muscle.The "PCSA to Diameter" FormulaIf you have the PCSA and the total fiber count (which we discussed earlier from the Duchateau & Enoka paper), you can find the average individual fiber CSA first, then convert that to a diameter.Find Average Individual CSA:$$\text{Individual CSA} = \frac{PCSA}{\text{Total Number of Fibers}}$$Convert to Diameter ($d$):$$d = 2 \times \sqrt{\frac{\text{Individual CSA}}{\pi}}$$Why this is actually more accurateUsing the PCSA from a source like the Journal of Anatomy [cite: 1] is often more "honest" for your simulation because:Pennation Angle: PCSA accounts for the fact that in the Flexor Digitorum, fibers are "pennated" (angled like a feather)[cite: 1].True Force-Electric Link: Since PCSA is the gold standard for predicting a muscle's force[cite: 1], using it to derive your fiber diameter ensures that the "electrical" amplitude in your PySpice circuit matches the "mechanical" strength of a real human arm.Typical Values for the Flexor DigitorumAccording to studies on forearm architecture[cite: 1]:FDS PCSA: Ranges roughly between 15 and 25 $cm^2$ depending on the specific finger compartment and the size of the individual[cite: 1].Total Fibers: If the FDS has ~100,000 to 150,000 total fibers across all compartments[cite: 1], the math usually brings you right back to that 50–60 $\mu m$ diameter we've been using.
