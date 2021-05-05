import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression

path = "uploads/"


def linear_regression(username, dependent="y", independents=["x"]):
    try:
        local_path = "{}/{}".format(path, username)
        dataset = pd.read_csv(local_path + "/dataset_train.csv")

        x = dataset[independents]
        y = dataset[dependent]
        x = x.fillna(x.mean())
        y = y.fillna(y.mean())

        number_of_rows = y.size
        test_size = 0.2
        a = int((1 - test_size) * number_of_rows)
        output_y = pd.Series(y.iloc[a:number_of_rows].values)

        # Split the dataset into the training set and test set
        xTrain, xTest, yTrain, yTest = train_test_split(x, y, test_size=0.2, random_state=0)

        linearRegressor = LinearRegression()
        linearRegressor.fit(xTrain, yTrain)

        yPrediction = pd.Series(linearRegressor.predict(xTest))
        output = pd.DataFrame({"Actual Y": output_y, "Predicted Y": yPrediction})
        # File to send as a response
        output.to_csv(local_path + "/output.csv")
        return True
    except:
        return False
