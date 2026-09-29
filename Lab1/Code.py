import random

SIMULATION_TIME = 300
YELLOW_TIME = 3

MIN_GREEN = 20
MAX_GREEN = 60

POPULATION_SIZE = 30
GENERATIONS = 50

MUTATION_RATE = 0.1
TOURNAMENT_SIZE = 3

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

def simulate(chromosome, traffic):

    ns_green = chromosome[0]
    ew_green = chromosome[1]

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

    fitness = 1 / (1 + cost)

    return fitness, {
        "waiting_time": total_waiting_time,
        "queue_time": total_queue_time,
        "stopped_vehicles": stopped_vehicles
    }


def create_individual():

    ns_green = random.randint(
        MIN_GREEN,
        MAX_GREEN
    )

    ew_green = random.randint(
        MIN_GREEN,
        MAX_GREEN
    )

    return [ns_green, ew_green]

def create_population():

    return [
        create_individual()
        for _ in range(POPULATION_SIZE)
    ]

def selection(population, traffic):

    tournament = random.sample(
        population,
        TOURNAMENT_SIZE
    )

    tournament.sort(
        key=lambda x: simulate(x, traffic)[0],
        reverse=True
    )

    return tournament[0]

def crossover(parent1, parent2):

    child = [
        parent1[0],
        parent2[1]
    ]

    return child


def mutate(individual):

    if random.random() < MUTATION_RATE:

        gene = random.randint(0, 1)

        individual[gene] += random.randint(-5, 5)

        individual[gene] = max(
            MIN_GREEN,
            min(MAX_GREEN, individual[gene])
        )

    return individual

def genetic_algorithm(traffic):

    population = create_population()

    best_solution = None
    best_fitness = -float("inf")

    history = []

    for generation in range(GENERATIONS):

        evaluated = []

        for individual in population:

            fitness, stats = simulate(
                individual,
                traffic
            )

            evaluated.append(
                (fitness, individual, stats)
            )

        evaluated.sort(
            key=lambda x: x[0],
            reverse=True
        )

        current_best = evaluated[0]

        if current_best[0] > best_fitness:

            best_fitness = current_best[0]

            best_solution = current_best[1].copy()

        history.append(best_fitness)

        print(
            f"Generation {generation + 1:02d} | "
            f"Best = {current_best[1]} | "
            f"Fitness = {current_best[0]:.8f}"
        )

        new_population = []

        # Elitism
        new_population.append(
            evaluated[0][1].copy()
        )

        while len(new_population) < POPULATION_SIZE:

            parent1 = selection(
                population,
                traffic
            )

            parent2 = selection(
                population,
                traffic
            )

            child = crossover(
                parent1,
                parent2
            )

            child = mutate(child)

            new_population.append(child)

        population = new_population

    return best_solution, history

if __name__ == "__main__":

    random.seed(42)

    # Generate traffic
    traffic = generate_all_traffic()

    print("\nTraffic generated:")
    for road in traffic:
        print(
            road,
            "vehicles =",
            len(traffic[road])
        )

    print("\nRunning Genetic Algorithm...\n")

    best_solution, history = genetic_algorithm(
        traffic
    )
    fitness, stats = simulate(
        best_solution,
        traffic
    )

    print("\n==============================")
    print("OPTIMAL SIGNAL TIMING")
    print("==============================")

    print(
        "North-South Green:",
        best_solution[0],
        "seconds"
    )

    print(
        "East-West Green:",
        best_solution[1],
        "seconds"
    )

    print(
        "Yellow:",
        YELLOW_TIME,
        "seconds"
    )

    print("\nPerformance:")

    print(
        "Total waiting time:",
        stats["waiting_time"]
    )

    print(
        "Total queue time:",
        stats["queue_time"]
    )

    print(
        "Stopped vehicles:",
        stats["stopped_vehicles"]
    )