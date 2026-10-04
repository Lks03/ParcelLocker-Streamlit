from datetime import datetime


class Parcel:
    def __init__(
        self,
        parcel_id,
        tracking_number,
        recipient,
        locker_id,
        pickup_code,
        status="Stored",
        created_at=None,
        collected_at=None,
    ):
        self.parcel_id = parcel_id
        self.tracking_number = tracking_number
        self.recipient = recipient
        self.locker_id = locker_id
        self.pickup_code = pickup_code
        self.status = status
        self.created_at = created_at or datetime.now().isoformat(timespec="seconds")
        self.collected_at = collected_at

    def get_pickup_code(self):
        return self.pickup_code

    def get_recipient_name(self):
        return self.recipient.get_name()

    def is_stored(self):
        return self.status == "Stored"

    def collect(self):
        if not self.is_stored():
            raise ValueError("This parcel has already been collected.")
        self.status = "Collected"
        self.collected_at = datetime.now().isoformat(timespec="seconds")

    def to_dict(self):
        return {
            "id": self.parcel_id,
            "tracking_number": self.tracking_number,
            "recipient_name": self.recipient.get_name(),
            "recipient_contact": self.recipient.get_contact(),
            "locker_id": self.locker_id,
            "pickup_code": self.pickup_code,
            "status": self.status,
            "created_at": self.created_at,
            "collected_at": self.collected_at,
        }
