import os
import pandas as pd

def main():
    os.chdir(r'C:\Users\Derek\Desktop\Python Car Data\data\sale')
    final =[]
    for file in os.listdir('.'):
        if '.csv' in file:
            final.append(pd.read_csv(file))
            print(final)
    final = pd.concat(final)
    final.to_csv('sale_amount.csv', index=False)

if __name__ == "__main__":
    main()