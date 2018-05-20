# IS590PR - Section B (Friday) - Team 1
# Team Members: Aayushi Vora, Harsh Mangal, Pan Zhang, Rujuta Dawkhar, Xinyu Tian
"""
>>> Disney = Navigation('edges.csv', 'nodes.csv', 'CarSpin', 'DisneyGallery', True)
>>> Disney.calculate_shortest_path()
['CarSpin', 'Toonstreet3_Toonstreet1', 'Toonstreet3_AdventureLand8', 'DisneyGallery']
>>> Disney.turn_by_turn_instruction()
Start route from CarSpin to DisneyGallery.
Walk along Toonstreet1 road for 0.1 miles in South direction to Toonstreet3_Toonstreet1.
Walk along Toonstreet3 road for 0.2 miles in East direction to Toonstreet3_AdventureLand8.
Walk along AdventureLand8 road for 0.1 miles in South direction to DisneyGallery.
You have arrived at DisneyGallery.
The total distance is 0.4 miles.

# automated test that verifies that it is possible to navigate from every attraction in your facility to every other facility
>>> Disney.connections()
True
"""
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import itertools
from networkx.algorithms.connectivity import (build_auxiliary_edge_connectivity)
from networkx.algorithms.flow import build_residual_network
from networkx.algorithms.connectivity import local_edge_connectivity


