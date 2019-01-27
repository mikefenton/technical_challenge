import unittest

import numpy as np
import pandas as pd

from check import Check
from solver import solver


def convert_and_call(color, customers, demand):
    return solver({"colors": color, "customers": customers, "demands": demand})


class PaintshopTest(unittest.TestCase):

    def test_impossible(self):
        demand = [[1, 1, 0], [1, 1, 1]]
        self.assertEqual(convert_and_call(1, 2, demand), "IMPOSSIBLE")

    def test_no_matte(self):
        demand = [[1, 1, 0], [1, 2, 0]]
        self.assertEqual(convert_and_call(2, 2, demand), "0 0")

    def test_all_matte(self):
        demand = [[1, 1, 1], [2, 1, 0, 2, 1], [3, 1, 0, 2, 0, 3, 1]]
        self.assertEqual(convert_and_call(3, 3, demand), "1 1 1")

    def test_color_not_requested(self):
        demand = [[1, 5, 1], [2, 1, 0, 2, 1]]
        self.assertEqual(convert_and_call(5, 2, demand), "0 0 0 0 1")


class CheckTest(unittest.TestCase):

    def test_wrong_T_demand(self):
        demand = [[2, 1, 0]]
        self.assertEqual(convert_and_call(1, 1, demand), "IMPOSSIBLE")

    def test_too_many_matte_finishes(self):
        demand = [[2, 1, 1, 2, 1]]
        self.assertEqual(convert_and_call(2, 1, demand), "IMPOSSIBLE")

    def test_too_many_colors(self):
        demand = [[2, 1, 0, 3, 0]]
        self.assertEqual(convert_and_call(2, 1, demand), "IMPOSSIBLE")

    def test_too_many_customers(self):
        demand = [[1, 1, 0], [1, 2, 0]]
        self.assertEqual(convert_and_call(2, 1, demand), "IMPOSSIBLE")

    def test_wrong_finish(self):
        demand = [[1, 1, 2]]
        self.assertEqual(convert_and_call(1, 1, demand), "IMPOSSIBLE")

    def test_negative_values(self):
        demand = [[1, -1, 0]]
        self.assertEqual(convert_and_call(1, 1, demand), "IMPOSSIBLE")

    def test_not_enough_colors_for_customers(self):
        demand = [[1, 1, 0], [1, 1, 0]]
        self.assertEqual(convert_and_call(1, 2, demand), "IMPOSSIBLE")

    def test_too_many_paint_choices(self):
        demand = [[1, 1, 0], [2, 1, 1, 2, 0], [3, 2, 1, 3, 0, 3, 1]]
        check = Check(3, 3, demand)
        check.max_paint_combos = 5
        check.convert_request_to_df()
        self.assertEqual(check.possible, True)
        check.check_nd_arr()
        self.assertEqual(check.possible, False)

    def test_convert_request_to_df(self):
        demand = [[1, 1, 0], [2, 2, 1, 2, 0], [3, 1, 0, 2, 1, 2, 0]]
        check = Check(2, 3, demand)
        check.convert_request_to_df()

        # Define expected return.
        df = pd.DataFrame()
        df['cust_id'] = [0, 1, 1, 2, 2, 2]
        df['color'] = [1, 2, 2, 1, 2, 2]
        df['finish'] = [0, 1, 0, 0, 1, 0]
        df['n_paints'] = [1, 2, 2, 3, 3, 3]
        df['n_cust'] = np.NaN
        df['n_finish'] = np.NaN

        for col in df.columns.values:
            df[col] = df[col].astype(float)

        self.assertEqual(check.df.to_csv(), df.to_csv())

    def test_enrich_df(self):
        demand = [[1, 1, 0], [2, 2, 1, 2, 0], [3, 1, 0, 2, 1, 2, 0]]
        check = Check(2, 3, demand)

        # Define expected return.
        df = pd.DataFrame()
        df['cust_id'] = [0, 1, 1, 2, 2, 2]
        df['color'] = [1, 2, 2, 1, 2, 2]
        df['finish'] = [0, 1, 0, 0, 1, 0]
        df['n_paints'] = [1, 2, 2, 3, 3, 3]
        df['n_cust'] = np.NaN
        df['n_finish'] = np.NaN

        check.df = df.copy()

        for col in check.df.columns.values:
            check.df[col] = check.df[col].astype(float)

        check.enrich_df()

        df['n_cust'] = 2
        df['n_finish'] = [1, 2, 2, 1, 2, 2]

        self.assertEqual(check.df.to_csv(), df.to_csv())

if __name__ == "__main__":
     unittest.main()
