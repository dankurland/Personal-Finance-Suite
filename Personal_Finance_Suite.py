import openpyxl
import pandas as pd
from datetime import datetime, timedelta
import xlsxwriter


now = datetime.now()
date_time = now.strftime("%m_%d_%Y %I_%M_%p")

federal_tax_rate_path = "./federaltaxrates.csv"
state_tax_rate_path = "./statetaxrates.csv"
city_tax_rate_path = "./NYCtaxrates.csv"


# calculate social security tax
class EffectiveFederalTax:

    def __init__(self, salary, marital_status):
        self.salary = salary
        self.marital_status = marital_status

    def calculateSocialSecurityTaxDue(self):
        if self.salary >= 147000:
            return 9114
        else:
            return round(self.salary * 0.062, 2)


# calculate federal income tax + remainder of fica (medicare) for single filers
class EffectiveFederalTaxSingle(EffectiveFederalTax):
    def __init__(self, salary, deductions):
        super().__init__(salary, "single")
        self.deductions = deductions

    def calculateFederalIncomeTaxDue(self):
        federal_tax_rate_table = pd.read_csv(federal_tax_rate_path)
        federal_tax_bracket_tier = 0
        single_income_column = federal_tax_rate_table.columns.get_loc("Single Income")
        single_income_percentage_tax_column = federal_tax_rate_table.columns.get_loc("Single Tax Rate")
        max_index = len(list(federal_tax_rate_table.index)) - 1
        while federal_tax_bracket_tier <= max_index and \
                int(federal_tax_rate_table.iloc[federal_tax_bracket_tier, single_income_column]) < \
                (self.salary - self.deductions):
            federal_tax_bracket_tier += 1
        federal_tax_bracket_tier -= 1
        federal_tax_due = 0
        counter = 0
        while counter <= federal_tax_bracket_tier - 1:
            federal_tax_due += (federal_tax_rate_table.iloc[counter + 1, single_income_column]
                                - federal_tax_rate_table.iloc[counter, single_income_column])\
                               * (float((federal_tax_rate_table.iloc[counter, single_income_percentage_tax_column])
                                     .strip("%")) / 100)
            counter += 1
        marginal_tax_due = (self.salary - self.deductions - federal_tax_rate_table.iloc[federal_tax_bracket_tier,
                                                                                        single_income_column]) \
                           * (float((federal_tax_rate_table.iloc[federal_tax_bracket_tier,
                            single_income_percentage_tax_column]).strip("%")) / 100)
        federal_tax_due += marginal_tax_due
        return round(federal_tax_due, 2)

    def calculateMedicareTaxDue(self):
        if self.salary <= 200000:
            return round(self.salary * 0.0145, 2)
        else:
            return round(self.salary * 0.0145 + (self.salary - 200000) * 0.009, 2)

    def calculateTotalFederalTaxesDue(self):
        return self.calculateSocialSecurityTaxDue() + self.calculateFederalIncomeTaxDue() \
               + self.calculateMedicareTaxDue()


# calculate federal income tax + remainder of fica (medicare) for married filers
class EffectiveFederalTaxMarried(EffectiveFederalTax):

    def __init__(self, salary, deductions):
        super().__init__(salary, "Married")
        self.deductions = deductions

    def calculateFederalIncomeTaxDue(self):
        federal_tax_rate_table = pd.read_csv(federal_tax_rate_path)
        federal_tax_bracket_tier = 0
        married_income_column = federal_tax_rate_table.columns.get_loc("Married Income")
        married_income_percentage_tax_column = federal_tax_rate_table.columns.get_loc("Married Tax Rate")
        max_index = len(list(federal_tax_rate_table.index)) - 1
        while federal_tax_bracket_tier <= max_index and \
                int(federal_tax_rate_table.iloc[federal_tax_bracket_tier, married_income_column]) \
                < (self.salary - self.deductions):
            federal_tax_bracket_tier += 1
        federal_tax_bracket_tier -= 1
        federal_tax_due = 0
        counter = 0
        while counter <= federal_tax_bracket_tier - 1:
            federal_tax_due += (federal_tax_rate_table.iloc[counter + 1, married_income_column]
                                - federal_tax_rate_table.iloc[counter, married_income_column])\
                               * (float((federal_tax_rate_table.iloc[counter, married_income_percentage_tax_column])
                                     .strip("%")) / 100)
            counter += 1
        marginal_tax_due = (self.salary - self.deductions - federal_tax_rate_table.iloc[federal_tax_bracket_tier,
                                                                                        married_income_column])\
                           * (float((federal_tax_rate_table.iloc[federal_tax_bracket_tier,
                            married_income_percentage_tax_column]).strip("%")) / 100)
        federal_tax_due += marginal_tax_due
        return round(federal_tax_due, 2)

    def calculateMedicareTaxDue(self):
        if self.salary <= 250000:
            return round(self.salary * 0.0145, 2)
        else:
            return round(self.salary * 0.0145 + (self.salary - 250000) * 0.009, 2)

    def calculateTotalFederalTaxesDue(self):
        return self.calculateSocialSecurityTaxDue() + self.calculateFederalIncomeTaxDue() \
               + self.calculateMedicareTaxDue()


