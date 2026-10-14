import secrets

import streamlit as st
from postgrest.exceptions import APIError
from supabase import create_client

from locker import Locker
from parcel import Parcel
from recipient import Recipient
from repository import StorageError


_USER_ERRORS = {
    "All fields are required.",
    "Enter a 6-digit pickup code.",
    "This tracking number is already registered.",
    "No available locker. The parcel cannot be registered.",
    "Invalid pickup code.",
    "This parcel has already been collected.",
    "The locker record does not match this parcel. Please contact staff.",
}


class ParcelController:
    def __init__(self):
        self._client = None

    # 从 Streamlit Secrets 读取连接配置
    # Read connection settings from Streamlit Secrets
    @property
    def db(self):
        if self._client is None:
            try:
                url = st.secrets["SUPABASE_URL"].strip()
                key = st.secrets["SUPABASE_SECRET_KEY"].strip()
                if not url or not key:
                    raise ValueError("Missing settings")
                self._client = create_client(url, key)
            except Exception:
                raise StorageError(
                    "Cannot initialize Supabase. Check SUPABASE_URL and "
                    "SUPABASE_SECRET_KEY in Streamlit Secrets."
                ) from None
        return self._client

    # 仅显示已知业务错误，避免显示密钥或个人资料
    # Show only known business errors without exposing secrets or personal data
    @staticmethod
    def _raise_error(error):
        message = getattr(error, "message", "")
        if getattr(error, "code", "") == "P0001" and message in _USER_ERRORS:
            raise ValueError(message) from None
        raise StorageError(
            "Supabase request failed. Check the connection, credentials, "
            "tables and functions. If you were saving, check Parcel Records "
            "before trying again; the operation may already have completed."
        ) from None

    def _execute(self, query):
        try:
            return query.execute().data
        except Exception as error:
            self._raise_error(error)

    # 将数据库记录转换为页面现有的包裹对象
    # Convert a database record into the parcel object used by the pages
    @staticmethod
    def _parcel(row):
        return Parcel(
            row["id"], row["tracking_number"],
            Recipient(row["recipient_name"], row["recipient_contact"]),
            row["locker_id"], row["pickup_code"], row["status"],
            row["created_at"], row["collected_at"],
        )

    @staticmethod
    def _code(code):
        code = code.strip()
        if len(code) != 6 or not code.isascii() or not code.isdigit():
            raise ValueError("Enter a 6-digit pickup code.")
        return code

    # 通过数据库函数完成存件，取件码碰撞时重新生成
    # Register through the database function and regenerate colliding pickup codes
    def register(self, name, contact, tracking):
        name, contact, tracking = (value.strip() for value in (name, contact, tracking))
        if not all((name, contact, tracking)):
            raise ValueError("All fields are required.")
        db = self.db
        for _ in range(10):
            params = {
                "p_name": name,
                "p_contact": contact,
                "p_tracking": tracking,
                "p_code": f"{secrets.randbelow(1_000_000):06d}",
            }
            try:
                row = db.rpc("register_parcel", params).execute().data
            except APIError as error:
                if error.code == "23505" and "parcels_pickup_code_key" in error.message:
                    continue
                self._raise_error(error)
            except Exception as error:
                self._raise_error(error)
            else:
                return self._parcel(row)
        raise StorageError("Could not generate a unique pickup code. Please try again.")

    # 验证取件码，每次读取数据库中的最新状态
    # Verify the pickup code against the latest database state
    def verify(self, code):
        code = self._code(code)
        rows = self._execute(
            self.db.table("parcels").select("*").eq("pickup_code", code).limit(1)
        )
        if not rows:
            raise ValueError("Invalid pickup code.")
        parcel = self._parcel(rows[0])
        if not parcel.is_stored():
            raise ValueError("This parcel has already been collected.")
        return parcel

    # 在同一个数据库事务中领取包裹并释放柜子
    # Collect the parcel and release the locker in one database transaction
    def collect(self, code):
        code = self._code(code)
        row = self._execute(self.db.rpc("collect_parcel", {"p_code": code}))
        return self._parcel(row)

    # 分页读取，避免记录超过接口返回上限时被截断
    # Read pages to avoid truncating records at the API response limit
    def _rows(self, table):
        rows = []
        while True:
            page = self._execute(
                self.db.table(table).select("*").order("id")
                .range(len(rows), len(rows) + 499)
            )
            if not page:
                return rows
            rows.extend(page)

    def parcels(self):
        return [self._parcel(row) for row in self._rows("parcels")]

    def lockers(self):
        return [
            Locker(row["id"], row["status"], row["parcel_id"])
            for row in self._rows("lockers")
        ]
