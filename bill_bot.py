import datetime
from telegram.ext import (
    Application,
    MessageHandler,
    CommandHandler,
    filters,
)
import yaml


# 获取当天日期
def get_date():
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d")


# 新增一笔消费
def add_record(date, money):
    with open("bill.yaml", "r") as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
    if date in data:
        data[date] += money
    else:
        data[date] = money
    data[date] = round(data[date], 2)
    with open("bill.yaml", "w") as f:
        yaml.dump(data, f)


# 获取某一天的账单
def get_bill(date):
    with open("bill.yaml", "r") as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
    if date in data:
        return round(data[date], 2)
    else:
        return 0


# 获取本月账单
async def get_month_bill(update, context):
    with open("bill.yaml", "r") as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
    month_bill = 0
    for date in data:
        if date.startswith(get_date()[:-2]):
            month_bill += data[date]
    month_bill = round(month_bill, 2)
    user_id = update.message.from_user.id
    await context.bot.send_message(user_id, f"本月消费总额: {month_bill}元")


# 获取全年账单，按月份统计
async def get_year_bill(update, context):
    current_year = get_date()[:4]  # 获取当前年份
    with open("bill.yaml", "r") as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
    year_bill = {}
    for date in data:
        if date.startswith(current_year):  # 只统计当前年份的数据
            month = date[:-3]
            if month in year_bill:
                year_bill[month] += data[date]
            else:
                year_bill[month] = data[date]
            year_bill[month] = round(year_bill[month], 2)
    bill_sum = round(sum(year_bill.values()), 2)
    reply_text = f"全年消费总额: {bill_sum}元\n"
    user_id = update.message.from_user.id
    for month in sorted(year_bill.keys()):
        reply_text += f"{month}月消费总额: {round(year_bill[month], 2)}元\n"
    await context.bot.send_message(user_id, reply_text)


async def get_message(update, context):
    user_id = update.message.from_user.id
    text = update.message.text
    try:
        money = float(text)
        add_record(get_date(), money)
        await context.bot.send_message(user_id, f"新增一笔消费: {round(money, 2)}元\n今日消费总额: {get_bill(get_date())}元")
    except:
        await context.bot.send_message(user_id, "输入错误，请输入数字")



def main():
    app = Application.builder().token("<telegram bot token>").build()
    app.add_handler(CommandHandler("getmonth", get_month_bill))
    app.add_handler(CommandHandler("getyear", get_year_bill))
    app.add_handler(MessageHandler(filters.TEXT, get_message))
    app.run_polling()




if __name__ == "__main__":
    main()