class EffectiveStateTax:

    def __init__(self, salary, state, marital_status):
        self.salary = salary
        self.state = state
        self.marital_status = marital_status


# calculate state income tax for single filers
class EffectiveStateTaxSingle(EffectiveStateTax):

    def __init__(self, salary, state, deductions):
        super().__init__(salary, state, "single")
        self.deductions = deductions

    def calculateStateIncomeTaxDue(self):
        state_tax_rate_table = pd.read_csv(state_tax_rate_path)
        my_state_tax_rate_table = state_tax_rate_table.loc[state_tax_rate_table["State"] == str(self.state)]
        single_income_column = my_state_tax_rate_table.columns.get_loc("Single Filer Brackets")
        single_income_percentage_tax_column = my_state_tax_rate_table.columns.get_loc("Single Filer Rates")
        max_index = my_state_tax_rate_table["Single Filer Rates"].notnull().sum() - 1
        if my_state_tax_rate_table.iloc[max_index, single_income_percentage_tax_column] == "none":
            return 0
        state_tax_bracket_tier = 0
        while state_tax_bracket_tier <= max_index and \
                int(my_state_tax_rate_table.iloc[state_tax_bracket_tier, single_income_column]) \
                < (self.salary - self.deductions):
            state_tax_bracket_tier += 1
        state_tax_bracket_tier -= 1
        state_tax_due = 0
        counter = 0
        while counter <= state_tax_bracket_tier - 1:
            state_tax_due += (my_state_tax_rate_table.iloc[counter + 1, single_income_column]
                                - my_state_tax_rate_table.iloc[counter, single_income_column])\
                               * (float((my_state_tax_rate_table.iloc[counter, single_income_percentage_tax_column])
                                     .strip("%")) / 100)
            counter += 1
        marginal_tax_due = (self.salary - self.deductions - my_state_tax_rate_table.iloc[state_tax_bracket_tier,
                                                                                        single_income_column])\
                           * (float((my_state_tax_rate_table.iloc[state_tax_bracket_tier,
                            single_income_percentage_tax_column]).strip("%")) / 100)
        state_tax_due += marginal_tax_due
        return (round(state_tax_due, 2))


# calculate state income tax for married filers
class EffectiveStateTaxMarried(EffectiveStateTax):

    def __init__(self, salary, state, deductions):
        super().__init__(salary, state, "married")
        self.deductions = deductions

    def calculateStateIncomeTaxDue(self):
        state_tax_rate_table = pd.read_csv(state_tax_rate_path)
        my_state_tax_rate_table = state_tax_rate_table.loc[state_tax_rate_table["State"] == str(self.state)]
        married_income_column = my_state_tax_rate_table.columns.get_loc("Married Filing Jointly Brackets")
        married_income_percentage_tax_column = my_state_tax_rate_table.columns.get_loc("Married Filing Jointly Rates")
        max_index = my_state_tax_rate_table["Married Filing Jointly Rates"].notnull().sum() - 1
        if my_state_tax_rate_table.iloc[max_index, married_income_percentage_tax_column] == "none":
            return 0
        state_tax_bracket_tier = 0
        while state_tax_bracket_tier <= max_index and \
                int(my_state_tax_rate_table.iloc[state_tax_bracket_tier, married_income_column]) \
                < (self.salary - self.deductions):
            state_tax_bracket_tier += 1
        state_tax_bracket_tier -= 1
        state_tax_due = 0
        counter = 0
        while counter <= state_tax_bracket_tier - 1:
            state_tax_due += (my_state_tax_rate_table.iloc[counter + 1, married_income_column]
                                - my_state_tax_rate_table.iloc[counter, married_income_column])\
                               * (float((my_state_tax_rate_table.iloc[counter, married_income_percentage_tax_column])
                                     .strip("%")) / 100)
            counter += 1
        marginal_tax_due = (self.salary - self.deductions - my_state_tax_rate_table.iloc[state_tax_bracket_tier,
                                                                                        married_income_column])\
                           * (float((my_state_tax_rate_table.iloc[state_tax_bracket_tier,
                            married_income_percentage_tax_column]).strip("%")) / 100)
        state_tax_due += marginal_tax_due
        return (round(state_tax_due, 2))


