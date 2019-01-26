import numpy as np
import pandas as pd


class Check:

    def __init__(self, colors, customers, request):
        self.colors = colors
        self.batches = pd.DataFrame(columns=['color', 'batches'])
        self.customers = customers
        self.request = request
        self.possible = True
        self.solution = np.full(self.colors, np.NaN)
        self.nd_arr = np.empty((self.customers, self.colors, 2))
        self.nd_arr.fill(np.NaN)
        self.df = None
        self.check_input()
        self.convert_request_to_df()
        self.enrich_df()
        self.check_df()
        self.check_nd_arr()

    def convert_request_to_df(self):
        columns = ['cust_id', 'color', 'finish', 'n_paints', 'n_cust', 'n_finish']
        df = []
        for i, customer in enumerate(self.request):
            # Iterate over all entries in the request array.
            self.check_customer(customer)
            n_paints = customer[0]
            for color, finish in zip(customer[1::2], customer[::2][1:]):
                # Create a new customer.
                df.append(pd.Series([i, color, finish, n_paints, np.NaN, np.NaN],
                                    index=columns))
                # Update entry in 3D array.
                self.nd_arr[i, color - 1, finish] = True

        # Create dataframe.
        self.df = pd.DataFrame(df)

    def enrich_df(self):
        for color, group in self.df.groupby('color'):
            self.df.loc[group.index, 'n_cust'] = group['cust_id'].nunique()
            self.df.loc[group.index, 'n_finish'] = group['finish'].nunique()
        for col in self.df.columns.values:
            self.df[col] = self.df[col].astype(int)

    def check_customer(self, customer):
        if (len(customer)) % 2 != 1:
            # Ensure length of given customer array is correct.
            self.possible = False
        if not all([isinstance(i, int) for i in customer]):
            # Must be all integer values.
            self.possible = False
        if customer[0] < 1:
            # Must be a positive integer.
            self.possible = False
        if customer[0] != int(len(customer[1:]) / 2):
            # T must be correctly specified.
            self.possible = False
        if customer[1] < 1 or customer[1] > self.colors:
            # Specified color must be within permissible range.
            self.possible = False
        if customer[2] not in (0, 1):
            # Paint finish must be binary.
            self.possible = False

    def check_input(self):
        if not isinstance(self.colors, int):
            self.possible = False
        if not isinstance(self.customers, int):
            self.possible = False
        if self.colors < 1 or self.colors > 2000:
            # Number of colors must be within specified bounds.
            self.possible = False
        if self.customers < 1 or self.customers > 2000:
            # Number of customers must be within specified bounds.
            self.possible = False
        if len(self.request) != self.customers:
            # Number of customers must be correctly specified.
            self.possible = False
        if self.colors < self.customers:
            # We can only have one batch per color. Too many customers.
            self.possible = False

    def check_nd_arr(self):
        # Find unliked paint colors and set these to 0 in base solution.
        unliked = np.sum(np.nansum(self.nd_arr, axis=0), axis=1)
        self.solution[unliked == 0] = 0

    def check_df(self):
        if self.df.groupby('cust_id').apply(lambda x: x['n_paints'].unique()[0]).sum() > 3000:
            # Sum of paint choices must be less than 3000.
            self.possible = False
        for customer, group in self.df.groupby('cust_id'):
            if group['finish'].sum() > 1:
                # Too many matte finishes per customer specified.
                self.possible = False
            if group.drop_duplicates(subset=['color', 'finish']).shape[0] != group.shape[0]:
                # Duplicate entries of color and finish specified.
                self.possible = False
        for (color, finish), group in self.df.groupby(['color', 'finish']):
            if (group['n_paints'].nunique() == 1) & \
                    (group['n_paints'].unique()[0] == 1) & \
                    (group['n_paints'].shape[0] > 1):
                # We have customers competing for the same paint specifications.
                self.possible = False
            elif (group['n_paints'].nunique() == 1) & \
                    (group['n_paints'].unique()[0] == 1) & \
                    (group['n_paints'].shape[0] == 1):
                # There are some customers who only requested one paint, and who are the only
                # ones requesting that paint. These paints must be completed in this finish.
                self.solution[color - 1] = finish
