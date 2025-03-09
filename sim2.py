import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Total population
N = 1000
# Initial number of infected and recovered individuals
I0, R0 = 1, 0
# Everyone else is susceptible to infection initially
S0 = N - I0 - R0

# Contact rate, beta, and mean recovery rate, gamma, (in 1/days)
beta, gamma = 0.3, 1./14
# Mortality rate
mortality_rate = 0.01

# A grid of time points (in days)
days = 365
t = np.linspace(0, days, days)

# SIR model differential equations
def deriv(y, t, N, beta, gamma, mortality_rate):
    S, I, R, D = y
    dSdt = -beta * S * I / N
    dIdt = beta * S * I / N - gamma * I
    dRdt = gamma * I * (1 - mortality_rate)
    dDdt = gamma * I * mortality_rate
    return dSdt, dIdt, dRdt, dDdt

# Initial conditions vector
y0 = S0, I0, R0, 0

# Integrate the SIR equations over the time grid, t.
from scipy.integrate import odeint
ret = odeint(deriv, y0, t, args=(N, beta, gamma, mortality_rate))
S, I, R, D = ret.T

# Plotting
fig, ax = plt.subplots()
ax.set_xlim(0, days)
ax.set_ylim(0, N)
ax.set_xlabel('Days')
ax.set_ylabel('Number of Individuals')
ax.set_title('Mpox Outbreak Simulation')

line_susceptible, = ax.plot([], [], 'b', label='Susceptible')
line_infected, = ax.plot([], [], 'r', label='Infected')
line_recovered, = ax.plot([], [], 'g', label='Recovered')
line_deceased, = ax.plot([], [], 'k', label='Deceased')
ax.legend()

def init():
    line_susceptible.set_data([], [])
    line_infected.set_data([], [])
    line_recovered.set_data([], [])
    line_deceased.set_data([], [])
    return line_susceptible, line_infected, line_recovered, line_deceased

def update(frame):
    line_susceptible.set_data(t[:frame], S[:frame])
    line_infected.set_data(t[:frame], I[:frame])
    line_recovered.set_data(t[:frame], R[:frame])
    line_deceased.set_data(t[:frame], D[:frame])
    return line_susceptible, line_infected, line_recovered, line_deceased

ani = FuncAnimation(fig, update, frames=len(t), init_func=init, blit=True)
plt.show()
