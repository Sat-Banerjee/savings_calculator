import json
from matplotlib import pyplot as plt

def handle_head(data_json, head_type):
    monthly_head_val = 0
    for key, value in data_json.iteritems():
        if key == "monthly":
            # handle monthly income(s)
            for mKey, mVal in value.iteritems():
                print "Taking into account(" + str(head_type) + ") of: " + str(mVal) + " under the head: " + mKey
                monthly_head_val += mVal

        elif key == "other":
            # handle other income(s)
            for oKey, oVal in value.iteritems():
                # for this other income source
                print "Taking into account(" + str(head_type) + ") of: " + str(oVal) + " under the head: " + oKey
                amount = oVal["amount"]
                freq = oVal["pay_frequency"]
                monthly_head_val += float(amount * freq) / 12
    
    return monthly_head_val

def handle_inflation(data_json):
    return float (data_json["percentage"])

def handle_increment(data_json):
    return (float(data_json["yearly"]["percentage"]), 
            float(data_json["promotion"]["percentage"]), 
            float(data_json["promotion"]["interval"]),
            float(data_json["salary_cap"]))

def handle_age(data_json):
    return (float(data_json["current"]), float(data_json["retirement"]))

def handle_intrest_rate(data_json):
    return (float(data_json["percentage"]))

# just a note, for FD, final amount = principal * (1+(rate/n))**(n*t)
# where n : no. of cumulative intrest per year (intrest qtrly, half yearly or yearly)
# t : how many years
# rate : intrest rate. Eg if 10% then 0.1 
def get_maturity_value(principal, intrest_rate, time_months, cumulative_period=4):
    maturity_amount = principal * (1 + (intrest_rate/cumulative_period)) ** (cumulative_period * time_months/12)
    return maturity_amount

def get_new_val(init_value, percentage):
    percentage = float(percentage)/100 
    return (init_value * (1+percentage))


category_file = open("./category.json", "r")
category_json = json.load(category_file)
#print category_json
category_file.close()

monthly_income = 0
monthly_expense = 0
inflation = 0.0
yearly_inc = 0.0
promotion_inc = 0.0
promotion_interv = 0
curr_age = 0
retire_age = 0
intrest_rate = 0.0

for key, value in category_json.iteritems():
    if key == "income":
        monthly_income = handle_head(data_json=value, head_type="income")
        print "Monthly Income comes to : " + str(monthly_income)
    elif key == "expense":
        monthly_expense = handle_head(data_json=value, head_type="expense")
        print "Monthly Expense comes to : " + str(monthly_expense)
    elif key == "inflation":
        inflation = handle_inflation(data_json=value)
        print "Inflation rate: " + str(inflation)
    elif key == "increment":
        yearly_inc, promotion_inc, promotion_interv, salary_cap = handle_increment(data_json=value)
        print "Yearly inc: " + str(yearly_inc) + "%"
        print "Promotion inc: " + str(promotion_inc) + "%"
        print "Promotion interval: " + str(promotion_interv) + " years"
    elif key == "age": 
        curr_age, retire_age = handle_age(value)
        print "Current age: {}, Retirement age: {}".format(str(curr_age), str(retire_age))
    elif key == "intrest_rate":
        intrest_rate = handle_intrest_rate(value)
    else : 
        print "Invalid key:" + key

# All json data is read, process the data now

total_savings = 0.0

total_months = (retire_age-curr_age)*12
months_left = total_months
dummy_list = list()

for year in range(1, int(retire_age-curr_age)+1):
    # for this year
    savings = monthly_income - monthly_expense
    
    for month in range (12):
        maturity_amount = get_maturity_value(principal=savings, intrest_rate=(5.4/100), time_months=months_left)
        print "Principal: {}, time: {} years, maturity amount: {}".format(str(savings), str(months_left/12), str(maturity_amount))
        total_savings += maturity_amount
        months_left -= 1
        dummy_list.append(total_savings)
        plt.plot (dummy_list)
        plt.draw()
        plt.pause (0.01)

    # year end
    print "Year: " + str(year)
    print "total savings: " + str(total_savings)

    # apply increment & inflation
    inc_percentage = yearly_inc
    if promotion_interv != 0 : 
        if (year % promotion_interv == 0):
            # hurray, promotion year
            inc_percentage = promotion_inc
            print "Promotion applied at year : " + str(curr_age + year)

    if monthly_income < salary_cap :
        monthly_income = get_new_val(init_value=monthly_income, percentage=inc_percentage)
    else : 
        monthly_income = salary_cap
        
    monthly_expense = get_new_val(init_value=monthly_expense, percentage=inflation)

    print "New Monthly Income: " + str(monthly_income)
    print "New Monthly Expense: " + str(monthly_expense)

plt.show()
