"""Streamlit presentation only; business operations go through the controller."""
from html import escape
from pathlib import Path

import streamlit as st

from controller import ParcelController
from repository import StorageError


PAGES = ["Home", "Register Parcel", "Collect Parcel", "Parcel Records", "Locker Status"]


def clear_flow():
    for key in ("registration", "verified_code", "collected", "pickup_code"):
        st.session_state.pop(key, None)


def navigate(page):
    clear_flow()
    st.session_state["page"] = page


def invalidate_code():
    st.session_state.pop("verified_code", None)
    st.session_state.pop("collected", None)


def home_button():
    st.button("Back to Home", on_click=navigate, args=("Home",), key="back_home")


def heading(text, centered=False):
    cls = ' class="center-title"' if centered else ''
    st.html(f"<h2{cls}>{escape(text)}</h2>")


def register_page(controller):
    heading("Register Parcel", True)
    with st.container(key="narrow_form"):
        with st.form("registration_form", border=False):
            name = st.text_input("Recipient name", placeholder="Enter recipient name", max_chars=100)
            contact = st.text_input("Recipient contact", placeholder="Enter phone number or email", max_chars=150)
            tracking = st.text_input("Tracking number", placeholder="Enter tracking number", max_chars=100)
            submitted = st.form_submit_button("Register Parcel", type="primary")
        if submitted:
            st.session_state.pop("registration", None)
            try:
                parcel = controller.register(name, contact, tracking)
                st.session_state["registration"] = parcel.to_dict()
            except (ValueError, StorageError) as error:
                st.error(str(error))
    if result := st.session_state.get("registration"):
        st.divider()
        with st.container(key="registration_result"):
            st.subheader("Parcel registered successfully.")
            st.write(f"Assigned locker: {result['locker_id']:02d}")
            st.write(f"Pickup code: {result['pickup_code']}")
            st.write("Notification preview: Your parcel is ready for collection.")
            st.caption("Preview only. No message sent.")
    with st.container(key="center_back"):
        home_button()


def collect_page(controller):
    heading("Collect Parcel", True)
    with st.container(key="narrow_form"):
        code = st.text_input("6-digit pickup code", key="pickup_code", max_chars=6,
                             placeholder="Enter pickup code", on_change=invalidate_code)
        if st.button("Verify Code", type="primary"):
            invalidate_code()
            try:
                controller.verify(code)
                st.session_state["verified_code"] = code.strip()
            except (ValueError, StorageError) as error:
                st.error(str(error))
    if verified := st.session_state.get("verified_code"):
        try:
            parcel = controller.verify(verified)
        except (ValueError, StorageError) as error:
            st.session_state.pop("verified_code", None)
            st.error(str(error))
        else:
            st.divider()
            with st.container(key="collection_result"):
                heading("Code verified", True)
                st.html(f'<p class="center-copy">Your parcel is in Locker {parcel.locker_id:02d}.</p>'
                        '<p class="center-copy">Please take your parcel and close the locker.</p>')
                if st.button("Confirm Collection", type="primary"):
                    try:
                        controller.collect(verified)
                        st.session_state.pop("verified_code", None)
                        st.session_state["collected"] = True
                        st.rerun()
                    except (ValueError, StorageError) as error:
                        st.error(str(error))
    if st.session_state.get("collected"):
        st.divider()
        with st.container(key="collection_result"):
            heading("Parcel collected successfully.", True)
            st.html('<p class="center-copy">The locker is available again.</p>')
    with st.container(key="center_back"):
        home_button()
    st.html('<p class="simulation-note">Locker opening is simulated.</p>')


def records_page(controller):
    heading("Parcel Records")
    st.html('<p class="page-description">Registered and collected parcels</p>')
    parcels = controller.parcels()
    if not parcels:
        st.info("No parcels registered yet. Use Register Parcel to add the first parcel.")
    else:
        rows = "".join(
            '<tr>' + ''.join(f'<td>{escape(str(value))}</td>' for value in (
                p.parcel_id, p.tracking_number, p.get_recipient_name(), f"{p.locker_id:02d}", p.status
            )) + '</tr>' for p in parcels
        )
        st.html('<div class="table-scroll"><table class="parcel-table"><caption class="sr-only">Parcel records</caption>'
                '<thead><tr><th scope="col">ID</th><th scope="col">Tracking number</th>'
                '<th scope="col">Recipient</th><th scope="col">Locker</th><th scope="col">Status</th></tr></thead>'
                f'<tbody>{rows}</tbody></table></div>')
        stored = sum(p.is_stored() for p in parcels)
        st.write(f"{len(parcels)} parcel records · {stored} stored · {len(parcels) - stored} collected")
    home_button()


def lockers_page(controller):
    heading("Locker Status")
    lockers = controller.lockers()
    available = sum(locker.is_available() for locker in lockers)
    st.html(f'<p class="locker-summary">Total: {len(lockers)} &nbsp; | &nbsp; Available: {available}'
            f' &nbsp; | &nbsp; Occupied: {len(lockers) - available}</p>')
    cards = ''.join(
        f'<div class="locker {"available" if locker.is_available() else "occupied"}">'
        f'<strong>Locker {locker.locker_id:02d}</strong><span>{escape(locker.get_status())}</span></div>'
        for locker in lockers
    )
    st.html(f'<div class="locker-grid">{cards}</div>')
    home_button()


def home_page():
    heading("Welcome", True)
    st.html('<p class="center-copy">Choose what you would like to do.</p>')
    with st.container(key="narrow_form"):
        st.button("Collect Parcel", type="primary", use_container_width=True,
                  on_click=navigate, args=("Collect Parcel",))
        st.divider()
        st.caption("Courier / Staff")
        for page in ("Register Parcel", "Parcel Records", "Locker Status"):
            st.button(page, use_container_width=True, on_click=navigate, args=(page,))


def run_app():
    st.set_page_config(page_title="Parcel Locker System", layout="wide", initial_sidebar_state="expanded")
    st.html(f"<style>{Path(__file__).with_name('styles.css').read_text(encoding='utf-8')}</style>")
    st.session_state.setdefault("page", "Home")
    with st.sidebar:
        st.subheader("Navigation")
        page = st.radio("Pages", PAGES, key="page", on_change=clear_flow, label_visibility="collapsed")
        st.divider()
        st.caption("Local demonstration")
    role = {"Register Parcel": "Courier", "Collect Parcel": "Customer",
            "Parcel Records": "Staff", "Locker Status": "Staff"}.get(page, "")
    st.html(f'<header class="app-header"><h1>Parcel Locker System</h1><span>{role}</span></header>')
    controller = ParcelController()
    try:
        if page == "Home":
            home_page()
        else:
            {"Register Parcel": register_page, "Collect Parcel": collect_page,
             "Parcel Records": records_page, "Locker Status": lockers_page}[page](controller)
    except StorageError as error:
        st.error(str(error))
    st.html('<footer class="app-footer">Local demo · Simulated locker operation</footer>')