class Navigation(object):
    """
    >>> Disney = Navigation('edges.csv', 'nodes.csv', 'Swiz', 'Tiki', True)
    >>> Disney.calculate_shortest_path()
    ['Swiz', 'Toonstreet3_AdventureLand7', 'Toonstreet3_AdventureLand6', 'AdventureLand6_Waltstreet', 'Waltstreet_Waltstreet7', 'Tiki']
    >>> Disney.turn_by_turn_instruction()
    Start route from Swiz to Tiki.
    Walk along AdventureLand7 road for 0.2 miles in North direction to Toonstreet3_AdventureLand7.
    Walk along Toonstreet3 road for 0.5 miles in West direction to Toonstreet3_AdventureLand6.
    Walk along AdventureLand6 road for 0.3 miles in North direction to AdventureLand6_Waltstreet.
    Walk along Waltstreet road for 0.5 miles in East direction to Waltstreet_Waltstreet7.
    Walk along Waltstreet7 road for 0.2 miles in North direction to Tiki.
    You have arrived at Tiki.
    The total distance is 1.7 miles.

    #checking unidirectional and handicapped path simultaneously
    >>> Disney = Navigation('edges.csv', 'nodes.csv', 'PennyArcade', 'JungleCruise', True)
    >>> Disney.calculate_shortest_path()
    ['PennyArcade', 'Waltstreet_Waltstreet1', 'Waltstreet_Waltstreet7', 'AdventureLand6_Waltstreet', 'Toonstreet3_AdventureLand6', 'Toonstreet3_AdventureLand5', 'JungleCruise']
    >>> Disney.turn_by_turn_instruction()
    Start route from PennyArcade to JungleCruise.
    Walk along Waltstreet1 road for 0.3 miles in North direction to Waltstreet_Waltstreet1.
    Walk along Waltstreet road for 0.3 miles in West direction to Waltstreet_Waltstreet7.
    Walk along Waltstreet road for 0.5 miles in West direction to AdventureLand6_Waltstreet.
    Walk along AdventureLand6 road for 0.3 miles in South direction to Toonstreet3_AdventureLand6.
    Walk along Toonstreet3 road for 0.3 miles in West direction to Toonstreet3_AdventureLand5.
    Walk along AdventureLand5 road for 0.2 miles in South direction to JungleCruise.
    You have arrived at JungleCruise.
    The total distance is 1.9 miles.

    #Non handicap and unidirectional simultaneously
    >>> Disney = Navigation('edges.csv', 'nodes.csv', 'DisneyGallery', 'PennyArcade', False)
    >>> Disney.calculate_shortest_path()
    ['DisneyGallery', 'Toonstreet3_AdventureLand8', 'Toonstreet3_AdventureLand4', 'Toonstreet3_AdventureLand5', 'AdventureLand6_Waltstreet', 'Waltstreet_Waltstreet7', 'Waltstreet_Waltstreet4', 'PennyArcade']
    >>> Disney.turn_by_turn_instruction()
    Start route from DisneyGallery to PennyArcade.
    Walk along AdventureLand8 road for 0.1 miles in North direction to Toonstreet3_AdventureLand8.
    Walk along Toonstreet3 road for 0.3 miles in East direction to Toonstreet3_AdventureLand4.
    Walk along Toonstreet3 road for 0.5 miles in East direction to Toonstreet3_AdventureLand5.
    Walk along AdventureLand9 road for 0.2 miles in Northeast direction to AdventureLand6_Waltstreet.
    Walk along Waltstreet road for 0.5 miles in East direction to Waltstreet_Waltstreet7.
    Walk along Waltstreet road for 0.5 miles in East direction to Waltstreet_Waltstreet4.
    Walk along Waltstreet4 road for 1.0 miles in South direction to PennyArcade.
    You have arrived at PennyArcade.
    The total distance is 3.1 miles.
    """


    def __init__(self, edge_filepath, node_filepath, start=None, next=None, handicap_flag=False):
        # set the default value of start (source) and next (target) as None to build the network initially
        self.__edge_filepath = edge_filepath
        self.__node_filepath = node_filepath
        self.__start = start
        self.__next = next
        self.__handicap_flag = handicap_flag
        self.__DiGraph = Navigation.read_from_csv_get_attribute(edge_filepath, node_filepath, handicap_flag)
        self.__path = Navigation.calculate_shortest_path(self)

    @staticmethod
    def simple_slip(direction: str)->str:
        # Adapted from IS590PR Examples, by J. Weible
        """Given a 1-digit compass direction 'E', 'W', 'N', or 'S', return the opposite.
        Raise exception with none of those.
        :param direction: a string containing 'E', 'W', 'N', or 'S'
        :return: a string containing 'E', 'W', 'N', or 'S'
        >>> Navigation.simple_slip('E')
        'W'
        >>> Navigation.simple_slip('S')
        'N'
        >>> Navigation.simple_slip('SE') # test an unsupported value
        Traceback (most recent call last):
        ...
        ValueError: Invalid or unsupported direction SE given.
        """
        if direction == 'E':
            return 'W'
        elif direction == 'W':
            return 'E'
        elif direction == 'N':
            return 'S'
        elif direction == 'S':
            return 'N'
        else:
            raise ValueError('Invalid or unsupported direction {} given.'.format(direction))

    @staticmethod
    def flip_direction(direction: str) -> str:
        """
        Support the flipping of 2-digit compass directions based on simple_flip().
        Raise exception for any other strings.
        :param direction: a string 'SE', 'SW', 'NE', or 'NW'
        :return: a string containing 'SE', 'SW', 'NE', or 'NW'
        >>> Navigation.flip_direction('SE')
        'NW'
        >>> Navigation.flip_direction('NE')
        'SW'
        """
        if len(direction) == 1:
            return Navigation.simple_slip(direction)
        elif len(direction) == 2:
            return Navigation.simple_slip(direction[0])+Navigation.simple_slip(direction[1])
        else:
            raise ValueError('Invalid or unsupported direction {} given.'.format(direction))

    @staticmethod
    def add_attribute_to_edge(Graph, DiGraph, a, b, attributes):
        """
        Given a Graph imported from a csv file, convert it to a DiGraph according to bi_dir_indicator.
        For two-way connections, convert it to a bi-direction edge, otherwise to a uni-direction edge.
        Raise attribute exception if the column 'bi_dir_indicator' doesn't exist.
        :param Graph: Graph object imported from a csv file
        :param DiGraph: Empty Digraph object to overwrite
        :param a: A node of an edge
        :param b: Another node of the edge
        :param attributes: Name of attributes attached to an edge, string
        :return: The modified DiGraph
        """
        if Graph[a][b]['bi_dir_indicator'] == 1:    # two-way
            DiGraph.add_edge(a, b)
            DiGraph.add_edge(b, a)                  # add the opposite one
            for attr in attributes[2:]:
                DiGraph[a][b][attr] = Graph[a][b][attr]
                DiGraph[b][a][attr] = Graph[a][b][attr] # add the corresponding attributes
                # flip the direction for the opposite one
                DiGraph[b][a]['direction'] = Navigation.flip_direction(Graph[a][b]['direction'])
        elif Graph[a][b]['bi_dir_indicator'] == 0:    # one-way
            DiGraph.add_edge(b, a)                    # TODO - something weird, but working
            for attr in attributes[2:]:
                DiGraph[b][a][attr] = Graph[a][b][attr]
        else:                                         # if the column 'bi_dir_indicator' is missing
            raise AttributeError
        return DiGraph

    @staticmethod
    def read_from_csv_get_attribute(edge_path: str, node_path: str, handicap_mode_flag: bool) -> nx.DiGraph:
        """
        Given an edge csv file consisting of nodes and their attributes, and a node csv file with edges and attributes,
        return a DiGraph to use in NetworkX.
        :param edge_path: the file path of the csv file including edges and their attributes
        :param node_path: the file path of the csv file including nodes and their attributes
        :param handicap_mode_flag: switch between the handicapped accessible mode (True) and the normal mode (False)
        :return: a DiGraph object imported
        """
        edge_df = pd.read_csv(edge_path)                        # read the csv file into a DataFrame
        attributes = edge_df.columns.get_values().tolist()      # retrieve names of attributes by the column names
        G = nx.from_pandas_edgelist(edge_df, 'from_node', 'to_node', edge_attr = attributes)    # TODO - something weird, but working, error occurs in this step possibly
        DG = nx.DiGraph()                                       # create an empty DiGraph object
        # add attributes for edges
        for (a, b) in G.edges():                                # go through all edges in the Graph imported
            DG = Navigation.add_attribute_to_edge(G, DG, a, b, attributes)
            if handicap_mode_flag == True:
                if G[a][b][
                    'handicap_indicator'] == 0:  # 0 = route normal people ONLY, 1 = route available for both normal AND handicapped
                    handicap_distance = DG[a][b]['distance'] + 10000
                    dict1 = {(a, b): {'distance': handicap_distance}, (b, a): {'distance': handicap_distance}}
                    nx.set_edge_attributes(DG, dict1)
            # add attributes for attractions

        node_df = pd.read_csv(node_path).set_index('Attractions')
        node_dict = node_df.to_dict('index')  # convert from DataFrame to dict
        nx.set_node_attributes(DG, node_dict)
        return DG

    def connections(self):
        # References taken from NetwrokX documentation
        def check_connections(self):
            """
            :return: a True/ False value depending on connections
            """
        count = 0
        DG = Navigation.read_from_csv_get_attribute('edges.csv','nodes.csv', handicap_mode_flag=bool)
        H = build_auxiliary_edge_connectivity(DG)
        # And the function for building the residual network from the
        # flow package
        # Note that the auxiliary digraph has an edge attribute named capacity
        R = build_residual_network(H, 'capacity')
        result = dict.fromkeys(DG, dict())
        # Reuse the auxiliary digraph and the residual network by passing them
        # as parameters
        #print(local_edge_connectivity(DG, 'Indiana1', 'DisneyLandMonoRail'))
        for u, v in itertools.combinations(DG, 2):
            k = local_edge_connectivity(DG, u, v, auxiliary=H, residual=R)
            result[u][v] = k
            # print(u,v)
            # print(result[u][v])
            if result[u][v] == 0:
                count = 1
                #print(u,v)
        if count == 1:
            return False
        else:
            return True

    @staticmethod
    def direction_narrative(d1):
        """
        Convert the direction codes to readable words.
        If the direction codes are not compass directions, raise a value error.
        :param d1: one or two digit direction codes, string
        :return: words of directions, string
        """
        direction = {'N': 'North', 'E': 'East', 'S': 'South', 'W': 'West',
                     'NW': 'Northwest', 'NE': 'Northeast', 'SW':  'Southwest', 'SE':'Southeast'}
        if d1 in direction:
            return direction[d1]
        else:
            raise ValueError

    def get_all_attractions(self):
        """
        Retrieve all attractions from the DiGraph object.
        :return: A list of the name of all attractions.
        """
        attractions_list = pd.read_csv(self.__node_filepath)['Attractions'].tolist()
        # get the list of attractions from the csv file directly
        attractions = [node for node in self.__DiGraph.nodes() if node in attractions_list]
        # filter the nodes of attractions from all nodes, or throw away the junctions
        return attractions

    def draw_graph(self):
        """
        Draw the network graph with the shortest path highlighted.
        """
        plt.figure(figsize=(10, 10), dpi=200)               # set the size of figure
        pos = nx.kamada_kawai_layout(self.__DiGraph)        # use a layout function to build a dict of positions
        # the positions of nodes are not accurate to the fact and the visualization is just an abstract illustration
        attractions = Navigation.get_all_attractions(self)  # retrieve the list of all attractions
        labels = {node:node for node in attractions}        # create the dict of labels of all attractions
        nx.draw_networkx(self.__DiGraph, pos=pos, with_labels=True, node_color='b', node_size=50, labels=labels, font_size=14)
        path_edges = [(self.__path[n], self.__path[n+1]) for n in range(len(self.__path)-1)]    # build the edges list from the lists of all attractions
        nx.draw_networkx_edges(self.__DiGraph, pos=pos, edgelist=path_edges, edge_color='r', width=8, arrows=False) # specify the style of the shortest path
        plt.xticks([])                                      # remove ticks
        plt.yticks([])
        return plt

    def list_all_attractions(self):
        """
        List all attractions with their attributes.
        """
        attractions = Navigation.get_all_attractions(self)  # retrieve the list of all attractions
        # define the attributes 'HandicapAccessible', 'AverageWaitingTime', 'MinWeight' and 'MinHeight' to list
        handicap_accessible = nx.get_node_attributes(self.__DiGraph, 'HandicapAccessible')
        time = nx.get_node_attributes(self.__DiGraph, 'AverageWaitingTime')
        min_weight = nx.get_node_attributes(self.__DiGraph, 'MinWeight')
        min_height = nx.get_node_attributes(self.__DiGraph, 'MinHeight')
        # sort the list alphabetically
        attractions.sort()
        # format the output with proper spaces added
        print('Attraction_Name      Handicap_Accessible  Average_Waiting_Time(min)  MinWeight(lb)  MinHeight(inch)')
        for node in attractions:
            print('{:<20} {:<20} {:<25} {:<13} {:<15}'.\
                  format(node, handicap_accessible[node], time[node], min_height[node], min_weight[node]))

    def calculate_shortest_path(self):
        """
        Given the source and target, return the shortest path with distance as the weight.
        :param source: starting point
        :param target: end point
        :return: shortest path between starting point and end point
        """
        return nx.shortest_path(self.__DiGraph, source=self.__start, target=self.__next, weight='distance')

    def turn_by_turn_instruction(self):
        """
        Provide turn-by-turn navigation instruction. Using all internal parameters.
        """
        print('Start route from', self.__start, 'to', self.__next + '.')
        total_distance = 0                                                  # accelerator
        for i in range(1, len(self.__path)):
            # get the direction and distance between each two node
            direction = self.__DiGraph[self.__path[i - 1]][self.__path[i]]['direction']
            distance = self.__DiGraph[self.__path[i - 1]][self.__path[i]]['distance']
            # deduct the sentinel values
            if distance >=10000:
                distance = round((distance - 10000),2)
            path_name = self.__DiGraph[self.__path[i - 1]][self.__path[i]]['path']
            total_distance += distance
            print('Walk along', path_name, 'road for', distance, 'miles in',
                      Navigation.direction_narrative(direction), 'direction to', self.__path[i] + '.')
        print('You have arrived at', self.__next + '.')
        print('The total distance is', str(round(total_distance,2)), 'miles.')

