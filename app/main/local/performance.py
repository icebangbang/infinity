from app import application
application.create_app("infinity")

from app.main.task import stock_task

stock_task.sync_profit.apply_async(args=[])

stock_task.sync_balance.apply_async(args=[])

stock_task.sync_cash_flow.apply_async(args=[])

# stock_task.sync_analysis_indicator.apply_async(args=[])