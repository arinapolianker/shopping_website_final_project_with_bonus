import pandas as pd
import streamlit as st


get_jwt_token = st.session_state.functions['get_jwt_token']
user_id = st.session_state.get('user_id')
get_user_data = st.session_state.functions['get_user_data']
predict_new_user = st.session_state.functions['predict_new_user']
get_performance_metrics = st.session_state.functions['get_performance_metrics']

if "jwt_token" not in st.session_state or not st.session_state.jwt_token:
    st.warning("You must be logged in to view this page.")
    st.stop()

st.set_page_config(
    page_title="Churn Prediction",
    page_icon="📊",
    layout="centered",
)

st.title("User Churn Prediction & Model Metrics 📊")

st.subheader("Data Overview")
data_path = "resources/csv/user_churn_data.csv"
df = pd.read_csv(data_path)
st.write("Here are the first 10 rows of the dataset:")
st.dataframe(df.head(10))

if st.button("Load Model Performance Metrics"):
    with st.spinner("Fetching performance metrics..."):
        metrics = get_performance_metrics()
        accuracy = metrics["accuracy"]
        recall = metrics["recall"]
        f1 = metrics["f1_score"]
        confusion = metrics["confusion_matrix"]

        st.write(f"**Accuracy Score:** {accuracy:.2%}")
        st.write(f"**Recall Score:** {recall:.2%}")
        st.write(f"**F1 Score:** {f1:.2%}")

        st.write("**Confusion Matrix:**")
        confusion_df = pd.DataFrame(
            confusion,
            columns=["Predicted: Stay", "Predicted: Churn"],
            index=["Actual: Stay", "Actual: Churn"]
        )
        st.dataframe(confusion_df)

st.subheader("Predict Churn for Current User")
if st.button("Predict Churn for Current User"):
    with st.spinner("Processing..."):
        jwt_token = st.session_state.get('jwt_token')
        response = get_user_data(user_id, jwt_token)

        if response.status_code == 200:
            prediction = response.json()
            churn_status = "Will Churn" if prediction["churn_prediction"] == 1 else "Will Stay"
            st.success(f"Prediction for your account: {churn_status}")
        else:
            st.error("Failed to fetch prediction.")

st.subheader("Predict Churn for a New User")
with st.form("predict_churn_form"):
    st.write("Enter the user data below:")
    total_orders = st.number_input("Total Orders", min_value=0, value=10)
    total_spent = st.number_input("Total Spent", min_value=0.0, value=100.0, format="%.2f")
    favorite_items_count = st.number_input("Favorite Items Count", min_value=0, value=5)
    avg_order_value = st.number_input("Average Order Value", min_value=0.0, value=10.0, format="%.2f")
    days_since_last_order = st.number_input("Days Since Last Order", min_value=0, value=30)
    submit_button = st.form_submit_button("Predict Churn")

if submit_button:
    with st.spinner("Processing new user prediction..."):
        user_features = {
            "total_orders": total_orders,
            "total_spent": total_spent,
            "favorite_items_count": favorite_items_count,
            "avg_order_value": avg_order_value,
            "days_since_last_order": days_since_last_order
        }
        response = predict_new_user(user_features)

        if response.status_code == 200:
            prediction = response.json()
            churn_status = "Will Churn" if prediction["churn_prediction"] == 1 else "Will Stay"
            st.success(f"Prediction for the new data: {churn_status}")
        else:
            st.error("Failed to fetch prediction for the new data.")
