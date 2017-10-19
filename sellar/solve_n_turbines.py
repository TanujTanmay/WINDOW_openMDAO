from openmdao.api import Problem, Group, ExplicitComponent, view_model, IndepVarComp
from numpy import sqrt
import numpy as np

u_far = 8.5


def ct(v):
    if v < 4.0:
        return np.array([0.1])
    elif v <= 25.0:
        return 7.3139922126945e-7 * v ** 6.0 - 6.68905596915255e-5 * v ** 5.0 + 2.3937885e-3 * v ** 4.0 - 0.0420283143 * v ** 3.0 + 0.3716111285 * v ** 2.0 - 1.5686969749 * v + 3.2991094727
    else:
        return np.array([0.1])


def wake_deficit(x, Ct, k=0.04, r0=40.0):
    if x > 0.0:
        return (1.0 - sqrt(1.0 - Ct)) / (1.0 + (k * x) / r0) ** 2.0
    else:
        return 0.0


def speed(deficit):
    return u_far * (1.0 - deficit)


def distance(t1, t2):
    if t2[0] < t1[0]:
        return sqrt((t1[1] - t2[1]) ** 2.0 + (t1[2] - t2[2] ** 2.0))
    else:
        return 0.0


n_turbines = 3


class ThrustCoefficient(ExplicitComponent):

    def __init__(self, number):
        super(ThrustCoefficient, self).__init__()
        self.number = number

    def setup(self):

        for n in range(n_turbines):
            if n != self.number:
                self.add_input('U{}'.format(n), val=u_far)

        self.add_output('ct', shape=n_turbines - 1, val=0.79)

        # Finite difference all partials.
        # self.declare_partials('*', '*', method='fd')

    def compute(self, inputs, outputs):
        c_t = np.array([])
        for n in range(n_turbines):
            if n != self.number:
                c_t = np.append(c_t, [ct(inputs['U{}'.format(n)])])
        outputs['ct'] = c_t


class DistanceComponent(ExplicitComponent):
    def __init__(self, number):
        super(DistanceComponent, self).__init__()
        self.number = number

    def setup(self):
        self.add_input('layout', shape=(n_turbines, 3))
        self.add_output('dist', shape=n_turbines - 1, val=1.0)

        # Finite difference all partials.
        # self.declare_partials('*', '*', method='fd')

    def compute(self, inputs, outputs):
        layout = inputs['layout']
        d = np.array([])
        for n in range(len(layout)):
            if n != self.number:
                d = np.append(d, [distance(layout[self.number], layout[n])])
        outputs['dist'] = d


class WakeDeficit(ExplicitComponent):
    def setup(self):
        self.add_input('dist', shape=n_turbines - 1, val=560.0)
        self.add_input('ct', shape=n_turbines - 1, val=0.79)
        self.add_output('dU', shape=n_turbines - 1, val=0.3)

    def compute(self, inputs, outputs):
        deficits = np.array([])
        d = inputs['dist']
        c_t = inputs['ct']
        for ind in range(len(d)):
            if d[ind] > 0.0:
                deficits = np.append(deficits, [wake_deficit(d[ind], c_t[ind])])
            else:
                deficits = np.append(deficits, [0])
        outputs['dU'] = deficits


class SumComponent(ExplicitComponent):
    def setup(self):
        self.add_input('all_deficits', shape=n_turbines - 1)
        self.add_output('sos')

    def compute(self, inputs, outputs):
        defs = inputs['all_deficits']
        summation = 0.0
        for item in defs:
            summation += item ** 2.0
        outputs['sos'] = summation


class SqrtRSS(ExplicitComponent):

    def setup(self):
        self.add_input('summation')
        self.add_output('sqrt')

    def compute(self, inputs, outputs):
        outputs['sqrt'] = sqrt(inputs['summation'])


class SpeedDeficits(ExplicitComponent):

    def setup(self):
        self.add_input('dU', val=0.5)
        self.add_output('U', val=8.0)

    def compute(self, inputs, outputs):
        dU = inputs['dU']

        outputs['U'] = u_far * (1.0 - dU)


class WakeModel(Group):

    def setup(self):
        indep2 = self.add_subsystem('indep2', IndepVarComp())
        indep2.add_output('layout', np.array([[0, 0.0, 0.0], [1, 560.0, 0.0], [2, 1120.0, 0.0]]))
        for n in range(n_turbines):
            self.add_subsystem('ct{}'.format(n), ThrustCoefficient(n))
            self.add_subsystem('dist{}'.format(n), DistanceComponent(n))
            self.add_subsystem('deficits{}'.format(n), WakeDeficit())
            merge = self.add_subsystem('merge{}'.format(n), Group())
            merge.add_subsystem('sum'.format(n), SumComponent(), promotes_inputs=['all_deficits'])
            merge.add_subsystem('sqrt'.format(n), SqrtRSS(), promotes_outputs=['sqrt'])
            # self.add_subsystem('sum{}'.format(n), SumComponent())
            # self.add_subsystem('sqrt{}'.format(n), SqrtRSS())
            self.add_subsystem('speed{}'.format(n), SpeedDeficits())
            merge.connect('sum.sos'.format(n), 'sqrt.summation'.format(n))
            self.connect('ct{}.ct'.format(n), 'deficits{}.ct'.format(n))
            self.connect('indep2.layout', 'dist{}.layout'.format(n))
            self.connect('dist{}.dist'.format(n), 'deficits{}.dist'.format(n))
            self.connect('deficits{}.dU'.format(n), 'merge{}.all_deficits'.format(n))
            self.connect('merge{}.sqrt'.format(n), 'speed{}.dU'.format(n), )
            for m in range(n_turbines):
                if m != n:
                    self.connect('speed{}.U'.format(n), 'ct{}.U{}'.format(m, n))


if __name__ == '__main__':
    from openmdao.api import LinearBlockGS, DirectSolver, ScipyIterativeSolver, LinearBlockJac, LinearRunOnce
    prob = Problem()

    prob.model = WakeModel()
    NS = prob.model.linear_solver = LinearRunOnce()
    NS.options['iprint'] = 1
    prob.setup()
    # view_model(prob)

    prob.run_model()
    for n in range(n_turbines):
        print(prob['speed{}.U'.format(n)])