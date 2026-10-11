import streamlit as st
from config import (API_BASE, PRIORITY_RANK, PRIORITY_OPTIONS, STATUS_OPTIONS)
from api_client import load_cases, update_status
from ui import priority_pill, status_pill, field
from styles import CSS

st.set_page_config(page_title="Dispute Triage Queue", layout="wide", page_icon="⚖️")
st.markdown(CSS, unsafe_allow_html=True)


def open_case(case_id):
    st.session_state.selected = case_id


def back_to_queue():
    st.session_state.selected = None


def change_status_from_queue(case_id):
    new_status = st.session_state[f"status_{case_id}"]
    update_status(case_id, new_status)
    st.toast(f"{case_id} → {new_status}")


if "selected" not in st.session_state:
    st.session_state.selected = None


# ============ DETAIL VIEW ============
if st.session_state.selected:
    cases = load_cases()
    case = next((c for c in cases if c["case_id"] == st.session_state.selected), None)
    if case is None:
        back_to_queue()
        st.rerun()

    raw = case.get("raw_case") or {}

    st.button("← Back to queue", on_click=back_to_queue)

    # case id uses `inherit` so it is legible in light AND dark mode
    st.markdown(
        f"<div style='display:flex;align-items:center;gap:14px;margin:0.3rem 0 0.8rem'>"
        f"<span style='font-size:2.2rem;font-weight:700;color:inherit;line-height:1'>{case['case_id']}</span>"
        f"<span style='position:relative;top:1px'>{priority_pill(case.get('priority'), size='1rem')}</span>"
        f"</div>",
        unsafe_allow_html=True,
    )

    current = case.get("status") or "New"
    new_status = st.selectbox("Status", STATUS_OPTIONS, index=STATUS_OPTIONS.index(current))
    if new_status != current:
        update_status(case["case_id"], new_status)
        st.toast(f"Status → {new_status}")
        st.rerun()

    with st.container(border=True):
        st.subheader("Triage summary")
        st.write(case.get("summary") or "_No summary — this case needs manual review._")

    with st.container(border=True):
        st.subheader("Priority reasoning")
        st.write(case.get("reasoning") or "_None._")

    with st.container(border=True):
        st.subheader("Dispute details")
        c1, c2, c3 = st.columns(3)
        with c1:
            field("Reason code", f"{raw.get('reason_code','')} — {raw.get('reason_description','')}")
            field("Card network", raw.get("card_network"))
            field("Merchant", raw.get("merchant_name"))
        with c2:
            field("Disputed amount", f"{raw.get('currency','')} {raw.get('disputed_amount','')}")
            field("Transaction date", raw.get("transaction_date"))
            field("Response deadline", raw.get("response_deadline"))
        with c3:
            field("Customer ref", raw.get("customer_ref"))
            field("Prior disputes", raw.get("prior_disputes_by_customer"))
            field("Card", f"•••• {raw.get('card_last4','')}")

        st.markdown("**Customer claim**")
        st.info(raw.get("customer_claim") or "—")
        st.markdown("**Merchant notes**")
        st.warning(raw.get("merchant_notes") or "—")

        evidence = raw.get("evidence_available") or []
        if evidence:
            st.markdown("**Evidence available**")
            st.markdown("\n".join(f"- {e}" for e in evidence))

    with st.expander("Raw case data"):
        st.json(raw)


# ============ QUEUE VIEW ============
else:
    st.title("Dispute Triage Queue")

    f1, f2, f3 = st.columns([2, 2, 1], vertical_alignment="bottom")
    with f1:
        priority_filter = st.multiselect("Priority", PRIORITY_OPTIONS, default=[])
    with f2:
        status_filter = st.multiselect("Status", STATUS_OPTIONS, default=[])
    with f3:
        if st.button("🔄 Refresh", use_container_width=True):
            load_cases.clear()
            st.rerun()

    with st.spinner("Loading cases…"):
        cases = load_cases()

    if priority_filter:
        cases = [c for c in cases if c.get("priority") in priority_filter]
    if status_filter:
        cases = [c for c in cases if c.get("status") in status_filter]

    cases.sort(key=lambda c: PRIORITY_RANK.get(c.get("priority"), 3))
    st.caption(f"{len(cases)} cases in queue")

    for case in cases:
        with st.container(border=True):
            c1, c2 = st.columns([8, 1.3], vertical_alignment="center")
            with c1:
                st.markdown(
                    f"**{case['case_id']}** &nbsp; {priority_pill(case.get('priority'))} "
                    f"&nbsp; {status_pill(case.get('status'))}",
                    unsafe_allow_html=True,
                )
                st.write(case.get("summary") or "_Needs manual review_")
            with c2:
                st.button("Open", key=case["case_id"], on_click=open_case,
                          args=(case["case_id"],), use_container_width=True, type="primary")
                current = case.get("status") or "New"
                st.selectbox(
                    "Status", STATUS_OPTIONS,
                    index=STATUS_OPTIONS.index(current),
                    key=f"status_{case['case_id']}",
                    on_change=change_status_from_queue,
                    args=(case["case_id"],),
                    label_visibility="collapsed",
                )

