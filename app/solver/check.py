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

    def check(self):
        calls = [self.check_input, self.check_customers, self.convert_request_to_df,
                 self.enrich_df, self.check_df, self.check_nd_arr]
        for method in calls:
            # We only need to do subsequent checks if things are not impossible thus far.
            if self.possible:
                method()
        return self

    def convert_request_to_df(self):
        columns = ['cust_id', 'color', 'finish', 'n_paints', 'n_cust', 'n_finish']
        df = []
        for i, customer in enumerate(self.request):
            # Iterate over all entries in the request array.
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

    def check_customers(self):
        for i, customer in enumerate(self.request):
            # logger.info("Checking customer %d.")
            self.check_customer(customer)

    def check_customer(self, customer):
        if (len(customer)) % 2 != 1:
            # Ensure length of given customer array is correct.
            # logger.info("Uneven number of entries for customer.")
            self.possible = False
        if not all([isinstance(i, int) for i in customer]):
            # Must be all integer values.
            # logger.info("All customer values not integers.")
            self.possible = False
        if not all([i >= 0 for i in customer]):
            # Must be positive integer.
            # logger.info("All customer values not positive.")
            self.possible = False
        if customer[0] != int(len(customer[1:]) / 2):
            # T must be correctly specified.
            # logger.info("T incorrectly specified")
            self.possible = False
        if any([i > self.colors for i in customer[1::2]]):
            # Specified colors must be within permissible range.
            # logger.info("Specified colors outside of permissible range.")
            self.possible = False
        if any([i not in (0, 1) for i in customer[::2][1:]]):
            # Paint finishes must be binary.
            # logger.info("Paint finish not binary.")
            self.possible = False

    def check_input(self):
        if not isinstance(self.colors, int):
            # logger.info("Specied number of colors not an integer.")
            self.possible = False
        if not isinstance(self.customers, int):
            # logger.info("Specied number of customers not an integer.")
            self.possible = False
        if self.colors < 1 or self.colors > 2000:
            # Number of colors must be within specified bounds.
            # logger.info("Number of colors must be less than 2000.")
            self.possible = False
        if self.customers < 1 or self.customers > 2000:
            # Number of customers must be within specified bounds.
            # logger.info("Number of customers must be less than 2000.")
            self.possible = False
        if len(self.request) != self.customers:
            # Number of customers must be correctly specified.
            # logger.info("Number of customers incorrectly specified.")
            self.possible = False
        if self.colors < self.customers:
            # We can only have one batch per color. Too many customers.
            # logger.info("Not enough colors for all customers")
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
