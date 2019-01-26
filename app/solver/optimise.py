from __future__ import print_function, division

import numpy as np

from itertools import product, permutations


class Optimise:

    def __init__(self, colors, customers, solution, nd_arr):
        self.colors = colors
        self.customers = customers
        self.solution = solution
        self.nd_arr = nd_arr
        self.iterations = 0
        self.optimal = False
        self.nan_idx = np.isnan(self.solution)
        self.cust_arr, self.remaining_custs, self.one_color_custs = self.get_basic_customer_mapping()
        self.nan_idx_cust = np.isnan(self.cust_arr)

    def get_basic_customer_mapping(self):
        # Init array with NaN values for each customer.
        cust_arr = np.full(self.colors, np.NaN)

        # Get the number of paint colors each customer likes.
        color_custs = np.sum(np.nansum(self.nd_arr, axis=1), axis=1)

        # Single out customers who only like one color.
        one_color_custs = color_custs == 1

        for cust_id in np.arange(self.customers)[color_custs == 1]:
            # Iterate over all customers who only liked one color

            # This customer can only get this paint.
            cust_arr[np.nansum(self.nd_arr[cust_id, :, :], axis=1) == 1] = cust_id

        if np.all(np.sort(cust_arr[~np.isnan(cust_arr)]) == np.arange(self.customers)):
            # Optimality achieved with no optimisation necessary.
            self.optimal = True

        # Get remaining customers who don't have a default slot.
        satisfied_custs = cust_arr[~np.isnan(cust_arr)]
        all_custs = np.arange(self.customers)
        remaining_custs = np.setdiff1d(all_custs, satisfied_custs, assume_unique=True)

        num_remaining_custs = len(remaining_custs)
        num_remaining_colors = sum(self.nan_idx)
        if num_remaining_custs < num_remaining_colors:
            # More color slots than customers. Pad with NaN.
            for i in range(num_remaining_colors - num_remaining_custs):
                remaining_custs = np.append(remaining_custs, np.NaN)

        return cust_arr, remaining_custs, one_color_custs

    def get_fitness(self, solution):
        return np.nansum(solution)

    def check_solution(self, solution):
        """
        Given a candidate binary array solution, check whether this solution
        satisfies the requirements of the original df, i.e. that each customer
        has at least one paint they like.

        :param solution: A candidate binary array solution.
        :return: True if solution satisfies requirements, else False.
        """

        # Initial state is that this solution doesn't work.
        full_result = False

        for cust_perm in permutations(self.remaining_custs):
            # Iterate over all combinations of customer to create array
            # of customer IDs.

            # Create copy of the customer array.
            cust_arr = np.copy(self.cust_arr)

            # Fill empty slots of customer array.
            cust_arr[self.nan_idx] = cust_perm

            # Will this permutation of customers work?
            perm_result = True

            # Check if all customer IDs match their requirements.
            for color, cust, finish in zip(np.argwhere(self.nan_idx).flatten(), cust_arr[self.nan_idx],
                                           solution[self.nan_idx]):
                if np.isnan(cust):
                    continue

                if np.isnan(self.nd_arr[int(cust), int(color), int(finish)]):
                    # This customer doesn't like this paint spec.
                    perm_result = False
                    break

            self.iterations += 1

            if perm_result:
                # We have a permutation of customers who are all satisfied.
                full_result = True
                break

        return full_result

    def iterate_all_combinations(self):
        """
        Iterate over all possible combinations of paint colors and finishes.
        Check each one to see if it is valid (i.e. if it satisfies all customers).
        If so, calculate its fitness (the number of glossy finishes).
        Save the solution with the lowest fitness.

        :return: Nothing.
        """

        # Find paints that must be glossy & matte.
        self.solution[np.nansum(self.nd_arr[self.one_color_custs, :, 0], axis=0) == 1.0] == 0
        self.solution[np.nansum(self.nd_arr[self.one_color_custs, :, 1], axis=0) == 1.0] == 1

        # Update the NaN index.
        self.nan_idx = np.isnan(self.solution)

        if np.sum(self.nan_idx) == 0 and self.optimal:
            # Optimal solution found without optimisation.
            self.solution = self.solution.astype(int)
            return

        # Get best possible fitness from what we have.
        best_fitness = self.get_fitness(np.nan_to_num(self.solution))

        # Get all binary combinations of the remaining values.
        all_combos = product([0, 1], repeat=np.sum(self.nan_idx))

        # Store best so far.
        best = [np.inf, self.solution]

        for combo in all_combos:
            # Iterate over everything.

            # Build the solution.
            solution = np.copy(self.solution)

            # Fill NaN values in the solution with this combination.
            solution[self.nan_idx] = combo

            # Check whether solution is valid.
            valid = self.check_solution(solution.astype(int))

            if valid:
                # Get fitness.
                fitness = self.get_fitness(solution)
                if fitness < best[0]:
                    # Update the best
                    best = [fitness, solution]

                    # Check whether we have achieved optimality.
                    if fitness == best_fitness:
                        break
        self.solution = best[1].astype(int)
