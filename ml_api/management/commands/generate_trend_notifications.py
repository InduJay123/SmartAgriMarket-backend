from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from datetime import datetime, date, timedelta
import pandas as pd
import os

from ml_api.models import TrendAlert
from alerts.models import Alert

from ml_models.predictors.price_predictor import PricePredictor

User = get_user_model()

PRICE_THRESHOLD = 15.0   # % change to trigger alert

def severity_from_change(abs_pct: float) -> str:
    if abs_pct >= 30:
        return "HIGH"
    if abs_pct >= 20:
        return "MEDIUM"
    return "LOW"

class Command(BaseCommand):
    help = "Generate PRICE trend alerts and notify all farmers."

    def add_arguments(self, parser):
        parser.add_argument("--days", type=int, default=7, help="Forecast days ahead")
        parser.add_argument("--baseline-days", type=int, default=7, help="Baseline window (days)")
        parser.add_argument("--product", type=str, default=None, help="Run for only one product")

    def handle(self, *args, **opts):
        days_ahead = opts["days"]
        baseline_days = opts["baseline_days"]
        only_product = opts["product"]

        # 1) farmers (edit if you have role field)
        farmers = User.objects.filter(is_staff=False, is_superuser=False)

        # 2) Load predictor (auto-trains already in __init__)
        predictor = PricePredictor(auto_train=True)

        # 3) Load dataset once for baselines
        dataset_path = predictor.DEFAULT_DATASET_PATH
        if not os.path.exists(dataset_path):
            self.stdout.write(self.style.ERROR(f"Dataset not found: {dataset_path}"))
            return

        df = pd.read_csv(dataset_path)
        df["Date"] = pd.to_datetime(df["Date"])
        df["Product_lower"] = df["Product"].str.lower()

        products = predictor.products
        if only_product:
            products = [only_product]

        alerts_created = 0
        notifications_created = 0

        for product in products:
            baseline = self._baseline_price(df, product, baseline_days)
            if baseline is None or baseline == 0:
                # If no baseline found, skip (or set baseline from last available row)
                continue

            forecasts = predictor.predict_future(product=product, days_ahead=days_ahead)
            for f in forecasts:
                f_date = date.fromisoformat(f["date"])
                pred_val = float(f["predicted_price"])

                change_pct = ((pred_val - baseline) / baseline) * 100.0
                if abs(change_pct) < PRICE_THRESHOLD:
                    continue

                direction = "UP" if change_pct > 0 else "DOWN"
                sev = severity_from_change(abs(change_pct))
                reason = f"Predicted price {direction} by {change_pct:.1f}% vs last {baseline_days}d avg"

                alert, created = TrendAlert.objects.get_or_create(
                    product=product,
                    metric="PRICE",
                    forecast_date=f_date,
                    direction=direction,
                    defaults={
                        "predicted_value": pred_val,
                        "baseline_value": baseline,
                        "change_pct": change_pct,
                        "severity": sev,
                        "reason": reason,
                        "status": "NEW",
                    }
                )

                if not created:
                    continue

                alerts_created += 1

                title = f"PRICE {direction} Alert ({sev})"
                message = (
                    f"{product}: Forecast price on {f_date} is Rs {pred_val:.2f}. "
                    f"Baseline (last {baseline_days} days avg): Rs {baseline:.2f}. "
                    f"Change: {change_pct:.1f}%. {reason}."
                )

                final_alerts = []

                for _u in farmers:
                    final_alerts.append(
                        Alert(
                            crop_name=product,
                            category="MARKET",
                            alert_type="PRICE_ALERT",
                            message=message,
                            scheduled_for=f_date,
                            status="SENT",
                            title=title,
                            url="",
                            level=sev,
                        )
                    )

                Alert.objects.bulk_create(final_alerts, batch_size=1000)
                notifications_created += len(final_alerts)

                alert.status = "NOTIFIED"
                alert.save(update_fields=["status"])

        self.stdout.write(self.style.SUCCESS(
            f"Done. Alerts: {alerts_created}, Notifications: {notifications_created}"
        ))

    def _baseline_price(self, df: pd.DataFrame, product: str, baseline_days: int):
        pl = product.lower()
        p_df = df[df["Product_lower"] == pl].sort_values("Date")

        if p_df.empty:
            return None

        # take latest baseline_days records
        last_rows = p_df.tail(baseline_days)
        # baseline on Pettah_Wholesale (same as predictor target)
        if "Pettah_Wholesale" not in last_rows.columns:
            return None

        return float(last_rows["Pettah_Wholesale"].mean())
