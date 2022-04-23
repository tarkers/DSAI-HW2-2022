import pandas as pd
import numpy as np


def load_data(csv):
    df = pd.read_csv(csv, names=["open", "high", "low", "close"])
    return df


class Trader:
    def __init__(self) -> None:
        self.now_hold = 0
        self.high_peak = 0
        self.low_peak = 99999
        self.last_rows = []
        self.predict_actions = []
        self.hold_price = 0
        self.is_hold = 0
        self.uptime = 0
        self.droptime = 0
        self.last_open_price = 0

    def predict_action(self, row):
        last_day_diff = row.open-self.last_open_price
        today_diff = round(row.close-row.open, 2)
        if last_day_diff > 0:  # 確認漲幅情勢
            self.uptime += 1
            self.droptime = 0
        else:
            self.uptime = 0
            self.droptime += 1
        '''
        simple check 
        '''
        if self.is_hold == 1:  # check to hold or sold
            if self.uptime>2: #連三漲 賣
                self.is_hold=0
                return -1
            else:  #續抱
                return 0
        elif self.is_hold == 0:  # check to buy or short or do nothing
            if self.uptime>3: #作空
                self.is_hold=-1
                self.hold_price=row.open
                return -1
            elif self.droptime>2:  #買進
                self.is_hold=1
                return 1
            else:  #不入場
                return 0 
        elif self.is_hold == -1:  # check to hold or buy 
            if row.open > self.hold_price:  # hold     
                return 0
            else:           #買回
                self.is_hold=0
                return 1

        else:
            print("error,check algorithm ")

    def train(self, train_df, prev_data=5,range_list=20):
        self.last_close = np.array(train_df['open'].tail(prev_data))
        self.high_peak = np.amax(train_df['open'].tail(range_list))
        self.high_peak = np.amin(train_df['open'].tail(range_list))
        for index in range(len(self.last_close)):
            if index == 0:
                continue
            else:
                if self.high_peak < self.last_close[index]:
                    self.high_peak = self.last_close[index]
                if self.low_peak > self.last_close[index]:
                    self.low_peak = self.last_close[index]

                diff = round(self.last_close[index] -
                             self.last_close[index-1], 2)
                if diff > 0:
                    self.uptime += 1
                    self.droptime = 0
                    self.predict_actions.append(1)
                elif diff == 0:
                    self.predict_actions.append(0)
                else:
                    self.uptime = 0
                    self.droptime += 1
                    self.predict_actions.append(-100)
            self.last_open_price = self.last_close[index]
        # print(self.predict_actions,self.high_peak,self.low_peak,self.uptime,self.droptime)


if __name__ == "__main__":
    # You should not modify this part.
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--training", default="training_data.csv",
                        help="input training data file name")
    parser.add_argument("--testing", default="testing_data.csv",
                        help="input testing data file name")
    parser.add_argument("--output", default="output.csv",
                        help="output file name")
    args = parser.parse_args()

    # The following part is an example.
    # You can modify it at will.
    training_data = load_data(args.training)
    trader = Trader()
    trader.train(training_data)

    testing_data = load_data(args.testing)

    with open(args.output, 'w', encoding='UTF8', newline='') as output_file:
        # first day do nothing
        output_file.write(str(0)+"\n")
        for index, row in testing_data.iterrows():
            # We will perform your action as the open price in the next day.
            action = trader.predict_action(row)
            if index != len(testing_data.index)-2:
                output_file.write(str(action)+"\n")
            else:
                break
