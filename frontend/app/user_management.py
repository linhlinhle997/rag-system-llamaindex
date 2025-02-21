import os

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
API_URL = os.getenv("BACKEND_URL")


def show(selectbox_key):
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if "access_token" not in st.session_state:
        st.session_state.access_token = None

    if "refresh_token" not in st.session_state:
        st.session_state.refresh_token = None

    col_1, col_2 = st.columns([1, 1])
    with col_1:
        login()
    with col_2:
        create_user()

    st.markdown("---")

    if st.session_state.logged_in:
        logout()
        st.markdown("---")
        get_user()
        st.markdown("---")
        get_users()
        st.markdown("---")
        update_user()
        st.markdown("---")
        delete_user()


def login():
    st.subheader("Login")

    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login"):
        try:
            response = requests.post(
                f"{API_URL}/auth/login",
                json={"email": email, "password": password},
                timeout=10,
            )
            data = response.json()
            if response.status_code == 200:
                st.session_state.logged_in = True
                st.session_state.access_token = data.get("access_token")
                st.session_state.refresh_token = data.get("refresh_token")
                st.success("Login successull!")
            else:
                st.error(f"Error: {data.get('detail', 'Invalid credentials')}")
        except requests.exceptions.RequestException as e:
            st.error(f"Network errpr: {str(e)}")


def refresh_access_token():
    if not st.session_state.refresh_token:
        return None
    try:
        response = requests.post(
            f"{API_URL}/auth/refresh",
            json={"refresh_token": st.session_state.refresh_token},
            timeout=10,
        )
        data = response.json()

        if response.status_code == 200:
            st.session_state.access_token = data.get("access_token")
            return st.session_state.access_token
        else:
            st.session_state.logged_in = False
            st.session_state.access_token = None
            st.session_state.refresh_token = None
            st.error("Session expired, please login again.")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Network error: {str(e)}")
        return None


def logout():
    if not st.session_state.get("logged_in"):
        st.error("You need to login first")
        return

    st.subheader("Logout")
    if st.button("Logout"):
        try:
            response = requests.post(
                f"{API_URL}/auth/logout",
                json={"refresh_token": st.session_state.refresh_token},
                timeout=10,
            )
            if response.status_code == 200:
                st.success("Logout successful!")
            else:
                st.warning(
                    f"Logout failed: {response.json().get('detail', 'Unknown error')}"
                )
        except requests.exceptions.RequestException as e:
            st.warning(f"Network error while logging out {str(e)}, clearing session")

        st.session_state.logged_in = False
        st.session_state.access_token = None
        st.session_state.refresh_token = None


def get_user():
    if not st.session_state.logged_in:
        st.error("You need to login first")
        return

    st.subheader("Get User")
    email = st.text_input("Email", key="get_user_email")

    if st.button("Get User"):
        headers = {"Authorization": f"Bearer {st.session_state.access_token}"}

        try:
            response = requests.get(
                f"{API_URL}/user/get_user?email={email}", headers=headers, timeout=10
            )

            if response.status_code == 200:
                user = response.json()
                st.write(user)

            else:
                st.error("An error occurred while fetching the user details.")
        except requests.exceptions.RequestException as e:
            st.error(f"Network error: {str(e)}")


def get_users():
    if not st.session_state.logged_in:
        st.error("You need to login first")
        return

    st.subheader("Get Users")
    if st.button("Get Users"):
        headers = {"Authorization": f"Bearer {st.session_state.access_token}"}

        try:
            response = requests.get(
                f"{API_URL}/user/get_users", headers=headers, timeout=10
            )

            if response.status_code == 200:
                users = response.json()
                st.write(users)
            else:
                st.error("An error occurred while getting the users.")
        except requests.exceptions.RequestException as e:
            st.error(f"Network error: {str(e)}")


def update_user():
    if not st.session_state.logged_in:
        st.error("You need to login first")
        return

    st.subheader("Update User")

    email = st.text_input("Email", key="update_user_email")
    username = st.text_input("Username", key="update_user_username")
    password = st.text_input("Password", type="password", key="update_user_password")

    if st.button("Update User"):
        headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
        data = {"username": username, "email": email, "password": password}

        try:
            response = requests.put(
                f"{API_URL}/user/update_user", json=data, headers=headers, timeout=10
            )

            if response.status_code == 200:
                st.success("User updated successfully!")
                st.write(response.json())
            else:
                st.error("An error occurred while updating the user")
        except requests.exceptions.RequestException as e:
            st.error(f"Network error: {str(e)}")


def create_user():
    st.subheader("Create User")

    username = st.text_input("Username", key="create_user_username")
    email = st.text_input("Email", key="create_user_email")
    password = st.text_input("Password", type="password", key="create_user_password")

    if st.button("Create User"):
        try:
            response = requests.post(
                f"{API_URL}/user/create_user",
                json={"username": username, "email": email, "password": password},
                timeout=10,
            )
            data = response.json()

            if response.status_code == 200:
                st.success("User created successfully!")
                st.write(data)
            else:
                st.error(f"Error: {data.get('detail', 'Unknown error')}")
        except requests.exceptions.RequestException as e:
            st.error(f"Network error: {str(e)}")


def delete_user():
    if not st.session_state.logged_in:
        st.error("You need to login first")
        return

    st.subheader("Delete User")
    email = st.text_input("Email", key="delete_user_email")

    if st.button("Delete User"):
        headers = {"Authorization": f"Bearer {st.session_state.access_token}"}

        try:
            response = requests.delete(
                f"{API_URL}/user/delete_user?email={email}", headers=headers, timeout=10
            )

            if response.status_code == 200:
                st.success("User deleted successfully!")
            else:
                st.error("An error occurred while deleting the user")
        except requests.exceptions.RequestException as e:
            st.error(f"Network error: {str(e)}")
