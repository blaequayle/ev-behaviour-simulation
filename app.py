import numpy as np
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from archetypes import DriverType
from simulator import EVBehaviourSimulator

st.set_page_config(layout="wide")
st.title("EV Driver Behaviour Simulation")
st.text(
    "This app uses a simulation to model the behaviour of different archetypes of EV drivers over a 24-hour period, and visualises their plug-in patterns and state of charge (SoC) profiles."
)
# CONFIGURATION & INSTANTIATION
population_size = st.number_input(
    min_value=1000,
    max_value=10000,
    label="What size population do you want to model?",
)
simulator = EVBehaviourSimulator(population_size=population_size)
population = simulator.create_population()

# INDIVIDUAL DRIVER
st.subheader(
    "Option 1: Choose a pattern of driver behaviour and view simulation result for randomly selected user in that group"
)
driver_type = st.selectbox(
    "The available archetypes are:",
    [i.value for i in DriverType],
)

single_user = population[
    population["driver_type"] == DriverType(driver_type)
].sample(n=1)
plugged_in_count_single_user = simulator.simulate_plug_in_count(single_user)
state_of_charge_single_user = simulator.simulate_state_of_charge(single_user)
st.text(
    f"The SoC at plug in is: {min(state_of_charge_single_user)[0] * 100:.2f}%"
)

labels = plugged_in_count_single_user.index.map(
    lambda x: f"{int(x.total_seconds() // 3600):02d}:{int((x.total_seconds() % 3600) // 60):02d}"
)

fig = make_subplots(specs=[[{"secondary_y": True}]])

fig.add_trace(
    go.Scatter(
        x=labels,
        y=state_of_charge_single_user.ravel().tolist(),
        name="SoC",
        line=dict(color="orange", width=3),
    ),
    secondary_y=True,
)

fig.add_trace(
    go.Scatter(
        x=labels,
        y=plugged_in_count_single_user.values,
        name="Plugged In",
        line=dict(color="green", width=3),
    ),
    secondary_y=False,
)
fig.update_xaxes(title_text="Time of day")
fig.update_yaxes(
    title_text="% EV plugged in", secondary_y=False, showgrid=False
)
fig.update_yaxes(
    title_text="State of Charge", secondary_y=True, showgrid=False
)
fig.update_layout(
    title="Periods when EV plugged in & state of charge over 24 hours"
)
st.plotly_chart(fig)
st.text("Note: 1 can be interpreted as plugged-in, 0 as not plugged-in")

# POPULATION LEVEL
st.subheader("Option 2: View simulation results at population level")

plug_in_count = simulator.simulate_plug_in_count(population)
state_of_charge = simulator.simulate_state_of_charge(population)
plug_in_count_percentage = (plug_in_count / population_size) * 100

labels = plug_in_count_percentage.index.map(
    lambda x: f"{int(x.total_seconds() // 3600):02d}:{int((x.total_seconds() % 3600) // 60):02d}"
)

p5 = np.percentile(state_of_charge, 5, axis=1)
p50 = np.percentile(state_of_charge, 50, axis=1)
p95 = np.percentile(state_of_charge, 95, axis=1)


fig = make_subplots(specs=[[{"secondary_y": True}]])

fig.add_trace(
    go.Bar(
        x=labels,
        y=plug_in_count_percentage.values,  # convert to percent
        name="Plugged In %",
        opacity=0.4,
        marker_color="grey",
    ),
    secondary_y=False,
)

fig.add_trace(
    go.Scatter(
        x=labels,
        y=p50,
        name="Median SoC",
        mode="lines",
    ),
    secondary_y=True,
)

fig.add_trace(
    go.Scatter(
        x=labels,
        y=p95,
        name="95th percentile",
        mode="lines",
        line=dict(dash="dash"),
    ),
    secondary_y=True,
)

fig.add_trace(
    go.Scatter(
        x=labels,
        y=p5,
        name="5th percentile",
        mode="lines",
        line=dict(dash="dash"),
    ),
    secondary_y=True,
)

# Fill the uncertainty band
fig.add_trace(
    go.Scatter(
        x=np.concatenate([labels, labels[::-1]]),
        y=np.concatenate([p95, p5[::-1]]),
        fill="toself",
        fillcolor="rgba(0, 150, 255, 0.15)",
        line=dict(color="rgba(255,255,255,0)"),
        hoverinfo="skip",
        name="5–95% band",
    ),
    secondary_y=True,
)

fig.update_layout(
    title="EV state of charge distribution vs % plugged in over 24 Hours",
    xaxis_title="Time of Day",
    template="plotly_white",
)

fig.update_yaxes(
    title_text="% EV plugged in", secondary_y=False, showgrid=False
)
fig.update_yaxes(
    title_text="State of Charge", secondary_y=True, showgrid=False
)

st.plotly_chart(fig)
