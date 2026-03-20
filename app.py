import streamlit as st
from datetime import datetime, timedelta
from src.storage import (
    load_workouts, add_workout, update_workout, delete_workout,
    get_workouts_by_date, get_month_workouts
)
from src.calendar_utils import get_month_calendar, get_month_name, get_weekday_names


# --- UI setup ---
st.set_page_config(
    page_title="Planer Treningowy",
    layout="wide"
)

st.title("📅 Planer Treningowy")

# --- Session State ---
if "current_date" not in st.session_state:
    st.session_state.current_date = datetime.now().date()

if "selected_date" not in st.session_state:
    st.session_state.selected_date = None

if "show_modal" not in st.session_state:
    st.session_state.show_modal = False

if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False

if "edit_id" not in st.session_state:
    st.session_state.edit_id = None

if "current_tab" not in st.session_state:
    st.session_state.current_tab = "Kalendarz"


def get_intensity_color(intensity: str) -> str:
    """Zwraca kolor dla intensywności"""
    colors = {
        "niska": "🟢",
        "średnia": "🟡",
        "wysoka": "🔴"
    }
    return colors.get(intensity.lower(), "⚪")


def get_status_icon(status: str) -> str:
    """Zwraca ikonę dla statusu"""
    if status == "ukończony":
        return "✅"
    return "📋"


def open_modal(date, edit_id=None):
    """Otwiera modal do dodawania/edycji treningu"""
    st.session_state.show_modal = True
    st.session_state.selected_date = date
    st.session_state.edit_id = edit_id
    st.session_state.edit_mode = edit_id is not None


def close_modal():
    """Zamyka modal"""
    st.session_state.show_modal = False
    st.session_state.selected_date = None
    st.session_state.edit_id = None
    st.session_state.edit_mode = False


def render_modal():
    """Renderuje modal do dodawania/edycji treningu"""
    if not st.session_state.show_modal:
        return
    
    st.divider()
    
    if st.session_state.edit_mode:
        workouts = load_workouts()
        edited_workout = next((w for w in workouts if w["id"] == st.session_state.edit_id), None)
        st.subheader("✏️ Edycja treningu")
    else:
        edited_workout = None
        st.subheader(f"➕ Dodaj trening na {st.session_state.selected_date}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        name = st.text_input(
            "Nazwa treningu",
            value=edited_workout.get("name", "") if edited_workout else "",
            key="modal_name"
        )
        
        workout_type = st.selectbox(
            "Typ treningu",
            ["Bieg - spokojny", "Bieg - regeneracyjny", "Bieg - tempo", "Bieg - sprinty", "Bieg - zawody", "Siłownia", "Rozciąganie", "Rollowanie", "Rozciąganie+rollowanie", "Rower", "Pływanie", "Inne"],
            index=0 if not edited_workout else ["Bieg - spokojny", "Bieg - regeneracyjny", "Bieg - tempo", "Bieg - sprinty", "Bieg - zawody", "Siłownia", "Rozciąganie", "Rollowanie", "Rozciąganie+rollowanie", "Rower", "Pływanie", "Inne"].index(edited_workout.get("type", "Inne")),
            key="modal_type"
        )
        
        duration = st.number_input(
            "Czas trwania (minuty)",
            min_value=5,
            max_value=360,
            value=edited_workout.get("duration", 60) if edited_workout else 60,
            step=5,
            key="modal_duration"
        )
    
    with col2:
        intensity_options = ["Niska", "Średnia", "Wysoka"]
        intensity_key_map = {"niska": 0, "średnia": 1, "wysoka": 2}
        current_intensity_index = 0
        
        if edited_workout:
            stored_intensity = edited_workout.get("intensity", "średnia").lower()
            current_intensity_index = intensity_key_map.get(stored_intensity, 1)
        
        intensity = st.selectbox(
            "Intensywność",
            intensity_options,
            index=current_intensity_index,
            key="modal_intensity"
        )
        
        status = st.selectbox(
            "Status",
            ["Zaplanowany", "Ukończony"],
            index=0 if not edited_workout else (1 if edited_workout.get("status") == "ukończony" else 0),
            key="modal_status"
        )
        
        date_input = st.date_input(
            "Data",
            value=st.session_state.selected_date,
            key="modal_date"
        )
    
    notes = st.text_area(
        "Notatki",
        value=edited_workout.get("notes", "") if edited_workout else "",
        height=100,
        key="modal_notes"
    )
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("💾 Zapisz", use_container_width=True):
            if not name:
                st.error("Wprowadź nazwę treningu")
                return
            
            date_str = date_input.strftime("%Y-%m-%d")
            
            if st.session_state.edit_mode:
                update_workout(
                    st.session_state.edit_id,
                    name=name,
                    type=workout_type,
                    duration=int(duration),
                    intensity=intensity.lower(),
                    date=date_str,
                    status=status.lower(),
                    notes=notes
                )
                st.success("✅ Trening zaktualizowany!")
            else:
                add_workout(
                    name=name,
                    workout_type=workout_type,
                    duration=int(duration),
                    intensity=intensity.lower(),
                    date=date_str,
                    status=status.lower(),
                    notes=notes
                )
                st.success("✅ Trening dodany!")
            
            close_modal()
            st.rerun()
    
    with col2:
        if st.button("❌ Anuluj", use_container_width=True):
            close_modal()
            st.rerun()
    
    if st.session_state.edit_mode:
        with col3:
            if st.button("🗑️ Usuń trening", use_container_width=True):
                delete_workout(st.session_state.edit_id)
                st.success("✅ Trening usunięty!")
                close_modal()
                st.rerun()


