import cantera as ct
import numpy as np
import matplotlib.pyplot as plt
import csv

fuel = 'CH4'
mechanism = 'gri30.yaml'

T_init_kinetics = 1100.0
P_init_kinetics = ct.one_atm * 20.0

egr_fractions = np.linspace(0, 0.25, 15)
phi_values = [0.8, 1.0, 1.2]
colors = {0.8: 'blue', 1.0: 'green', 1.2: 'red'}

results = {
    'phi': [], 'egr': [],
    'T_ad': [], 'NO_ppm': [], 'CO_ppm': [],
    'ign_delay': []
}

time_history = {}
target_egr_for_time_plots = [0.0, 0.0536, 0.1071, 0.1607, 0.2143]

for phi in phi_values:
    for egr in egr_fractions:
        gas = ct.Solution(mechanism)

        gas.set_equivalence_ratio(phi, fuel, 'O2:1, N2:3.76')
        x_fuel = gas[fuel].X[0]
        x_o2 = gas['O2'].X[0]
        x_n2 = gas['N2'].X[0]

        comp = (f"{fuel}:{x_fuel * (1 - egr)}, O2:{x_o2 * (1 - egr)}, N2:{x_n2 * (1 - egr)}, "
                f"CO2:{egr * 0.5}, H2O:{egr * 0.5}")

        gas.TPX = 300.0, ct.one_atm, comp
        gas.equilibrate('HP')

        t_ad = gas.T
        no_ppm = gas['NO'].X[0] * 1e6
        co_ppm = gas['CO'].X[0] * 1e6

        is_time_plot_target = phi == 1.0 and any(
            np.isclose(egr, t_egr, atol=1e-3) for t_egr in target_egr_for_time_plots)

        gas.TPX = T_init_kinetics, P_init_kinetics, comp
        reactor = ct.IdealGasReactor(gas, clone=False)
        sim = ct.ReactorNet([reactor])

        time = 0.0
        t_max = 2.0
        dt = 5e-5

        t_hist = [0]
        T_hist = [gas.T]
        ign_delay = np.nan

        while time < t_max:
            time += dt
            sim.advance(time)

            if is_time_plot_target:
                t_hist.append(time)
                T_hist.append(reactor.T)

            if reactor.T > T_init_kinetics + 400 and np.isnan(ign_delay):
                ign_delay = time
                if not is_time_plot_target:
                    break

        if is_time_plot_target:
            matched_egr = min(target_egr_for_time_plots, key=lambda x: abs(x - egr))
            time_history[matched_egr] = {'time': t_hist, 'T': T_hist}

        results['phi'].append(phi)
        results['egr'].append(egr)
        results['T_ad'].append(t_ad)
        results['NO_ppm'].append(no_ppm)
        results['CO_ppm'].append(co_ppm)
        results['ign_delay'].append(ign_delay * 1000)

csv_file = 'egr_results.csv'
with open(csv_file, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Phi', 'EGR_fraction', 'T_ad_K', 'NO_ppm', 'CO_ppm', 'Ign_Delay_ms'])
    for i in range(len(results['phi'])):
        writer.writerow([
            results['phi'][i], results['egr'][i], results['T_ad'][i],
            results['NO_ppm'][i], results['CO_ppm'][i], results['ign_delay'][i]
        ])

plt.style.use('seaborn-v0_8-whitegrid')
ph_arr = np.array(results['phi'])
eg_arr = np.array(results['egr']) * 100
t_arr = np.array(results['T_ad'])
no_arr = np.array(results['NO_ppm'])
id_arr = np.array(results['ign_delay'])

plt.figure(figsize=(8, 6))
for phi in phi_values:
    idx = ph_arr == phi
    plt.plot(eg_arr[idx], t_arr[idx], color=colors[phi], marker='o', linewidth=2, label=f'$\\phi$={phi}')
plt.xlabel('EGR fraction [%]')
plt.ylabel('Adiabatic Flame Temp. [K]')
plt.title('Thermodynamic Effect: Temperature Reduction')
plt.legend()
plt.tight_layout()
plt.savefig('egr_temperature.png', dpi=300)
plt.close()

plt.figure(figsize=(8, 6))
for phi in phi_values:
    idx = ph_arr == phi
    plt.semilogy(eg_arr[idx], no_arr[idx], color=colors[phi], marker='s', linewidth=2, label=f'$\\phi$={phi}')
plt.xlabel('EGR fraction [%]')
plt.ylabel('NO Emission [ppm]')
plt.title('Environmental Effect: NOx Reduction')
plt.legend()
plt.tight_layout()
plt.savefig('egr_nox.png', dpi=300)
plt.close()

plt.figure(figsize=(8, 6))
for phi in phi_values:
    idx = ph_arr == phi
    plt.plot(eg_arr[idx], id_arr[idx], color=colors[phi], marker='^', linewidth=2, label=f'$\\phi$={phi}')
plt.xlabel('EGR fraction [%]')
plt.ylabel('Ignition Delay [ms]')
plt.title('Kinetic Effect: Autoignition Suppression')
plt.legend()
plt.tight_layout()
plt.savefig('egr_ignition_delay.png', dpi=300)
plt.close()

plt.figure(figsize=(8, 6))
for egr in sorted(time_history.keys()):
    data = time_history[egr]
    t_data = np.array(data['time']) * 1000
    T_data = data['T']
    plt.plot(t_data, T_data, linewidth=2, label=f'EGR={egr * 100:.1f}%')
plt.xlabel('Time [ms]')
plt.ylabel('Reactor Temperature [K]')
plt.title('Temperature Profiles over Time ($\\phi$=1.0)')
plt.xlim(0, 15)
plt.legend()
plt.tight_layout()
plt.savefig('egr_time_history.png', dpi=300)
plt.close()