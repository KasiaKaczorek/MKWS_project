# Numerical Analysis of Exhaust Gas Recirculation (EGR) Effects on Methane-Air Combustion Kinetics Using Cantera

This repository contains the source code and verification files for the "Computer Methods in Combustion" (MKWS) university project.

## Overview
The project evaluates the thermodynamic, environmental ($NO_x$ emissions), and kinetic (ignition delay) impacts of Exhaust Gas Recirculation (EGR) on a stoichiometric $CH_4$/Air mixture. 

## Files in this repository:
* `simulation.py` - The main Python script utilizing the Cantera library and GRI-Mech 3.0 mechanism to calculate adiabatic flame temperature, $NO_x$ mass fractions, and transient autoignition delay across an EGR sweep (0-25%).
* `NASA_CEA_Inputs/` - Structural `.inp` verification files designed to validate the thermodynamic equilibrium results against the NASA Chemical Equilibrium with Applications (CEA) code.
* `egr_results.csv` - Raw exported data from the Cantera simulation.
* Generated plots (`.png`) showcasing the physical mechanisms of EGR.
* Report.pdf - The comprehensive technical report detailing the theoretical background, methodology, and conclusions of the numerical analysis. It features the cross-validation between Cantera and NASA CEA, temporal reactor profiles, alongside a brief engineering comparison with real-world heavy-duty natural gas engines to provide practical context.