def render_calendar():
    """Renderuje kalendarz miesiąca"""
    col_nav1, col_nav2, col_nav3 = st.columns([1, 2, 1])
    
    current_year = st.session_state.current_date.year
    current_month = st.session_state.current_date.month
    
    with col_nav1:
        if st.button("⬅️ Poprzedni miesiąc", use_container_width=True, key="prev_month_btn"):
            if current_month == 1:
                st.session_state.current_date = datetime(current_year - 1, 12, 1).date()
            else:
                st.session_state.current_date = datetime(current_year, current_month - 1, 1).date()
            st.rerun()
    
    with col_nav2:
        month_name = get_month_name(current_month)
        
        col_center1, col_center2 = st.columns(2)
        with col_center1:
            selected_month = st.selectbox(
                "Miesiąc",
                range(1, 13),
                index=current_month - 1,
                format_func=lambda x: get_month_name(x),
                key="select_month"
            )
        
        with col_center2:
            selected_year = st.selectbox(
                "Rok",
                range(2020, 2030),
                index=min(current_year - 2020, 9),
                key="select_year"
            )
        
        if selected_month != current_month or selected_year != current_year:
            st.session_state.current_date = datetime(selected_year, selected_month, 1).date()
            st.rerun()
    
    with col_nav3:
        if st.button("Następny miesiąc ➡️", use_container_width=True, key="next_month_btn"):
            if current_month == 12:
                st.session_state.current_date = datetime(current_year + 1, 1, 1).date()
            else:
                st.session_state.current_date = datetime(current_year, current_month + 1, 1).date()
            st.rerun()
    
    st.markdown(f"### {month_name} {current_year}")
    
    # Pobranie treningów na miesiąc
    month_workouts = get_month_workouts(current_year, current_month)
    
    # Nagłówki dni tygodnia
    weekdays = get_weekday_names()
    col_headers = st.columns(7)
    for i, day_name in enumerate(weekdays):
        with col_headers[i]:
            st.markdown(f"**{day_name}**")
    
    # Kalendarz
    calendar_grid = get_month_calendar(current_year, current_month)
    
    for week in calendar_grid:
        cols = st.columns(7)
        for col_idx, (day, date_str) in enumerate(week):
            with cols[col_idx]:
                if day == 0:
                    st.markdown("")
                else:
                    # Kontener na dzień
                    with st.container(border=True):
                        day_header = f"**{day}**"
                        st.markdown(day_header)
                        
                        # Treningi na ten dzień
                        day_workouts = month_workouts.get(date_str, [])
                        
                        if day_workouts:
                            for workout in day_workouts:
                                icon = get_status_icon(workout.get("status", "zaplanowany"))
                                intensity_icon = get_intensity_color(workout.get("intensity", "średnia"))
                                
                                workout_text = f"{icon} {intensity_icon}\n{workout['name'][:15]}"
                                if len(workout['name']) > 15:
                                    workout_text += "..."
                                
                                col_btn1, col_btn2 = st.columns([3, 1])
                                
                                with col_btn1:
                                    st.markdown(f"<small>{workout_text}</small>", unsafe_allow_html=True)
                                
                                with col_btn2:
                                    if st.button("📝", key=f"edit_{workout['id']}", help="Edytuj", use_container_width=True):
                                        open_modal(date_str, edit_id=workout['id'])
                                        st.rerun()
                                
                                st.markdown(f"<small>{workout.get('duration', 0)}min</small>", unsafe_allow_html=True)
                                st.markdown(f"<small>{workout.get('notes', '')}</small>", unsafe_allow_html=True)
                        
                        # Przycisk dodawania treningu
                        if st.button("➕", key=f"add_{date_str}", use_container_width=True):
                            open_modal(date_str)
                            st.rerun()


