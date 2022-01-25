import Personal_Finance_Suite
from Personal_Finance_Suite import SavingsProfile, TaxProfile
import pandas as pd


state_tax_rate_path = "./statetaxrates.csv"
state_tax_rate_table = pd.read_csv(state_tax_rate_path)


# user input / output
def pinPointTypeOfAnalysis():
    print("Welcome to Dan's Personal Finance Dashboard!")
    while True:
        try:
            response = int(input('''
                Which analysis will we perform? 
                (1) Determine your w2 taxes for this year.
                (2) Run an in-depth analysis of when you can retire.
                (3) All done for today. 
                '''))
            if response == 1:
                taxAnalysis()
            elif response == 2:
                savingsAnalysis()
            elif response == 3:
                return
            else:
                print("This is not a valid selection. Please try again.")
            continue
        except ValueError:
            print("This is not a valid selection! Please try again.")
            continue


def taxAnalysis():
    while True:
        try:
            print("Let's start with some assumptions.")
            my_salary = float(input("What is your salary? (e.g. 50000)"))
            marital_status = str(input("(married) or (single)"))
            if marital_status in ["married", "Married"]:
                spouse_salary = float(input("What is your spouse's salary? (e.g. 50000)"))
            else:
                spouse_salary = 0
            state = str(input("What state do you live in?"))
            if state not in list(state_tax_rate_table["State"]):
                print("Not a valid State! Please try again.")
                continue
            city = str(input("What city do you live in?"))
            federal_deductions = float(input("What is your federal deduction for this year? (e.g. 12550)"))
            state_deductions = float(input("What is your state deduction for this year? (e.g. 8000)"))
            if city in ["New York City", "New York", "NYC"]:
                city_deductions = float(input("What is your city deduction for this year? (e.g. 8000)"))
            else:
                city_deductions = 0
            tax_input = ("salary (combined if married) = " + "{:,.2f}".format(my_salary + spouse_salary),
                         "marital status = " + str(marital_status),
                         "state = " + str(state), "city = " + str(city),
                         "federal deduction = " + "{:,.2f}".format(federal_deductions),
                         "state deduction = " + "{:,.2f}".format(state_deductions),
                         "city deduction = " + "{:,.2f}".format(city_deductions))
            tax_input_formatted = "\n".join(tax_input)
            print(tax_input_formatted)
            undo = input("Want to undo a parameter before we run your analysis (yes) or (no)?\n"
                         "Type '1' to go back to the Main Menu.")
            if undo == "yes":
                continue
            elif undo == "1":
                return
            else:
                tax_info = TaxProfile(my_salary, spouse_salary, marital_status, state, city, federal_deductions,
                                      state_deductions, city_deductions)
                tax_info.taxAnalytics("run full analytics suite")
                print("We have saved a file on your local drive with your full tax analytics for 2022. \n"
                      "Thank you for using Dan's Personal Finance Dashboard!")
                return
        except ValueError:
            print("Please try again! The parameter you entered is invalid.")
            continue


def savingsAnalysis():
    while True:
        try:
            print("Let's start with some assumptions.")
            net_worth = float(input("What is your net worth? (e.g. 25000)"))
            net_worth_goal = float(input("What is your net worth goal for retirement? (e.g. 500000)"))
            my_salary = float(input("What is your salary? (e.g. 50000)"))
            marital_status = str(input("(married) or (single)"))
            if marital_status in ["married", "Married"]:
                spouse_salary = float(input("What is your spouse's salary? (e.g. 50000)"))
            else:
                spouse_salary = 0
            annual_expenses = float(input("What are your annual expenses? (e.g. 30000)"))
            salary_growth_assumption = float(input("How much do you estimate your salary will grow  each year? "
                                                   "Please enter a decimal. (e.g. 1% = 0.01)"))
            stock_market_growth_assumption = float(input("How much do you estimate the stock market "
                                                         "will grow each year? Please enter a decimal."
                                                         " (e.g. 5% = 0.05)"))
            inflation_assumption = float(input("How much do you estimate inflation will be each year? "
                                               "Please enter a decimal. (e.g. 2% = 0.02)"))
            state = str(input("What state do you live in?"))
            if state not in list(state_tax_rate_table["State"]):
                print("Not a valid State! Please try again.")
                continue
            city = str(input("What city do you live in?"))
            federal_deductions = float(input("What is your federal deduction for this year? (e.g. 12550)"))
            state_deductions = float(input("What is your state deduction for this year? (e.g. 8000)"))
            if city in ["New York City", "New York", "NYC"]:
                city_deductions = float(input("What is your city deduction for this year? (e.g. 8000)"))
            else:
                city_deductions = 0
            savings_input = ("net worth = " + "{:,.2f}".format(net_worth),
                             "retirement goal = " + "{:,.2f}".format(net_worth_goal),
                             "salary (combined if married) = " + "{:,.2f}".format(my_salary + spouse_salary),
                             "marital status = " + str(marital_status),
                             "annual expenses = " + "{:,.2f}".format(annual_expenses),
                             "annual salary growth rate = " + "{:.2%}".format(salary_growth_assumption),
                             "annual stock market growth rate = " + "{:.2%}".format(stock_market_growth_assumption),
                             "inflation = " + "{:.2%}".format(inflation_assumption),
                             "state = " + str(state), "city = " + str(city),
                             "federal deduction = " + "{:,.2f}".format(federal_deductions),
                             "state deduction = " + "{:,.2f}".format(state_deductions),
                             "city deduction = " + "{:,.2f}".format(city_deductions))
            savings_input_formatted = "\n".join(savings_input)
            print(savings_input_formatted)
            undo = input("Want to undo a parameter before we run your analysis (yes) or (no)?\n"
                         "Type '1' to go back to the Main Menu.")
            if undo == "yes":
                continue
            elif undo == "1":
                return
            else:
                savings_info = SavingsProfile(my_salary, spouse_salary, marital_status, state, city,
                                              federal_deductions, state_deductions, city_deductions, net_worth,
                                              net_worth_goal,
                                              annual_expenses, salary_growth_assumption, stock_market_growth_assumption,
                                              inflation_assumption)
                savings_info.whenCanIRetire()
                print("We have saved a file on your local drive with your full retirement journey projections. \n"
                      "Thank you for using Dan's Personal Finance Dashboard!")
                return
        except ValueError:
            print("Please try again! The parameter you entered is invalid.")
            continue


def main():
    pinPointTypeOfAnalysis()


if __name__ == "__main__":
    main()
