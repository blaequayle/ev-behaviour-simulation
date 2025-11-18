### Axle Tech Test

#### Problem statement

Investigate how much flexibility is available from the large number of distributed assets that customers bring to Axle's platform

#### Requirements

- Build a simulator of EV driver behaviour

- Non-aggregated data for EV usage is hard to come by, so use data provided for 6 archetypes of EV driver behaviour

- It should be agent based i.e. allow for modelling of individual user behaviour

- It should be able to **surface population level observations** and capture **variation in the population of EV drivers**

- The simulator needs to be able to return when an **individual** is plugged in and state of charge of battery when plugged in

#### How did you design the system, bearing in mind its end use?

- An `EVBehaviourSimulator` has been built which simulates the behaviour of a population of drivers

- It uses the parameters for the 6 archetypes that were provided, and their relative proportion in the population, to create individual representations for each driver

- The tasks requires both individual and population level insights to be communicated and shared, so a Streamlit dashboard has been built to visualise the output from the simulation.

- It's available [here](https://ev-behaviour-simulation.streamlit.app/). The population size simulated can be configured via the app. It can return a visualisation of a simulation for an individual user within a specific archetype, or on a population level.


#### What assumptions have been taken?

- To add more variability in the State of Charge at plug-in value a normal distribution has been assumed to be a reasonable reflection of the real world, using the stated archetype value as the mean and a small standard deviation. There may be a better distribution to use for this.

- To be able to model a SoC profile for charging and discharging, rather than just a single point in time, a linear increase in SoC and a linear decrease in SoC was assumed. SoC at plug-out wa set to 80% as per the archetypes. The rate of change is likely to not be linear in reality, particularly for the charging portion where a vehicle may only be charging for a small portion of the time it is plugged in.

- The simulation has been applied to an arbitrary 24 hour period, rather than a specific time period. 30 minute intervals are used based on the settlement period being 30 minutes. It is assumed the archetypes adequately reflect EV driver behaviour, in reality studies have shown variation in behaviour between weekdays and weekends.


#### Which parts did you choose to spend time on?

- Investigating ways to build an agent based simulator, and building said simulator

- Visualisation of the output from the simulation - making it clear/easy to interpret output

- Having a distribution for SoC rather than just a single point, to be able to model the percentiles

- Set up project using uv to ensure that the build can be reproduced reliably 

#### What did you consider less important?

- There are python packages which allow for more advanced simulations, which I was not familiar with, so decided to go ahead with a simpler approach given the time available.

- Configured parameters for archetypes directly in a dictionary for ease. This does mean they are committed to the repo and potentially publically accessible. Updating them in the Streamlit app would also require a code change. It would be better to store these somewhere else and retrieve them as needed.

- For the "Always Plugged-in" group, for simplicity, they have been modelled as if their SoC is always 80% rather than having a SoC of 68%. This was done on the basis that they make up a small proportion of the population.

- Logging and full test coverage - important beyond a quick prototype

- Cleaning up code in streamlit app - could be pulled out into input and output functions for clarity

- Identifying more appropriate distribution to use for start SoC
