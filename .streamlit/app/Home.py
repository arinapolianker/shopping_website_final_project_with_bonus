import streamlit as st

from api.api import get_all_items, register_user, get_jwt_token, add_item_to_favorite_items, \
    get_favorite_items_by_user_id, delete_favorite_item, create_order, close_order, \
    delete_item_from_order, get_temp_order, update_temp_order_quantities, \
    get_user, get_order_by_id, delete_user_by_id, logout_user, get_order_by_user_id, fetch_filtered_items, \
    get_user_data, get_performance_metrics, predict_new_user

st.set_page_config(
    page_title="Speakers Web-Shop",
    page_icon="🎧",
    layout="wide",
)

if 'functions' not in st.session_state:
    st.session_state.functions = {
        'register_user': register_user,
        'get_jwt_token': get_jwt_token,
        'get_user': get_user,
        'logout_user': logout_user,
        'delete_user_by_id': delete_user_by_id,
        'get_all_items': get_all_items,
        'add_item_to_favorite_items': add_item_to_favorite_items,
        'get_favorite_items_by_user_id': get_favorite_items_by_user_id,
        'delete_favorite_item': delete_favorite_item,
        'create_order': create_order,
        'update_temp_order_quantities': update_temp_order_quantities,
        'get_order_by_id': get_order_by_id,
        'get_order_by_user_id': get_order_by_user_id,
        'get_temp_order': get_temp_order,
        'close_order': close_order,
        'delete_item_from_order': delete_item_from_order,
        'get_user_data': get_user_data,
        'get_performance_metrics': get_performance_metrics,
        'predict_new_user': predict_new_user
    }

if 'jwt_token' not in st.session_state:
    st.session_state.jwt_token = None
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'order_quantities' not in st.session_state:
    st.session_state.order_quantities = {}


st.title("Welcome to the Speakers Web-Shop!")

try:
    items = get_all_items()
except Exception as e:
    st.error(f"Error fetching items: {e}")
    items = []

st.markdown("## 🔍 Search Products")
search_col1, search_col2 = st.columns([8, 1])

with search_col1:
    search_by_name = st.text_input(
        "Search products",
        placeholder="Enter product names (separate multiple terms with commas)...",
        label_visibility="collapsed"
    )

with search_col2:
    if st.button("Clear🔄", use_container_width=True, type="secondary"):
        search_by_name = ""

col1, col2 = st.columns(2)
with col1:
    price_filter = st.slider("Filter by Price", 0, 500, (0, 500))
with col2:
    stock_filter = st.slider("Filter by Stock", 0, 100, (0, 100))

adv_price_operator = "None"
adv_price_value = 0.0
adv_stock_operator = "None"
adv_stock_value = 0

search_terms = [term.strip() for term in search_by_name.split(",")]

for term in search_terms:
    parts = term.split()
    if len(parts) == 3:
        keyword, operator, value = parts[0], parts[1], parts[2]

        if keyword in ["price"]:
            if operator in [">", "<", "="] and value.replace(".", "", 1).isdigit():
                adv_price_operator, adv_price_value = operator, float(value)

        elif keyword in ["stock", "amount"]:
            if operator in [">", "<", "="] and value.isdigit():
                adv_stock_operator, adv_stock_value = operator, int(value)

filtered_items = fetch_filtered_items(
    name=search_by_name,
    stock_filter=(adv_stock_operator, adv_stock_value) if adv_stock_operator != "None" else None,
    price_filter=(adv_price_operator, adv_price_value) if adv_price_operator != "None" else None,
)

filtered_items = [
    item for item in filtered_items
    if (price_filter[0] <= item["price"] <= price_filter[1]) and
       (stock_filter[0] <= item["item_stock"] <= stock_filter[1])
]

if filtered_items:
    st.markdown("### Available Items")
    num_columns = 4
    rows = [st.columns(num_columns) for _ in range((len(items) + num_columns - 1) // num_columns)]

    for i, item in enumerate(filtered_items):
        row_idx = i // num_columns
        col_idx = i % num_columns
        with rows[row_idx][col_idx]:
            with st.container():
                st.markdown("---")
                st.markdown(f"**{item['name']}**")
                st.markdown(f"<h4 style='color: #2E86C1;'>Price: ${item['price']:.2f}</h4>", unsafe_allow_html=True)
                if item['item_stock'] > 0:
                    st.markdown(f"**Stock:** :green[{item['item_stock']} available]")
                else:
                    st.markdown("**Stock:** :red[Out of stock]")
                col1, col2 = st.columns(2)

                with col1:
                    if st.button("Add to order🛒", key=f"order_{i}", use_container_width=True, disabled=item['item_stock'] == 0):
                        if 'jwt_token' in st.session_state and st.session_state['jwt_token']:
                            user_id = st.session_state.get("user_id")
                            temp_order = get_temp_order(user_id)
                            st.session_state["order_summary"] = None
                            if item["item_stock"] == 0:
                                st.warning(f"Can't add '{item['name']}' to order, Item sold out.")
                            else:
                                if not temp_order or "item" not in temp_order:
                                    shipping_address = st.session_state.get("user_address", "Default Address")
                                    item_quantities = {item["id"]: 1}
                                    total_price = sum(
                                        item["price"] * quantity for item_id, quantity in item_quantities.items())
                                    create_order(user_id, shipping_address, item_quantities, total_price, 'TEMP')
                                    st.session_state.order_quantities = item_quantities
                                    st.success(f"{item['name']} added to your order!")

                                else:
                                    existing_item = {order_item["item_id"] for order_item in temp_order["item"]}
                                    item_id = item["id"]
                                    if item_id in existing_item:
                                        item_quantities = {order_item["item_id"]: order_item["quantity"] for order_item in
                                                           temp_order["item"]}
                                        current_quantity = item_quantities.get(item_id, 0)
                                        new_quantity = current_quantity + 1
                                        if new_quantity > item["item_stock"]:
                                            st.warning(
                                                f"Cannot add more '{item['name']}' to your order. Only {item['item_stock']} are available.")
                                        else:
                                            update_temp_order_quantities(user_id, item_id, new_quantity)
                                            st.success(f"'{item['name']}' quantity updated in your order!")
                                    else:
                                        update_temp_order_quantities(user_id, item_id, 1)
                                        st.success(f"'{item['name']}' added to your order!")
                        else:
                            st.warning("Please log in to add items to your order.")

                with col2:
                    if st.button("Add to favorites❤️", key=f"favorite_{i}", use_container_width=True):
                        if 'jwt_token' in st.session_state and st.session_state['jwt_token']:
                            user_id = st.session_state.get("user_id")
                            favorite_items = get_favorite_items_by_user_id(user_id)

                            if any(favorite_item['item']['id'] == item['id'] for favorite_item in favorite_items):
                                st.error(f"You already added '{item['name']}' to your favorite item list")
                            else:
                                add_item_to_favorite_items(user_id, item['id'])
                                st.success(f"{item['name']} was Added to favorite items!")
                                st.session_state["favorite_items_updated"] = True
                        else:
                            st.warning("Please log in to add items to your favorites list.")
                st.markdown("---")
else:
    st.warning("No items available.")