# --- Main App ---
st.divider()

# Zakładki
tab_calendar, tab_stats = st.tabs(["📅 Kalendarz", "📊 Statystyki"])

with tab_calendar:
    render_calendar()
    render_modal()

with tab_stats:
    st.subheader("📊 Statystyki treningów")
    
    all_workouts = load_workouts()
    
    if not all_workouts:
        st.info("Brak danych o treningach. Dodaj swoje pierwsze treningi!")
    else:
        # Statystyki ogólne
        col1, col2, col3, col4 = st.columns(4)
        
        completed = len([w for w in all_workouts if w.get("status") == "ukończony"])
        planned = len([w for w in all_workouts if w.get("status") == "zaplanowany"])
        total_duration = sum(w.get("duration", 0) for w in all_workouts)
        
        with col1:
            st.metric("✅ Ukończone", completed)
        with col2:
            st.metric("📋 Zaplanowane", planned)
        with col3:
            st.metric("⏱️ Łączny czas", f"{total_duration} min")
        with col4:
            if completed + planned > 0:
                completion_rate = (completed / (completed + planned)) * 100
                st.metric("🎯 Realizacja", f"{completion_rate:.0f}%")
        
        st.divider()
        
        # Rozkład po typach treningów
        st.subheader("Treningi wg typów")
        types = {}
        for w in all_workouts:
            t = w.get("type", "Inne")
            types[t] = types.get(t, 0) + 1
        
        if types:
            type_col1, type_col2 = st.columns(2)
            with type_col1:
                for type_name, count in sorted(types.items(), key=lambda x: x[1], reverse=True):
                    st.write(f"{type_name}: **{count} treningów**")
            
            with type_col2:
                # Najczęstszy typ
                favorite = max(types, key=types.get)
                st.write(f"**Ulubiony typ:** {favorite} ({types[favorite]} treningów)")
        
        st.divider()
        
        # Rozkład po intensywnościach
        st.subheader("Rozkład intensywności")
        intensities = {}
        intensity_icons = {"niska": "🟢", "średnia": "🟡", "wysoka": "🔴"}
        
        for w in all_workouts:
            i = w.get("intensity", "średnia")
            intensities[i] = intensities.get(i, 0) + 1
        
        if intensities:
            int_col1, int_col2, int_col3 = st.columns(3)
            
            with int_col1:
                low_count = intensities.get("niska", 0)
                st.write(f"🟢 **Niska**: {low_count}")
            
            with int_col2:
                med_count = intensities.get("średnia", 0)
                st.write(f"🟡 **Średnia**: {med_count}")
            
            with int_col3:
                high_count = intensities.get("wysoka", 0)
                st.write(f"🔴 **Wysoka**: {high_count}")