class Locker:
    def __init__(self, locker_id, status="Available", parcel_id=None):
        self.locker_id = locker_id
        self.status = status
        self.parcel_id = parcel_id

    def is_available(self):
        return self.status == "Available"

    def store_parcel(self, parcel_id):
        if not self.is_available():
            raise ValueError("This locker is already occupied.")
        self.status = "Occupied"
        self.parcel_id = parcel_id

    def release(self):
        self.status = "Available"
        self.parcel_id = None

    def get_status(self):
        return self.status

    def to_dict(self):
        return {
            "id": self.locker_id,
            "status": self.status,
            "parcel_id": self.parcel_id,
        }
