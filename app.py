import streamlit as st
import random
import time
import pandas as pd
import streamlit.components.v1 as components

st.title("Trening tabliczki mnożenia – seria 10 przykładów")

# Inicjalizacja stanu
if "series" not in st.session_state:
    st.session_state.series = []
    st.session_state.current_index = 0
    st.session_state.start_time = None
    st.session_state.history = []
    st.session_state.running = False
    st.session_state.last_num = None

# Funkcja tworząca nową serię
def start_series(num: int):
    # Wszystkie mnożniki od 2 do 9 (8 przykładów)
    series = [(num, i) for i in range(2, 10)]
    # Dodajemy jeszcze 2 losowe, aby było razem 10
    series += [(num, random.randint(2, 9)) for _ in range(2)]
    random.shuffle(series)

    st.session_state.series = series
    st.session_state.current_index = 0
    st.session_state.history = []
    st.session_state.running = True
    st.session_state.start_time = None
    st.session_state.last_num = num

# Wybór cyfry i start
if not st.session_state.running:
    option = st.selectbox(
        "Wybierz cyfrę do treningu (2–9):",
        [str(i) for i in range(2, 10)]
    )

    if st.button("Start serii"):
        num = int(option)
        start_series(num)

# Główna logika – jeśli seria trwa
if st.session_state.running and st.session_state.current_index < len(st.session_state.series):
    a, b = st.session_state.series[st.session_state.current_index]
    st.write(f"Przykład {st.session_state.current_index+1} z {len(st.session_state.series)}")
    st.subheader(f"{a} × {b} = ?")

    if st.session_state.start_time is None:
        st.session_state.start_time = time.perf_counter()

    answer = st.text_input("Wpisz wynik:", key=f"answer_{st.session_state.current_index}")

    # Autofocus przez JS – zawsze ostatnie pole tekstowe
    components.html(
        """
        <script>
        const inputs = window.parent.document.querySelectorAll('input[type="text"]');
        if(inputs.length > 0) {
            inputs[inputs.length-1].focus();
        }
        </script>
        """,
        height=0,
    )

    if answer:
        try:
            ans = int(answer)
            correct = a * b
            if ans == correct:
                elapsed = time.perf_counter() - st.session_state.start_time
                st.success(f"Dobrze! Czas: {elapsed:.2f} sek.")
                st.session_state.history.append({
                    "Przykład": f"{a}×{b}",
                    "Odpowiedź": ans,
                    "Czas (sek)": round(elapsed, 2)
                })
                # Następny przykład
                st.session_state.current_index += 1
                st.session_state.start_time = None
                st.rerun()
            else:
                st.error("Źle, spróbuj jeszcze raz.")
        except ValueError:
            st.warning("Wpisz liczbę.")

# Po zakończeniu serii
if st.session_state.running and st.session_state.current_index >= len(st.session_state.series):
    st.success("Seria zakończona!")
    df = pd.DataFrame(st.session_state.history)
    st.dataframe(df, use_container_width=True)

    avg_time = df["Czas (sek)"].mean()
    st.markdown(f"**Średni czas dla całej serii:** {avg_time:.2f} sek.")

    # Statystyka wg mnożnika
    st.subheader("Średni czas dla poszczególnych mnożników")
    stats = []
    for i in range(2, 10):
        subset = df[df["Przykład"].str.contains(f"×{i}")]
        if not subset.empty:
            stats.append({"Mnożnik": i, "Średni czas (sek)": round(subset["Czas (sek)"].mean(), 2)})
    if stats:
        stats_df = pd.DataFrame(stats)
        st.dataframe(stats_df, use_container_width=True)

    # Przycisk powtórzenia serii
    if st.button("Powtórz serię"):
        start_series(st.session_state.last_num)
        st.rerun()

    st.session_state.running = False