class EffectiveCityTax:

    def __init__(self, salary, city, marital_status):
        self.salary = salary
        self.city = city
        self.marital_status = marital_status


# calculate city income tax for single filers
class EffectiveCityTaxSingle(EffectiveCityTax):

    def __init__(self, salary, city, deductions):
        super().__init__(salary, city, "single")
        self.deductions = deductions

    def calculateCityIncomeTaxDue(self):
        city_tax_rate_table = pd.read_csv(city_tax_rate_path)
        city_tax_bracket_tier = 0
        single_income_column = city_tax_rate_table.columns.get_loc("Single Income")
        single_income_percentage_tax_column = city_tax_rate_table.columns.get_loc("Single Tax Rate")
        max_index = len(list(city_tax_rate_table.index)) - 1
        while city_tax_bracket_tier <= max_index and \
        int(city_tax_rate_table.iloc[city_tax_bracket_tier, single_income_column]) < (self.salary - self.deductions):
            city_tax_bracket_tier += 1
        city_tax_bracket_tier -= 1
        city_tax_due = 0
        counter = 0
        while counter <= city_tax_bracket_tier - 1:
            city_tax_due += (city_tax_rate_table.iloc[counter + 1, single_income_column]
                            - city_tax_rate_table.iloc[counter, single_income_column]) \
                           * (float((city_tax_rate_table.iloc[counter, single_income_percentage_tax_column])
                                    .strip("%")) / 100)
            counter += 1
        marginal_tax_due = (self.salary - self.deductions - city_tax_rate_table.iloc[city_tax_bracket_tier,
                                                                                    single_income_column]) \
                       * (float((city_tax_rate_table.iloc[city_tax_bracket_tier,
                                                             single_income_percentage_tax_column]).strip("%")) / 100)
        city_tax_due += marginal_tax_due
        return round(city_tax_due, 2)


# calculate city income tax for married filers
class EffectiveCityTaxMarried(EffectiveCityTax):

    def __init__(self, salary, city, deductions):
        super().__init__(salary, city, "married")
        self.deductions = deductions

    def calculateCityIncomeTaxDue(self):
        city_tax_rate_table = pd.read_csv(city_tax_rate_path)
        city_tax_bracket_tier = 0
        married_income_column = city_tax_rate_table.columns.get_loc("Married Income")
        married_income_percentage_tax_column = city_tax_rate_table.columns.get_loc("Married Tax Rate")
        max_index = len(list(city_tax_rate_table.index)) - 1
        while city_tax_bracket_tier <= max_index and \
        int(city_tax_rate_table.iloc[city_tax_bracket_tier, married_income_column]) < (self.salary - self.deductions):
            city_tax_bracket_tier += 1
        city_tax_bracket_tier -= 1
        city_tax_due = 0
        counter = 0
        while counter <= city_tax_bracket_tier - 1:
            city_tax_due += (city_tax_rate_table.iloc[counter + 1, married_income_column]
                            - city_tax_rate_table.iloc[counter, married_income_column]) \
                           * (float((city_tax_rate_table.iloc[counter, married_income_percentage_tax_column])
                                    .strip("%")) / 100)
            counter += 1
        marginal_tax_due = (self.salary - self.deductions - city_tax_rate_table.iloc[city_tax_bracket_tier,
                                                                                    married_income_column]) \
                       * (float((city_tax_rate_table.iloc[city_tax_bracket_tier,
                                                             married_income_percentage_tax_column]).strip("%")) / 100)
        city_tax_due += marginal_tax_due
        return round(city_tax_due, 2)


