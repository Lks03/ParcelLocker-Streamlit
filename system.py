import os
import secrets
from pathlib import Path

from locker import Locker
from parcel import Parcel
from recipient import Recipient
from repository import ParcelRepository, StorageError


DATA_FILE = Path(__file__).with_name("data.json")
LOCKER_COUNT = 12


class ParcelLockerSystem:
    def __init__(self, data_file=None):
        self.repository = ParcelRepository(data_file or os.environ.get("PARCEL_LOCKER_DATA_FILE") or DATA_FILE)
        self.lockers = []
        self.parcels = []
        self.load_data()

    def load_data(self):
        data = self.repository.load()
        if data is None:
            self.lockers = [Locker(number) for number in range(1, LOCKER_COUNT + 1)]
            self.parcels = []
            return
        try:
            self._restore(data)
        except (KeyError, TypeError, ValueError, AttributeError) as error:
            raise StorageError("The saved records are invalid. Restore a valid data.json backup before continuing.") from error

    def _restore(self, data):

        self.lockers = [
            Locker(item["id"], item["status"], item["parcel_id"])
            for item in data["lockers"]
        ]
        self.parcels = []
        for item in data["parcels"]:
            recipient = Recipient(item["recipient_name"], item["recipient_contact"])
            parcel = Parcel(
                item["id"], item["tracking_number"], recipient, item["locker_id"],
                item["pickup_code"], item["status"], item["created_at"],
                item["collected_at"],
            )
            self.parcels.append(parcel)

    def save_data(self):
        data = {
            "lockers": [locker.to_dict() for locker in self.lockers],
            "parcels": [parcel.to_dict() for parcel in self.parcels],
        }
        self.repository.save(data)

    def find_available_locker(self):
        for locker in self.lockers:
            if locker.is_available():
                return locker
        return None

    def create_pickup_code(self):
        used_codes = {parcel.get_pickup_code() for parcel in self.parcels}
        while True:
            code = f"{secrets.randbelow(1_000_000):06d}"
            if code not in used_codes:
                return code

    def register_parcel(self, recipient_name, recipient_contact, tracking_number):
        recipient_name, recipient_contact, tracking_number = (
            value.strip() for value in (recipient_name, recipient_contact, tracking_number)
        )
        if not all((recipient_name, recipient_contact, tracking_number)):
            raise ValueError("All fields are required.")
        if any(p.tracking_number.casefold() == tracking_number.casefold() for p in self.parcels):
            raise ValueError("This tracking number is already registered.")
        locker = self.find_available_locker()
        if locker is None:
            raise ValueError("No available locker. The parcel cannot be registered.")

        recipient = Recipient(recipient_name, recipient_contact)
        parcel_id = max((p.parcel_id for p in self.parcels), default=0) + 1
        parcel = Parcel(
            parcel_id, tracking_number, recipient, locker.locker_id,
            self.create_pickup_code(),
        )
        self.parcels.append(parcel)
        locker.store_parcel(parcel_id)
        self.save_data()
        return parcel

    def find_parcel_by_code(self, pickup_code):
        for parcel in self.parcels:
            if parcel.get_pickup_code() == pickup_code:
                return parcel
        return None

    def find_locker(self, locker_id):
        for locker in self.lockers:
            if locker.locker_id == locker_id:
                return locker
        return None

    def verify_pickup_code(self, pickup_code):
        pickup_code = pickup_code.strip()
        if len(pickup_code) != 6 or not pickup_code.isascii() or not pickup_code.isdigit():
            raise ValueError("Enter a 6-digit pickup code.")
        parcel = self.find_parcel_by_code(pickup_code)
        if parcel is None:
            raise ValueError("Invalid pickup code.")
        if not parcel.is_stored():
            raise ValueError("This parcel has already been collected.")
        return parcel

    def collect_parcel(self, pickup_code):
        parcel = self.verify_pickup_code(pickup_code)
        locker = self.find_locker(parcel.locker_id)
        if locker is None or locker.parcel_id != parcel.parcel_id or locker.is_available():
            raise ValueError("The locker record does not match this parcel. Please contact staff.")

        parcel.collect()
        locker.release()
        self.save_data()
        return parcel

    def get_parcels(self):
        return self.parcels

    def get_lockers(self):
        return self.lockers
