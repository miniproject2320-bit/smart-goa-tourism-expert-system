            use_container_width=True,
            hide_index=True
        )

        # Use the generated itinerary to suggest regional stays.
        if "run_result" in st.session_state:

            res = st.session_state["run_result"]

            if res.get("segments"):

                route_regions = list(
                    dict.fromkeys([
                        r for r, _ in res["segments"]
                    ])
                )

                st.markdown("### Stays along your itinerary")

                st.caption(
                    "Suggested regions: "
                    + " → ".join(route_regions)
                )

                stay_recs = recommend_stays(
                    stays,
                    res["budget"],
                    route_regions
                )

                if stay_recs.empty:

                    st.info(
                        "No stays matched the itinerary budget and regions."
                    )

                else:

                    cols = [
                        c for c in [
                            "name",
                            "type",
                            "region",
                            "area",
                            "budget_level",
                            "price_range_inr",
                            "nearest_airport",
                            "nearest_station",
                            "beach_access",
                            "family_friendly",
                            "wifi",
                            "notes"
                        ]
                        if c in stay_recs.columns
                    ]

                    st.dataframe(
                        stay_recs[cols],
                        use_container_width=True,
                        hide_index=True
                    )


# ============================================================
# TAB 5: TRAVEL TIPS
# ============================================================

with tabs[4]:

    st.markdown(
        '<div class="section-title">Helpful Goa travel tips</div>',
        unsafe_allow_html=True
    )

    tips = [
        (
            "🌤️ Check the season",
            "Goa's monsoon season can affect beach access, "
            "water activities and outdoor travel. "
            "Check local advisories before travelling."
        ),

        (
            "🛵 Choose transport carefully",
            "A scooter can be flexible for confident riders. "
            "Taxis or a hired car may be easier for families "
            "and longer journeys."
        ),

        (
            "🗺️ Check road routes",
            "The distances in this project are approximate. "
            "Open Google Maps for road directions and check traffic."
        ),

        (
            "💳 Confirm prices",
            "Entry fees, accommodation rates and transport fares "
            "can change. Confirm directly with providers."
        ),

        (
            "🤝 Travel responsibly",
            "Respect local communities, keep beaches clean, "
            "follow safety signs and avoid swimming in unsafe conditions."
        )
    ]

    for title, body in tips:

        with st.expander(title, expanded=True):

            st.write(body)

    st.divider()

    st.markdown("### About this project")

    st.write(
        "Goa Smart Tourism Expert System is an educational "
        "prototype that uses a supplied tourism knowledge base "
        "and explainable rule-based recommendations to help "
        "visitors discover Goa and plan regional itineraries."
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    f"🌴 Goa Smart Tourism Expert System · "
    f"{len(places)} attractions loaded · "
    f"Student project prototype. "
    f"Verify live conditions, prices, opening hours and transport "
    f"before travelling."
)