if __name__ == "__main__":
    h_flag = False                                                                          # set the default mode as the normal mode
    while True:
        handicap_flag_str = input('Do you need a handicapped accessible route? (Y/N) \n')   # ask whether they require a handicapped-accessible route
        if handicap_flag_str in ['Y', 'y']:
            h_flag = True                                                                   # change to the handicapped accessible mode
            break
        elif handicap_flag_str in ['N', 'n']:
            break
    Disney = Navigation('edges.csv', 'nodes.csv', handicap_flag=h_flag)                     # build the object
    Disney.list_all_attractions()
    Disney.connections()
    start = next = str()
    action_flag_str = 'I'
    while True:
        while True:
            if action_flag_str == 'I':                                                      # first time
                start = str(input('Please input a starting point:\n'))
                next = str(input('Please input the attraction you want to go:\n'))
            if action_flag_str == 'RI':                                                     # second time (reroute)
                next = str(input('Please input the attraction you want to go:\n'))
            try:
                Disney = Navigation('edges.csv', 'nodes.csv', start=start, next=next, handicap_flag=h_flag)
                Disney.calculate_shortest_path()
                print("shortest path",Disney.calculate_shortest_path() )
            except KeyError:
                # Raise an exception if the input is not a name of node
                print('Invalid attraction name. Please double check your input.\n')
                continue
            except nx.NetworkXNoPath:
                # Raise an exception if there is no route available
                print('There is no path to', next)
                action_flag_str = 'RI'
                continue
            else:
                # until the input is totally valid
                break
        Disney.turn_by_turn_instruction()
        Disney.draw_graph().show()
        action_flag = False
        while action_flag == False:
            action_flag_str = input('Restart or quit (R/Q)? \n')
            # allow the user to quit or enter another navigation query
            if action_flag_str[0] in ['Q', 'q', 'R', 'r']:
                action_flag = True
        if action_flag_str[0] in ['Q', 'q']:
            print("Exiting the program, Goodbye!")
            break
        elif action_flag_str[0] in ['R', 'r']:
            start = next
            # when starting another navigation, set the last end point as the default starting point
            next = str(input('Please input the attraction you want to go:\n'))
            continue
