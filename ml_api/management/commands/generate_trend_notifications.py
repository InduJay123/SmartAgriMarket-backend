from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, timedelta

from ml_api.models import TrendAlert
from notifications_app.models import Notification

# Import your predictors (based on your folder structure)
from ml_models.predictors.price_predictor import predict_price
from ml_models.predictors.demand_predictor import predict_demand
from ml_models.predictors.yield_predictor import predict_yield

User = get_user_model()

PRICE_THRESHOLD = 15.0   # %
DEMAND_THRESHOLD = 20.0  # %
YIELD_THRESHOLD = 15.0   # %

def severity_from_change(abs_change_pct: float) -> str:
    if abs_change_pct >= 30:
        return "HIGH"
    if abs_change_pct >= 20:
        return "MEDIUM"
    return "LOW"

class Command(BaseCommand):
    help = "Generate trend alerts from ML predictions and notify all farmers."

    def add_arguments(self, parser):
        parser.add_argument("--days", type=int, default=7, help="Forecast days ahead")
        parser.add_argument("--crop-id", type=int, default=None, help="Run for a single crop_id")

    def handle(self, *args, **options):
        forecast_days = options["days"]
        only_crop_id = options["crop_id"]

        # 1) determine farmers (change this if you have role-based users)
        farmers = User.objects.filter(is_staff=False, is_superuser=False)

        # 2) choose crops list (replace with your Crops model if you have one)
        crop_ids = [only_crop_id] if only_crop_id else self.get_all_crop_ids()

        created_alerts = 0
        created_notifications = 0

        for crop_id in crop_ids:
            # ---- PRICE ----
            price_preds = predict_price(crop_id=crop_id, days=forecast_days)
            created_alerts, created_notifications = self.process_metric(
                crop_id, "PRICE", price_preds, PRICE_THRESHOLD, farmers,
                created_alerts, created_notifications
            )

            # ---- DEMAND ----
            demand_preds = predict_demand(crop_id=crop_id, days=forecast_days)
            created_alerts, created_notifications = self.process_metric(
                crop_id, "DEMAND", demand_preds, DEMAND_THRESHOLD, farmers,
                created_alerts, created_notifications
            )

            # ---- YIELD ----
            yield_preds = predict_yield(crop_id=crop_id, days=forecast_days)
            created_alerts, created_notifications = self.process_metric(
                crop_id, "YIELD", yield_preds, YIELD_THRESHOLD, farmers,
                created_alerts, created_notifications
            )

        self.stdout.write(self.style.SUCCESS(
            f"Done. Alerts created: {created_alerts}, Notifications created: {created_notifications}"
        ))

    def get_all_crop_ids(self):
        """
        Replace this with your Crops table query if you have it.
        For now: hardcode or load from your crops app.
        """
        # Example: from crops.models import Crop
        # return list(Crop.objects.values_list("id", flat=True))
        return [1, 2, 3, 4, 5]  # TODO: replace

    def process_metric(self, crop_id, metric, predictions, threshold, farmers,
                       created_alerts, created_notifications):
        """
        predictions expected shape:
        [
          {"date": datetime/date/str, "value": float, "baseline": float(optional)}
        ]
        If your predictor returns different format, just adjust here.
        """
        for item in predictions:
            forecast_date = item["date"]
            if isinstance(forecast_date, str):
                forecast_date = date.fromisoformat(forecast_date)
            elif hasattr(forecast_date, "date"):
                forecast_date = forecast_date if isinstance(forecast_date, date) else forecast_date.date()

            predicted_value = float(item["value"])
            baseline_value = float(item.get("baseline")) if item.get("baseline") is not None else None

            # If baseline missing, skip % logic or compute baseline from DB (recommended)
            if baseline_value and baseline_value != 0:
                change_pct = ((predicted_value - baseline_value) / baseline_value) * 100.0
            else:
                change_pct = None

            # decide if special
            if change_pct is None or abs(change_pct) < threshold:
                continue

            direction = "UP" if change_pct > 0 else "DOWN"
            sev = severity_from_change(abs(change_pct))
            reason = f"{metric} {direction} by {change_pct:.1f}%"

            # Create TrendAlert only if new (unique_together avoids duplicates)
            alert, created = TrendAlert.objects.get_or_create(
                crop_id=crop_id,
                metric=metric,
                forecast_date=forecast_date,
                direction=direction,
                defaults={
                    "predicted_value": predicted_value,
                    "baseline_value": baseline_value,
                    "change_pct": change_pct,
                    "severity": sev,
                    "reason": reason,
                    "status": "NEW",
                }
            )

            if not created:
                continue

            created_alerts += 1

            # Create notifications for ALL farmers
            notifs = []
            title = f"{metric} {direction} Alert ({sev})"
            msg = (
                f"Crop ID {crop_id}: Forecast for {forecast_date} is {predicted_value:.2f}. "
                f"Change: {change_pct:.1f}% vs baseline {baseline_value:.2f}. "
                f"Reason: {reason}."
            )

            for u in farmers:
                notifs.append(Notification(
                    user=u,
                    related_crop_id=crop_id,
                    type=f"{metric}_ALERT",
                    title=title,
                    message=msg,
                    is_read=False,
                    status="ACTIVE"
                ))

            Notification.objects.bulk_create(notifs, batch_size=1000)
            created_notifications += len(notifs)

            alert.status = "NOTIFIED"
            alert.save(update_fields=["status"])

        return created_alerts, created_notifications
