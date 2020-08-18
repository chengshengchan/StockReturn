# StockReturn
A dashboard to display the return of TW stock.

![image](https://github.com/chengshengchan/StockReturn/blob/master/imgs/Dashboard.png)

# Requirements
```
twstock
dash
```

# Prepare
Prepare a csv file as following format.
Cqn use Excel/Numbers then save as csv format, need to split by `,`.

| Date     | Id   | Share| Price| Paid | Receive | Note |
|----------|------|------|------|------|---------|------|
|2018/01/26| 2454 |  30  |      | 9260 |         |      |
|2018/02/06| 2454 |  30  |      | 8660 |         |      |
|2018/03/27| 245  | -60  |      |      | 20370   |      |

Notes:
- The **Price** column can be empty.


# Usage
```
# 1. Modify the `CSVPATH` in `constant,py`.
# 2. Run to parse data from TWSW website.

$ python prepare.py

# 3. Run the webpage
$ python index.py
```

