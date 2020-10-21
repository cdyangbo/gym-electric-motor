import os
import sys
import time
from examples.agents.simple_controllers import Controller
sys.path.append(os.path.abspath(os.path.join('..')))
import gym_electric_motor as gem
from gym_electric_motor import reference_generators as rg
from gym_electric_motor.visualization import MotorDashboard


"""Run this file from within the 'examples' folder:
>> cd examples
>> python pi_series_omega_control.py
Description:
        Environment to control a Continuously controlled DC Series Motor.

        Controlled Quantity: 'omega'

        Limitations: Physical limitation of the  motor Current

        Converter : OneQuadrantConverter from converters.py
"""

if __name__ == '__main__':
    """
           Continuous mode: The action is the average (normalized) voltage per time step which is assumed to be transferred to a PWM 
                            converter to generate the switching sequence.

           Discrete mode: The action is the switching state of the power converter i.e., a quantity from a discrete set of
                          switching states which can be generated by the converter.   


    """

    env = gem.make('DcSeriesCont-v1',  # replace with 'DcSeriesDisc-v1' for discrete controllers
                   state_filter=['omega', 'i'],
                   # Pass an instance
                   visualization=MotorDashboard(plots=['i', 'omega']),
                   # Take standard class and pass parameters (Load)
                   motor_parameter=dict(r_a=15e-3, r_e=15e-3, l_a=100e-3, l_e=100e-3),
                   load_parameter=dict(a=0, b=.1, c=.1, j_load=0.04),
                   # Pass a string (with extra parameters)
                   ode_solver='scipy.solve_ivp', solver_kwargs={},
                   # Pass a Class with extra parameters
                   reference_generator=rg.WienerProcessReferenceGenerator())

    # Assign a PI-controller to the speed control problem
    controller = Controller.make('pi_controller',env)
    state, reference = env.reset()

    # get the system time to measure program duration
    start = time.time()

    cum_rew = 0
    for i in range(100000):

        # the render command updates the dashboard
        env.render()

        # the controller accepts state and reference to calculate a new action
        action = controller.control(state, reference)

        # the drive environment accepts the action and simulates until the next time step
        (state, reference), reward, done, _ = env.step(action)

        if done:
            env.reset()
            controller.reset()
        cum_rew += reward

    print(cum_rew)
