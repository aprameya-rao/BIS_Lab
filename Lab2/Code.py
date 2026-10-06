import numpy as np
import random

SIMULATION_TIME = 300
YELLOW_TIME = 3
MIN_GREEN = 20
MAX_GREEN = 60

SWARM_SIZE = 20
ITERATIONS = 3
W = 0.5
C1 = 1.5
C2 = 2.0

class Particle:
    def __init__(self):
        self.position = np.array([
            float(random.randint(MIN_GREEN, MAX_GREEN)),
            float(random.randint(MIN_GREEN, MAX_GREEN))
        ])
        self.velocity = np.array([
            random.uniform(-5, 5),
            random.uniform(-5, 5)
        ])
        self.best_position = np.copy(self.position)
        self.best_fitness = -float('inf')

def get_signal_state(time, ns_green, ew_green):
    cycle = ns_green + YELLOW_TIME + ew_green + YELLOW_TIME
    t = time % cycle
    if t < ns_green:
        return "NS_GREEN"
    elif t < ns_green + YELLOW_TIME:
        return "NS_YELLOW"
    elif t < ns_green + YELLOW_TIME + ew_green:
        return "EW_GREEN"
    else:
        return "EW_YELLOW"

def simulate(timing_plan, traffic):
    ns_green = timing_plan[0]
    ew_green = timing_plan[1]

    # Queues
    queues = {
        "North": [],
        "South": [],
        "East": [],
        "West": []
    }

    total_waiting_time = 0
    total_queue_time = 0
    stopped_vehicles = 0

    # Store arrival index for each road
    indexes = {
        "North": 0,
        "South": 0,
        "East": 0,
        "West": 0
    }

    for time in range(SIMULATION_TIME):
        for road in traffic:
            arrivals = traffic[road]
            while (
                indexes[road] < len(arrivals)
                and arrivals[indexes[road]] == time
            ):
                queues[road].append(time)
                indexes[road] += 1

        signal = get_signal_state(
            time,
            ns_green,
            ew_green
        )

        if signal == "NS_GREEN":
            active_roads = ["North", "South"]
        elif signal == "EW_GREEN":
            active_roads = ["East", "West"]
        else:
            active_roads = []

        for road in active_roads:
            if len(queues[road]) > 0:
                arrival_time = queues[road].pop(0)
                waiting_time = time - arrival_time
                total_waiting_time += waiting_time

        for road in queues:
            queue_length = len(queues[road])
            total_queue_time += queue_length
            if queue_length > 0:
                stopped_vehicles += queue_length

    cost = (
        total_waiting_time
        + 0.5 * total_queue_time
        + 0.1 * stopped_vehicles
    )

    efficiency_score = 1 / (1 + cost)

    return efficiency_score, {
        "waiting_time": total_waiting_time,
        "queue_time": total_queue_time,
        "stopped_vehicles": stopped_vehicles
    }

def pso_optimize(traffic):
    swarm = [Particle() for _ in range(SWARM_SIZE)]

    global_best_position = None
    global_best_fitness = -float('inf')

    history = []

    for it in range(ITERATIONS):
        for particle in swarm:
            chromosome_representation = [int(round(particle.position[0])), int(round(particle.position[1]))]
            fitness, _ = simulate(chromosome_representation, traffic)
            if fitness > particle.best_fitness:
                particle.best_fitness = fitness
                particle.best_position = np.copy(particle.position)
            if fitness > global_best_fitness:
                global_best_fitness = fitness
                global_best_position = np.copy(particle.position)
        for particle in swarm:
            r1, r2 = random.random(), random.random()
            cognitive = C1 * r1 * (particle.best_position - particle.position)
            social = C2 * r2 * (global_best_position - particle.position)

            particle.velocity = W * particle.velocity + cognitive + social
            particle.position = particle.position + particle.velocity
            particle.position[0] = max(MIN_GREEN, min(MAX_GREEN, particle.position[0]))
            particle.position[1] = max(MIN_GREEN, min(MAX_GREEN, particle.position[1]))

        history.append(global_best_fitness)
        best_rounded = [int(round(global_best_position[0])), int(round(global_best_position[1]))]
        print(f"Iteration {it+1:02d} | Global Best Position = {best_rounded} | Fitness = {global_best_fitness:.8f}")

    return [int(round(global_best_position[0])), int(round(global_best_position[1]))], history

def generate_traffic(rate):
    arrivals = []
    for t in range(SIMULATION_TIME):
        if random.random() < rate:
            arrivals.append(t)
    return arrivals

def generate_all_traffic():
    traffic = {
        "North": generate_traffic(0.30),
        "South": generate_traffic(0.25),
        "East": generate_traffic(0.15),
        "West": generate_traffic(0.20)
    }
    return traffic

traffic = generate_all_traffic()
# Run the PSO algorithm on the generated traffic
print("\nRunning Particle Swarm Optimization...\n")
best_pso_solution, pso_history = pso_optimize(traffic)

pso_fitness, pso_stats = simulate(best_pso_solution, traffic)

print("\n==============================")
print("OPTIMAL SIGNAL TIMING (PSO)")
print("==============================")
print("North-South Green:", best_pso_solution[0], "seconds")
print("East-West Green:", best_pso_solution[1], "seconds")
print("Yellow:", YELLOW_TIME, "seconds")
print("\nPerformance:")
print("Total waiting time:", pso_stats["waiting_time"])
print("Total queue time:", pso_stats["queue_time"])
print("Stopped vehicles:", pso_stats["stopped_vehicles"])