# calculate effective tax rate from the classes/inheritance structure we have created
class TaxProfile:

    def __init__(self, my_salary, spouse_salary, marital_status, state, city, federal_deductions, state_deductions,
                 city_deductions):
        self.my_salary = my_salary
        self.spouse_salary = spouse_salary
        self.salary = my_salary + spouse_salary
        self.marital_status = marital_status
        self.state = state
        self.city = city
        self.federal_deductions = federal_deductions
        self.state_deductions = state_deductions
        self.city_deductions = city_deductions

    def createTaxAnalysisWorkBook(self):
        workbook = xlsxwriter.Workbook("./" + "Tax_Analysis_" + str(date_time) + ".xlsx")
        workbook.close()
        assumptions_table = [["salary", "{:,.2f}".format(self.salary)], ["marital_status", str(self.marital_status)],
                            ["state", str(self.state)],
                            ["city", str(self.city)],
                            ["federal_deductions", "{:,.2f}".format(self.federal_deductions)],
                            ["state_deductions", "{:,.2f}".format(self.state_deductions)],
                            ["city_deductions", "{:,.2f}".format(self.city_deductions)]]
        assumption_columns = ["Field", "Assumption"]
        assumptions = pd.DataFrame(assumptions_table, columns=assumption_columns)
        path = "./" + "Tax_Analysis_" + str(date_time) + ".xlsx"
        with pd.ExcelWriter(str(path), engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
            assumptions.to_excel(writer, sheet_name="Sheet1")

    # calculate tax rate/breakdown for federal, state, and city and (if flag is not set to "please just return
    # effective tax rate") export to workbook
    def taxAnalytics(self, flag):
        if self.marital_status == "married":
            my_social_security_tax_object = EffectiveFederalTax(self.my_salary, "married")
            spouse_social_security_tax_object = EffectiveFederalTax(self.spouse_salary, "married")
            social_security_tax_objects = [my_social_security_tax_object, spouse_social_security_tax_object]
            federal_tax_object = EffectiveFederalTaxMarried(self.salary, self.federal_deductions)
            state_tax_object = EffectiveStateTaxMarried(self.salary, self.state, self.state_deductions)
            city_tax_object = EffectiveCityTaxMarried(self.salary, self.city, self.city_deductions)
        else:
            my_social_security_tax_object = EffectiveFederalTax(self.my_salary, "single")
            social_security_tax_objects = [my_social_security_tax_object]
            federal_tax_object = EffectiveFederalTaxSingle(self.salary, self.federal_deductions)
            state_tax_object = EffectiveStateTaxSingle(self.salary, self.state, self.state_deductions)
            city_tax_object = EffectiveCityTaxSingle(self.salary, self.city, self.city_deductions)
        social_security_tax_amount = 0
        for social_security_tax_object in social_security_tax_objects:
            social_security_tax_amount += social_security_tax_object.calculateSocialSecurityTaxDue()
        medicare_tax_amount = federal_tax_object.calculateMedicareTaxDue()
        fica_tax_amount = social_security_tax_amount + medicare_tax_amount
        federal_income_tax_amount = federal_tax_object.calculateFederalIncomeTaxDue()
        total_federal_tax_amount = round(social_security_tax_amount + medicare_tax_amount + federal_income_tax_amount,
                                         2)
        state_income_tax_amount = state_tax_object.calculateStateIncomeTaxDue()
        if self.city == "New York City":
            city_income_tax_amount = city_tax_object.calculateCityIncomeTaxDue()
        else:
            city_income_tax_amount = 0
        total_tax_amount = total_federal_tax_amount + state_income_tax_amount + city_income_tax_amount
        if flag == "please just return effective tax rate":
            return total_tax_amount / self.salary
        analytics_table = [["total tax paid", "{:,.2f}".format(total_tax_amount)],
                               ["effective tax rate", str("{:.2%}".format(total_tax_amount / self.salary))],
                               ["total federal tax paid", "{:,.2f}".format(total_federal_tax_amount)],
                               ["effective federal tax rate", str("{:.2%}".format(total_federal_tax_amount /
                                                                                  self.salary))],
                               ["total fica tax paid", "{:,.2f}".format(fica_tax_amount)],
                               ["fica tax rate", str("{:.2%}".format(fica_tax_amount / self.salary))],
                               ["federal income tax paid", "{:,.2f}".format(federal_income_tax_amount)],
                               ["effective federal income tax rate", str("{:.2%}".format(federal_income_tax_amount
                                                                                         / self.salary))],
                               ["total state income tax paid", "{:,.2f}".format(state_income_tax_amount)],
                               ["effective state income tax rate", str("{:.2%}".format(state_income_tax_amount
                                                                                       / self.salary))],
                               ["total city income tax paid", "{:,.2f}".format(city_income_tax_amount)],
                               ["effective city income tax rate", str("{:.2%}".format(city_income_tax_amount
                                                                                      / self.salary))]]
        self.createTaxAnalysisWorkBook()
        dataframe = pd.DataFrame(analytics_table)
        path = "./" + "Tax_Analysis_" + str(date_time) + ".xlsx"
        with pd.ExcelWriter(str(path), engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
            dataframe.to_excel(writer, sheet_name=str(date_time), header=False, index=False)


# based on dynamically calculating the effective tax rate and other parameters each year, calculate how many years
# until retirement and provide relevant analytics to client
class SavingsProfile(TaxProfile):

    def __init__(self, my_salary, spouse_salary, marital_status, state, city, federal_deductions, state_deductions,
                 city_deductions, net_worth, net_worth_goal, annual_expenses, salary_growth_assumption,
                 stock_market_growth_assumption, inflation_assumption):
        super().__init__(my_salary, spouse_salary, marital_status, state, city, federal_deductions, state_deductions,
                 city_deductions)
        self.net_worth = net_worth
        self.net_worth_goal = net_worth_goal
        self.annual_expenses = annual_expenses
        self.salary_growth_assumption = salary_growth_assumption
        self.stock_market_growth_assumption = stock_market_growth_assumption
        self.inflation_assumption = inflation_assumption

    def createSavingsAnalysisWorkBook(self):
        workbook = xlsxwriter.Workbook("./" + "Savings_Analysis_" + str(date_time) + ".xlsx")
        workbook.close()

        assumptions_table = [["net worth", "{:,.2f}".format(self.net_worth)],
                             ["retirement goal", "{:,.2f}".format(self.net_worth_goal)],
                            ["current salary", "{:,.2f}".format(self.salary)],
                            ["current effective tax rate",
                             "{:.2%}".format(self.taxAnalytics("please just return effective tax rate"))],
                            ["annual expenses", "{:,.2f}".format(self.annual_expenses)],
                            ["annual salary growth rate", "{:.2%}".format(self.salary_growth_assumption)],
                            ["annual stock market growth", "{:.2%}".format(self.stock_market_growth_assumption)],
                            ["annual inflation", "{:.2%}".format(self.inflation_assumption)]]
        assumption_columns = ["Field", "Assumption"]
        assumptions = pd.DataFrame(assumptions_table, columns=assumption_columns)
        path = "./" + "Savings_Analysis_" + str(date_time) + ".xlsx"
        with pd.ExcelWriter(str(path), engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
            assumptions.to_excel(writer, sheet_name="Sheet1")

    def whenCanIRetire(self):
        year = 0
        net_worth = self.net_worth
        salary = self.salary
        my_salary = self.my_salary
        spouse_salary = self.spouse_salary
        effective_tax_rate = self.taxAnalytics("please just return effective tax rate")
        annual_expenses = self.annual_expenses
        retirement_progression = [[year, "{:,.2f}".format(net_worth), "{:,.2f}".format(salary),
                                   "{:.2%}".format(effective_tax_rate), "{:,.2f}".format(annual_expenses)]]
        while net_worth < self.net_worth_goal and year < 200:
            year += 1
            net_worth = max(net_worth * (1 + self.stock_market_growth_assumption), net_worth) \
                        + salary * (1 - effective_tax_rate) - annual_expenses
            salary *= (1 + self.salary_growth_assumption)
            my_salary *= (1 + self.salary_growth_assumption)
            spouse_salary *= (1 + self.salary_growth_assumption)
            annual_expenses *= (1 + self.inflation_assumption)
            tax_rate_calculator = TaxProfile(my_salary, spouse_salary, self.marital_status, self.state, self.city,
                                             self.federal_deductions, self.state_deductions, self.city_deductions)
            effective_tax_rate = tax_rate_calculator.taxAnalytics("please just return effective tax rate")
            retirement_progression.append([year, "{:,.2f}".format(net_worth), "{:,.2f}".format(salary),
            "{:.2%}".format(effective_tax_rate), "{:,.2f}".format(annual_expenses)])
        self.createSavingsAnalysisWorkBook()
        headers = ["year", "net worth", "salary", "effective tax rate", "annual expenses"]
        dataframe = pd.DataFrame(retirement_progression, columns=headers)
        path = "./" + "Savings_Analysis_" + str(date_time) + ".xlsx"
        with pd.ExcelWriter(str(path), engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
            dataframe.to_excel(writer, sheet_name=str(date_time), index=False)
