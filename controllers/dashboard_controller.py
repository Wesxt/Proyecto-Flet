from models.sale import Sale
from models.product import Product

class DashboardController:
    def __init__(self, view):
        self.view = view

    def get_dashboard_data(self):
        today_revenue = Sale.get_today_revenue()
        today_sales_count = Sale.get_today_sales_count()
        stock_alerts_count = Product.get_alerts_count()
        recent_sales = Sale.get_recent(5)
        stock_alerts = Product.get_alerts()
        
        # Limit stock alerts in Python side just like SQL query did
        stock_alerts = stock_alerts[:5]

        return {
            "today_revenue": today_revenue,
            "today_sales_count": today_sales_count,
            "stock_alerts_count": stock_alerts_count,
            "recent_sales": recent_sales,
            "stock_alerts": stock_alerts
        }
