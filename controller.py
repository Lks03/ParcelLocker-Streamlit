"""Coordinate each UI request against the latest saved model state."""
from threading import RLock

from system import ParcelLockerSystem


_LOCK = RLock()  # Serialize requests from sessions within one server process.


class ParcelController:
    def __init__(self, data_file=None):
        self.data_file = data_file

    def _system(self):
        return ParcelLockerSystem(self.data_file)

    def register(self, name, contact, tracking):
        with _LOCK:
            return self._system().register_parcel(name, contact, tracking)

    def verify(self, code):
        with _LOCK:
            return self._system().verify_pickup_code(code)

    def collect(self, code):
        with _LOCK:
            return self._system().collect_parcel(code)

    def parcels(self):
        with _LOCK:
            return self._system().get_parcels()

    def lockers(self):
        with _LOCK:
            return self._system().get_lockers()
