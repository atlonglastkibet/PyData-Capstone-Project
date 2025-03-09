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
                 population_size=1000, 
                 initial_infected=57,
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
        if self.time >= 365:  # Stop simulation after 365 days
            return None
        
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
        positions = {'susceptible': ([], []), 'infected': ([], []), 'recovered': ([], []), 'dead': ([], [])}
        for person in self.population:
            positions[person.status][0].append(person.x)
            positions[person.status][1].append(person.y)
        return positions
    
    def get_data(self):
        return self.data

# Create interactive simulation visualization
plt.style.use('default')  # Reset style to default
fig = plt.figure(figsize=(8, 8))
ax_sim = plt.subplot()  # Single subplot for spatial visualization

# Set up axes
ax_sim.set_title('Mpox Transmission Simulation (May 2022 - May 2023)', fontsize=14)
ax_sim.set_xlim(0, 1)
ax_sim.set_ylim(0, 1)
ax_sim.set_aspect('equal')
ax_sim.axis('off')  # Remove axes
ax_sim.set_facecolor('white')  # Set background to white

# Initialize simulation
initial_cases = 10  # Adjust based on reported cases in May 2022
sim = MpoxSimulation(
    population_size=200, 
    initial_infected=initial_cases, 
    transmission_radius=0.03, 
    transmission_rate=0.3, 
    recovery_time=14, 
    cfr=0.01  # Example CFR of 1%
)

positions = sim.get_positions_and_statuses()

# Initialize scatter plots for each category
color_map = {'susceptible': 'green', 'infected': 'red', 'recovered': 'blue', 'dead': 'black'}
scatters = {}
for status, color in color_map.items():
    scatters[status] = ax_sim.scatter([], [], c=color, alpha=0.8, label=status.capitalize())

# Add legend
ax_sim.legend(loc='upper right', fontsize=10)

# Initialize day text
day_text = ax_sim.text(0.05, 0.95, "Day: 0", transform=ax_sim.transAxes, 
                       fontsize=12, bbox=dict(facecolor='white', edgecolor='black', alpha=0.7))

# Function to update simulation for animation
def update(frame):
    if sim.time >= 365:  # Stop updating after 365 days
        return list(scatters.values()) + [day_text]
    
    positions = sim.update()
    
    # Update scatter plot data for each category
    for status, scatter in scatters.items():
        scatter.set_offsets(np.c_[positions[status][0], positions[status][1]])
    
    # Update day text
    day_text.set_text(f"Day: {sim.time}")
    
    return list(scatters.values()) + [day_text]

# Create animation with 365 frames
ani = FuncAnimation(fig, update, frames=365, interval=50, blit=True)
plt.tight_layout()
plt.show()

# If you need to save the animation:
# ani.save('mpox_simulation.mp4', writer='ffmpeg', fps=20)
