from openmdao.api import ExplicitComponent
from input_params import max_n_turbines, max_n_substations, max_n_turbines_p_branch, max_n_branches
import numpy as np


class AbstractElectricDesign(ExplicitComponent):

    def setup(self):
        self.add_input('layout', shape=(max_n_turbines, 3))
        self.add_input('n_turbines_p_cable_type', shape=3)
        self.add_input('substation_coords', shape=(max_n_substations, 2))
        self.add_input('n_substations', val=0)
        self.add_input('n_turbines', val=0)

        self.add_output('topology', shape=(max_n_substations, max_n_branches, max_n_turbines_p_branch, 2))
        self.add_output('cost_p_cable_type', shape=3)
        self.add_output('length_p_cable_type', shape=3)

    def compute(self, inputs, outputs):
        n_turbines = int(inputs['n_turbines'])
        layout = [[int(coord[0]), coord[1], coord[2]] for coord in inputs['layout'][:n_turbines]]
        n_substations = int(inputs['n_substations'])
        n_turbines_p_cable_type = [int(num) for num in inputs['n_turbines_p_cable_type']]
        substation_coords = inputs['substation_coords'][:n_substations]

        cost, topology_dict, cable_lengths = self.topology_design_model(layout, substation_coords, n_turbines_p_cable_type)

        topology_list = []
        for n in range(1, len(topology_dict) + 1):
            topology_list.append(topology_dict[n])
        # dif_sub = n_substations - len(topology)

        from itertools import izip_longest

        def find_shape(seq):
            try:
                len_ = len(seq)
            except TypeError:
                return ()
            shapes = [find_shape(subseq) for subseq in seq]
            return (len_,) + tuple(max(sizes) for sizes in izip_longest(*shapes,
                                                                        fillvalue=1))

        def fill_array(arr, seq):
            if arr.ndim == 1:
                try:
                    len_ = len(seq)
                except TypeError:
                    len_ = 0
                arr[:len_] = seq
                arr[len_:] = np.nan
            else:
                for subarr, subseq in izip_longest(arr, seq, fillvalue=()):
                    fill_array(subarr, subseq)
        # for sub in range(n_substations):
        #     dif_bran = max_n_branches - len(topology[sub])
        #     for bran in range(max_n_branches):
        #         for tur in range(max_n_turbines_p_branch):

        # topology = np.array(topology_list)
        topology = np.empty((max_n_substations, max_n_branches, max_n_turbines_p_branch, 2))
        fill_array(topology, topology_list)
        # print topology
        # topology = topology.reshape(1, 3, 3, 2)
        outputs['cost_p_cable_type'] = cost
        outputs['topology'] = topology
        outputs['length_p_cable_type'] = cable_lengths

    def topology_design_model(self, layout, substation_coords, n_turbines_p_cable_type, n_substations):
        # Define your own model in a subclass of AbstractCollectionDesign and redefining this method.
        pass
