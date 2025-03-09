import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib

matplotlib.use('TkAgg')  # Use TkAgg backend for animation display

class Person:
    def __init__(self, x, y, status="susceptible", recovery_time=14):
        self.x = x
        self.y = y
        self.status = status  # "susceptible", "infected", "recovered", or "dead"
        self.infection_time = 0
        self.recovery_time = recovery_time
        self.velocity = np.random.normal(0, 0.01, 2)  # Random velocity vector

    def move(self, bounds):
        # Update position based on velocity
        self.x += self.velocity[0]
        self.y += self.velocity[1]

        # Randomly change direction occasionally
        if np.random.random() < 0.05:
            self.velocity = np.random.normal(0, 0.01, 2)

        # Ensure staying within bounds
        if self.x < 0 or self.x > bounds[0]:
            self.velocity[0] *= -1
            self.x = np.clip(self.x, 0, bounds[0])
        if self.y < 0 or self.y > bounds[1]:
            self.velocity[1] *= -1
            self.y = np.clip(self.y, 0, bounds[1])

class MpoxSimulation:
    def __init__(self, 
                 population_size=200, 
                 initial_infected=2,
                 transmission_radius=0.03,  
                 transmission_rate=0.3,     
                 recovery_time=14,          
                 area_size=(1, 1),
                 cfr=0.01):  # Case Fatality Rate (CFR)
        
        self.population_size = population_size
        self.transmission_radius = transmission_radius
        self.transmission_rate = transmission_rate
        self.recovery_time = recovery_time
        self.area_size = area_size
        self.time = 0
        self.cfr = cfr
        
        # Create population
        self.population = []
        for i in range(population_size):
            x = np.random.random() * area_size[0]
            y = np.random.random() * area_size[1]
            status = "infected" if i < initial_infected else "susceptible"
            self.population.append(Person(x, y, status, recovery_time))
            
        # Track epidemic data
        self.data = {
            'time': [0],
            'susceptible': [population_size - initial_infected],
            'infected': [initial_infected],
            'recovered': [0],
            'deaths': [0]
        }
    
    def update(self):
        self.time += 1
        
        # Move all people
        for person in self.population:
            person.move(self.area_size)
        
        # Check for new infections and recoveries/deaths
        for person in self.population:
            if person.status == "infected":
                person.infection_time += 1
                
                # Check for recovery or death
                if person.infection_time >= person.recovery_time:
                    if np.random.random() < self.cfr:  # Apply case fatality rate
                        person.status = "dead"
                    else:
                        person.status = "recovered"
                
                # Check for transmission
                for other in self.population:
                    if other.status == "susceptible":
                        distance = np.sqrt((person.x - other.x)**2 + (person.y - other.y)**2)
                        if distance <= self.transmission_radius:
                            # Transmission probability
                            if np.random.random() < self.transmission_rate:
                                other.status = "infected"
        
        # Update statistics
        susceptible = sum(1 for p in self.population if p.status == "susceptible")
        infected = sum(1 for p in self.population if p.status == "infected")
        recovered = sum(1 for p in self.population if p.status == "recovered")
        deaths = sum(1 for p in self.population if p.status == "dead")
        
        self.data['time'].append(self.time)
        self.data['susceptible'].append(susceptible)
        self.data['infected'].append(infected)
        self.data['recovered'].append(recovered)
        self.data['deaths'].append(deaths)
        
        return self.get_positions_and_statuses()
    
    def get_positions_and_statuses(self):
        x = [p.x for p in self.population]
        y = [p.y for p in self.population]
        status = [p.status for p in self.population]
        return x, y, status
    
    def get_data(self):
        return self.data

# Create interactive simulation visualization
plt.style.use('ggplot')
fig = plt.figure(figsize=(12, 8))
fig.suptitle('Mpox Transmission Simulation (WHO/CDC Parameters)', fontsize=16)

