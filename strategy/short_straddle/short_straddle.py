from datetime import timedelta

from data.short_straddle import data


def get_nifty_50_lower_strike(price):
    return int((price // 50) * 50)


def trade(trade_date, expiry_date, strike_price):
    lot_size = 50

    ce_data = data.get_nifty_50_options_data(trade_date, trade_date, trade_date.year, expiry_date, "CE", strike_price)
    pe_data = data.get_nifty_50_options_data(trade_date, trade_date, trade_date.year, expiry_date, "PE", strike_price)

    ce_open = float(ce_data.get("FH_OPENING_PRICE"))
    ce_close = float(ce_data.get("FH_CLOSING_PRICE"))

    pe_open = float(pe_data.get("FH_OPENING_PRICE"))
    pe_close = float(pe_data.get("FH_CLOSING_PRICE"))

    profit = (ce_open - ce_close) * lot_size + (pe_open - pe_close) * lot_size

    return profit, ce_open, ce_close, pe_open, pe_close, lot_size


def run():
    expiry_dates = data.get_expiry_data()
    nifty_50_data = data.get_nifty_50_data()
    monthly_summary_data = []
    for index, from_date in enumerate(expiry_dates[:-1]):
        next_expiry = expiry_dates[index + 1]
        trade_date = from_date
        print(f"from={from_date}, to={next_expiry}")
        total_profit = 0
        trade_data = []
        while trade_date != next_expiry:
            if trade_date in nifty_50_data:
                ohlc = nifty_50_data.get(trade_date)
                strike_price = get_nifty_50_lower_strike(ohlc.open)
                print(trade_date, f"open={ohlc.open}, close={ohlc.close}", f"strike={strike_price}")
                profit, ce_open, ce_close, pe_open, pe_close, lot_size = trade(trade_date, next_expiry, strike_price)
                print(f"Profit at {trade_date}={profit}")
                trade_data.append(
                    (
                    trade_date.strftime("%d-%b-%Y"), ohlc.open, strike_price, next_expiry.strftime("%d-%b-%Y"), ce_open,
                    ce_close, pe_open, pe_close, lot_size, profit)
                )
                total_profit += profit
            trade_date += timedelta(days=1)
        with open(f"./output/{from_date.strftime("%d-%b-%Y")}_to_{next_expiry.strftime("%d-%b-%Y")}.csv",
                  "w") as csv_file:
            data_to_store = [
                ("trade_date", "nifty_50_open", "strike_price", "expiry_date", "ce_open", "ce_close", "pe_open",
                 "pe_close", "lot_size", "profit")
            ]
            data_to_store.extend(trade_data)
            data_to_store.append(("", "", "", "", "", "", "", "", "Total Profit", str(total_profit)))
            csv_data = "\n".join(map(lambda row: ",".join([str(entry) for entry in row]), data_to_store))
            csv_file.write(csv_data)
        print(f"Profit from {from_date} to {next_expiry} is {total_profit}")
        monthly_summary_data.append(
            (
                from_date.strftime("%d-%b-%Y"), next_expiry.strftime("%d-%b-%Y"), total_profit
            )
        )
    with open("./output/monthly_summary.csv", "w") as csv_file:
        data_to_store = [
            (
                "from_date", "to_date", "profit"
            )
        ]
        data_to_store.extend(monthly_summary_data)
        csv_data = "\n".join(map(lambda row: ",".join([str(entry) for entry in row]), data_to_store))
        csv_file.write(csv_data)


run()
