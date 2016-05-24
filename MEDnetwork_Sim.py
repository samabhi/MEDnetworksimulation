"""
Product Distribution

Covers:

- Resources: Resource
- Resources: Container
- Waiting for other processes

Scenario:
  A clinic has a limited number of medication units that share a common
  supply. Customers randomly arrive at the clinic, request medication and buy it.

  A clinic control process observes the clinic's medication level
  and calls a delivery truck for restocking if the clinics's level drops
  below a threshold.

"""
import itertools
import random

import simpy


random_seed = random.randint(10, 50)
clinic_med_supply = 100                   # medication units
THRESHOLD = 10                            # Threshold for calling the delivery truck (in %)
amount_customer = [1, 10]                 # Min/max levels of amount a customer can purchase
medication_buying_speed = 1               # medication buy rate / second
time_to_deliver = [100, 200]              # Seconds it takes the delivery truck to arrive
time_to_deliver_reroute =  [200, 400]
time_to_deliver_traffic = [400, 600]
customer_arrival_times = [10, 300]        # Create a customer every [min, max] seconds
simulation_time = 1000                    # Simulation time in seconds


def customer(name, env, clinic, medication):
    """A customer arrives at the clinic for medication.

    It requests an amount of medication. If the clinic's stock is
    depleted, the customer has to wait for the delivery truck to arrive.

    """
    print('%s arriving at %s at %.1f' % (name, medication.name, env.now))
    with clinic.request() as req:
        start = env.now
        # Request medication
        yield req

        # Get the required amount of medication
        liters_required = random.randint(*amount_customer)
        yield medication.get(liters_required)

        # The "actual" buying process takes some time
        yield env.timeout(liters_required / medication_buying_speed)

        print('%s got medication in %.1f seconds.' % (name, env.now - start))


def clinic_control(env, medication):
    """Periodically check the level of the *supply* and call the delivery
    truck if the level falls below a threshold."""
    while True:
        if medication.level < THRESHOLD or medication.level == 0:
            # We need to call the tank truck now!
            print('Calling delivery truck at %d' % env.now)
            # Wait for the tank truck to arrive and refuel the station
            yield env.process(delivery_truck(env, medication))

        yield env.timeout(500)  # Check every 500 seconds


def delivery_truck(env, medication):
    """Arrives at the clinic after a certain delay and restocks it."""
    road_conditions = random.randint(1,3)
    if road_conditions == 1:
        yield env.timeout(random.randint(*time_to_deliver))
    elif road_conditions == 2:
        print ('Delivery truck stuck in a lot of traffic, delivery will take time')
        yield env.timeout(random.randint(*time_to_deliver_traffic))
    elif road_conditions == 3:
        print ('Road conditions not optimal, delivery will take time')
        yield env.timeout(random.randint(*time_to_deliver_reroute))
    print('Delivery truck arriving at time %d' % env.now)
    amount = medication.capacity - medication.level
    print('Delivery truck restocking %.1f boxes of medication.' % amount)
    yield medication.put(amount)


def customer_generator(env, clinic, medication):
    """Generate new customers that arrive at the clinic."""
    for i in itertools.count():
        yield env.timeout(random.randint(*customer_arrival_times))
        env.process(customer('Customer %d' % i, env, clinic, medication))


# Setup and start the simulation
print('Product Distribution Network')
random.seed(random_seed)

# Create environment and start processes
env0 = simpy.Environment()
clinic = simpy.Resource(env0, 1)


clinic0 = simpy.Container(env0, clinic_med_supply, init=clinic_med_supply)
clinic0.name = "clinic 0"
env0.process(clinic_control(env0, clinic0))

clinic1 = simpy.Container(env0, clinic_med_supply, init=clinic_med_supply)
clinic1.name = "clinic 1"
env0.process(clinic_control(env0, clinic1))

clinic2 = simpy.Container(env0, clinic_med_supply, init=clinic_med_supply)
clinic2.name = "clinic 2"
env0.process(clinic_control(env0, clinic2))

clinic3 = simpy.Container(env0, clinic_med_supply, init=clinic_med_supply)
clinic3.name = "clinic 3"
env0.process(clinic_control(env0, clinic3))

clinic4 = simpy.Container(env0, clinic_med_supply, init=clinic_med_supply)
clinic4.name = "clinic 4"
env0.process(clinic_control(env0, clinic4))

env0.process(customer_generator(env0, clinic, clinic0))
env0.process(customer_generator(env0, clinic, clinic1))
env0.process(customer_generator(env0, clinic, clinic2))
env0.process(customer_generator(env0, clinic, clinic3))
env0.process(customer_generator(env0, clinic, clinic4))


# Execute!
env0.run(until=simulation_time)