# Create layout with multiple subplots
gs = plt.GridSpec(2, 2, height_ratios=[4, 1])
ax_sim = plt.subplot(gs[0, 0])  # Simulation plot
ax_stats = plt.subplot(gs[0, 1])  # Statistics plot
ax_info = plt.subplot(gs[1, :])  # Information text

# Set up axes
ax_sim.set_title('Population Simulation')
ax_sim.set_xlim(0, 1)
ax_sim.set_ylim(0, 1)
ax_sim.set_aspect('equal')

ax_stats.set_title('Epidemic Curve')
ax_stats.set_xlabel('Days')
ax_stats.set_ylabel('Number of People')

ax_info.axis('off')
info_text = """
Mpox Epidemiological Parameters (WHO/CDC):
- Incubation period: 5-21 days
- Infectious period: 2-4 weeks (14 days in this simulation)
- Transmission: Direct contact (modeled as proximity in simulation)
- Transmission rate: ~30% chance on close contact
- Case fatality: <1% for clade II, up to 10% for clade I
Color Legend:
- Green: Susceptible individuals
- Red: Infected individuals 
- Blue: Recovered individuals
- Black: Deceased individuals
"""
ax_info.text(0.5, 0.5, info_text, ha='center', va='center', fontsize=10)

# Initialize simulation
sim = MpoxSimulation(
    population_size=200, 
    initial_infected=3, 
    transmission_radius=0.03, 
    transmission_rate=0.3, 
    recovery_time=14, 
    cfr=0.01  # Example CFR of 1%
)

x, y, status = sim.get_positions_and_statuses()

# Initialize scatter plot with empty data
color_map = {'susceptible': 'green', 'infected': 'red', 'recovered': 'blue', 'dead': 'black'}
colors = [color_map[s] for s in status]
scatter = ax_sim.scatter(x, y, c=colors, alpha=0.8)

# Initialize line plots with empty data
data = sim.get_data()
susceptible_line, = ax_stats.plot(data['time'], data['susceptible'], 'g-', label='Susceptible')
infected_line, = ax_stats.plot(data['time'], data['infected'], 'r-', label='Infected')
recovered_line, = ax_stats.plot(data['time'], data['recovered'], 'b-', label='Recovered')
death_line, = ax_stats.plot(data['time'], data['deaths'], 'k-', label='Deaths')
ax_stats.legend()

# Initialize day text
day_text = ax_sim.text(0.05, 0.95, "Day: 0", transform=ax_sim.transAxes, 
                       fontsize=12, bbox=dict(facecolor='white', alpha=0.7))

# Function to update simulation for animation
def update(frame):
    x, y, status = sim.update()
    colors = [color_map[s] for s in status]
    
    # Update scatter plot data
    scatter.set_offsets(np.c_[x, y])
    scatter.set_color(colors)
    
    # Update day text
    day_text.set_text(f"Day: {sim.time}")
    
    # Update line plots
    data = sim.get_data()
    susceptible_line.set_data(data['time'], data['susceptible'])
    infected_line.set_data(data['time'], data['infected'])
    recovered_line.set_data(data['time'], data['recovered'])
    death_line.set_data(data['time'], data['deaths'])
    
    # Adjust x-axis limit as needed
    if sim.time > ax_stats.get_xlim()[1]:
        ax_stats.set_xlim(0, sim.time * 1.5)
    
    # Adjust y-axis limit if needed
    current_max = max(max(data['susceptible']), max(data['infected']), max(data['recovered']), max(data['deaths']))
    if current_max > ax_stats.get_ylim()[1]:
        ax_stats.set_ylim(0, current_max * 1.1)
    
    return scatter, susceptible_line, infected_line, recovered_line, death_line, day_text

# Create animation
ani = FuncAnimation(fig, update, frames=500, interval=50, blit=True)
plt.tight_layout()
plt.show()

# If you need to save the animation:
# ani.save('mpox_simulation.mp4', writer='ffmpeg', fps=20)