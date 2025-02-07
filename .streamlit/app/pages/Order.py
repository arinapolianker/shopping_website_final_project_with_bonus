import streamlit as st

get_jwt_token = st.session_state.functions['get_jwt_token']
user_id = st.session_state.get('user_id')

get_temp_order = st.session_state.functions['get_temp_order']
get_order_by_id = st.session_state.functions['get_order_by_id']
get_order_by_user_id = st.session_state.functions['get_order_by_user_id']
update_temp_order_quantities = st.session_state.functions['update_temp_order_quantities']
close_order = st.session_state.functions['close_order']
delete_item_from_order = st.session_state.functions['delete_item_from_order']

if "jwt_token" not in st.session_state or not st.session_state.jwt_token:
    st.warning("You must be logged in to view this page.")
    st.stop()

for key in ['order_quantities', 'temp_order', 'order_summary', 'order_placed']:
    if key not in st.session_state:
        st.session_state[key] = None

st.set_page_config(
    page_title="Order",
    page_icon="🛒",
    layout="wide",
)

st.title("My Orders🛍️")


def display_order_summary(order_summary):
    st.success("Your order has been placed! 🎉")
    st.markdown("### Order Summary")
    for summary_item in order_summary['item']:
        st.markdown(f"- **{summary_item['name']}**: {summary_item['quantity']} x ${summary_item['price']:.2f}")
    st.markdown(f"**Total Price:** ${order_summary['total_price']:.2f}")
    st.markdown(f"**Shipping Address:** {order_summary['shipping_address']}")
    st.markdown(f"**Order Number:** {order_summary['order_number']}")
    st.markdown(f"**Order Date:** {order_summary['order_date']}")


def display_pending_order(temp_order_data):
    if not temp_order_data.get('item'):
        st.session_state.temp_order = None
        st.session_state.total_price = 0.0
        st.session_state.order_quantities = {}
        return

    st.markdown("### 🟢 Pending Order Summary")
    total_price = 0.0

    for order_item in temp_order_data['item']:
        item_id = order_item['item_id']
        available_quantity = order_item['item_stock']
        quantity = st.session_state.order_quantities.get(str(item_id), order_item['quantity'])

        col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
        with col1:
            st.markdown(f"<span style='font-size:18px; font-weight:bold;'>{order_item['name']}</span>",
                        unsafe_allow_html=True)
        with col2:
            quantity_key = f"quantity_{item_id}"
            if quantity_key in st.session_state:
                new_quantity = st.session_state[quantity_key]
                if new_quantity != quantity and new_quantity <= available_quantity:
                    if new_quantity == 0:
                        delete_item_from_order(temp_order['id'], item_id)
                        st.session_state.order_quantities[str(item_id)] = 0
                        del st.session_state[quantity_key]
                        st.rerun()
                    else:
                        update_temp_order_quantities(user_id, item_id, new_quantity)
                        st.session_state.order_quantities[str(item_id)] = new_quantity
                        st.rerun()
            new_quantity = st.number_input(
                f"Quantity for {order_item['name']}",
                min_value=0,
                max_value=available_quantity,
                value=quantity,
                key=quantity_key,
                step=1,
            )

        with col3:
            item_total_price = order_item['price'] * new_quantity
            total_price += item_total_price
            st.markdown(f"**${item_total_price:.2f}**")
        with col4:
            if st.button(f"🗑️ Remove {order_item['name']}", key=f"remove_{item_id}"):
                delete_item_from_order(temp_order['id'], item_id)
                st.session_state.temp_order = get_temp_order(user_id)
                st.success(f"{order_item['name']} removed from your order!")
                st.rerun()
        st.markdown("---")

    st.markdown(f"### Total Price: ${total_price:.2f}")
    shipping_address = st.text_input("Shipping Address", value=temp_order_data['shipping_address'])

    if st.button("Place Order", type="primary"):
        if shipping_address:
            if shipping_address:
                insufficient_stock = []
                for order_item in temp_order_data['item']:
                    item_id = order_item['item_id']
                    requested_quantity = st.session_state.order_quantities.get(str(item_id), order_item['quantity'])
                    available_quantity = order_item['quantity']
                    if requested_quantity > available_quantity:
                        insufficient_stock.append(
                            f"{order_item['name']} (requested: {requested_quantity}, available: {available_quantity})")
                if insufficient_stock:
                    st.warning(
                        f"The following items have insufficient stock: {', '.join(insufficient_stock)}"
                    )
                else:
                    close_order(temp_order_data['id'], shipping_address, user_id)
                    finished_order = get_order_by_id(temp_order_data['id'])
                    st.session_state.update({
                        'order_summary': {
                            "item": finished_order['item'],
                            "total_price": finished_order['total_price'],
                            "shipping_address": shipping_address,
                            "order_date": finished_order['order_date'],
                            "order_number": finished_order['id'],
                        },
                        'temp_order': None,
                        'order_quantities': {},
                        'total_price': 0.0,
                        'order_placed': True,
                        'user_orders': get_order_by_user_id(user_id)
                    })
                    st.rerun()
        else:
            st.warning("Please provide a shipping address.")


try:
    temp_order = get_temp_order(user_id)
    user_orders = get_order_by_user_id(user_id)
except Exception as e:
    st.error(f"Error fetching items: {e}")
    temp_order = None
    user_orders = None

if st.session_state.get("order_summary"):
    display_order_summary(st.session_state['order_summary'])
    st.session_state["order_summary"] = None

if not temp_order or temp_order.get('status_code') == 404:
    st.info("Your cart order is currently empty.")
    st.session_state.temp_order = None
    st.session_state.order_quantities = {}
    st.session_state.total_price = 0.0
else:
    st.session_state['temp_order'] = temp_order
    st.session_state['order_quantities'] = temp_order.get('item_quantities', {})
    st.session_state.total_price = temp_order.get('total_price', 0.0)
    display_pending_order(temp_order)


st.markdown("### 🔵 Orders History")
if user_orders:
    for order in user_orders:
        if order['status'].upper() == 'CLOSE':
            with st.expander(f"Order #{order['id']} - {order['order_date']}"):
                for item in order['item']:
                    st.markdown(f"- **{item['name']}**: {item['quantity']} x ${item['price']:.2f}")
                st.markdown(f"**Total Price:** ${order['total_price']:.2f}")
                st.markdown(f"**Shipping Address:** {order['shipping_address']}")
else:
    st.info("You have no closed orders yet.")
