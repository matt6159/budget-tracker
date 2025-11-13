import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import os
from dotenv import load_dotenv

# Załaduj zmienne środowiskowe
load_dotenv()

# Konfiguracja Groq API (bezpieczne - z .env)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

if not GROQ_API_KEY:
    st.error("⚠️ Brak klucza Groq API! Ustaw zmienną GROQ_API_KEY w pliku .env")

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# Inicjalizacja session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'transactions' not in st.session_state:
    st.session_state.transactions = []
if 'next_id' not in st.session_state:
    st.session_state.next_id = 1


# Funkcja AI - kategoryzacja z Groq Llama 3.3 70B
def categorize_with_ai(description):
    """
    Kategoryzacja z Groq Llama 3.3 70B - prawdziwe AI
    Fallback do smart logic jeśli API niedostępne
    """
    try:
        # Wywołaj Groq API
        response = requests.post(
            GROQ_URL,
            headers={
                'Authorization': f'Bearer {GROQ_API_KEY}',
                'Content-Type': 'application/json'
            },
            json={
                'model': 'llama-3.3-70b-versatile',
                'messages': [
                    {
                        'role': 'system',
                        'content': 'Jesteś ekspertem kategoryzacji wydatków domowych. Odpowiadasz TYLKO jednym słowem z listy: Jedzenie, Transport, Rozrywka, Dom, Zdrowie lub Inne. Rozumiesz kontekst i polskie nazwy produktów.'
                    },
                    {
                        'role': 'user',
                        'content': f'Skategoryzuj wydatek: "{description}"'
                    }
                ],
                'temperature': 0.3,
                'max_tokens': 10
            },
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            category = result['choices'][0]['message']['content'].strip()
            
            # Walidacja kategorii
            valid_categories = ["Jedzenie", "Transport", "Rozrywka", "Dom", "Zdrowie", "Inne"]
            
            for valid_cat in valid_categories:
                if valid_cat.lower() in category.lower():
                    print(f"✅ Groq AI: '{description}' -> '{valid_cat}'")
                    return valid_cat
            
            # Jeśli nie rozpoznano - fallback
            print(f"⚠️ Groq unclear: '{category}' - używam fallback")
            return smart_categorize(description)
        else:
            print(f"❌ Groq API error: {response.status_code}")
            return smart_categorize(description)
            
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Groq niedostępne: {e} - używam fallback")
        return smart_categorize(description)
    except Exception as e:
        print(f"❌ Error: {e}")
        return smart_categorize(description)


def smart_categorize(description):
    """
    Fallback kategoryzacja - działa gdy AI niedostępne
    Rules-based algorithm z pattern matching
    """
    description_lower = description.lower()
    
    # Rozbudowany słownik kategorii (100+ wzorców)
    categories = {
        'Jedzenie': [
            # Sklepy
            'biedronka', 'lidl', 'kaufland', 'auchan', 'carrefour', 'tesco',
            'żabka', 'zabka', 'lewiatan', 'delikatesy', 'market', 'sklep spożywczy',
            # Restauracje
            'restauracja', 'mcdonald', 'kfc', 'pizza', 'kebab', 'burger king',
            'subway', 'sushi', 'bar mleczny', 'bistro', 'food', 'jedzenie',
            # Inne
            'piekarnia', 'cukiernia', 'kawiarnia', 'cafe', 'costa', 'starbucks',
            # Produkty
            'chleb', 'bułka', 'bulka', 'mleko', 'ser', 'masło', 'maslo',
            'mięso', 'mieso', 'wędlina', 'wedlina', 'owoce', 'warzywa'
        ],
        'Transport': [
            # Paliwo
            'orlen', 'bp', 'shell', 'lotos', 'circle k', 'station', 'paliwo', 
            'benzyna', 'diesel', 'lpg',
            # Transport publiczny
            'mpk', 'ztm', 'pkp', 'koleje', 'intercity', 'bilet', 'przejazd',
            'autobus', 'tramwaj', 'metro', 'skm', 'pkm',
            # Taxi i inne
            'uber', 'bolt', 'free now', 'taxi', 'parking', 'parkomat',
            'myjnia', 'warsztat', 'auto', 'mechanik'
        ],
        'Rozrywka': [
            # Streaming
            'netflix', 'spotify', 'hbo', 'disney', 'apple tv', 'prime video',
            'youtube premium', 'tidal',
            # Kino/teatr
            'cinema city', 'multikino', 'helios', 'kino', 'teatr', 'opera',
            'filharmonia', 'koncert', 'festiwal',
            # Gry
            'steam', 'playstation', 'xbox', 'nintendo', 'epic games', 'gog',
            # Inne
            'empik', 'książka', 'muzeum', 'galeria', 'zoo', 'aquapark',
            'escape room', 'bowling', 'bilard'
        ],
        'Dom': [
            # Meble/AGD
            'ikea', 'agata', 'black red white', 'jysk', 'home&you',
            'media markt', 'mediamarkt', 'rtv euro', 'euro agd', 'electro',
            'saturn', 'komputronik', 'x-kom', 'morele',
            # Budowa/remont
            'obi', 'castorama', 'leroy merlin', 'bricomarche', 'budmat',
            'narzędzia', 'narzedzia', 'farby', 'cement', 'remont',
            # Media/rachunki
            'czynsz', 'energia', 'tauron', 'pge', 'enea', 'energa',
            'gaz', 'pgnig', 'woda', 'mpwik', 'wodociągi', 'wodociagi',
            # Telekomunikacja
            'orange', 'play', 'plus', 't-mobile', 'netia', 'vectra',
            'internet', 'abonament', 'telefon', 'komórka', 'komorka'
        ],
        'Zdrowie': [
            # Apteki
            'apteka', 'pharmacy', 'gemini', 'dbam o zdrowie', 'DOZ',
            'lek', 'leki', 'recepta', 'witaminy', 'suplementy',
            # Służba zdrowia
            'przychodnia', 'poradnia', 'szpital', 'klinika', 'lekarz',
            'dentysta', 'stomatolog', 'okulista', 'optyk', 'vision express',
            'ortodonta', 'protetyka',
            # Sport/wellness
            'siłownia', 'silownia', 'fitness', 'gym', 'fit', 'trening',
            'basen', 'pływalnia', 'plywalnia', 'spa', 'wellness', 
            'masaż', 'masaz', 'rehabilitacja', 'fizjoterapia', 'joga'
        ]
    }
    
    # Scoring system - zliczamy dopasowania
    category_matches = {cat: 0 for cat in categories}
    
    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword in description_lower:
                category_matches[category] += 1
    
    # Zwróć kategorię z największą liczbą dopasowań
    max_matches = max(category_matches.values())
    if max_matches > 0:
        for category, matches in category_matches.items():
            if matches == max_matches:
                return category
    
    # Jeśli żadne słowo nie pasuje
    return "Inne"


# Logowanie
def login_page():
    st.title("🔐 Logowanie - Budget Tracker")
    
    col1, col2, col3 = st.columns([1,2,1])
    
    with col2:
        username = st.text_input("Nazwa użytkownika")
        password = st.text_input("Hasło", type="password")
        
        if st.button("Zaloguj", use_container_width=True):
            if username == "admin" and password == "admin123":
                st.session_state.logged_in = True
                st.success("✅ Zalogowano pomyślnie!")
                st.rerun()
            else:
                st.error("❌ Błędne dane logowania")
        
        st.info("💡 Demo: admin / admin123")


# Główna aplikacja
def main_app():
    st.title("💰 Budget Tracker")
    st.caption("Powered by Groq Llama 3.3 70B 🤖")
    
    # Sidebar
    with st.sidebar:
        st.header("Menu")
        page = st.radio("Wybierz", ["📊 Dashboard", "➕ Dodaj transakcję", "📁 Import CSV", "📋 Historia", "🚪 Wyloguj"])
    
    # Dashboard
    if page == "📊 Dashboard":
        st.header("Dashboard")
        
        if len(st.session_state.transactions) == 0:
            st.info("Brak transakcji. Dodaj pierwszą transakcję!")
        else:
            df = pd.DataFrame(st.session_state.transactions)
            
            # Metryki
            col1, col2, col3 = st.columns(3)
            with col1:
                total = df['amount'].sum()
                st.metric("Suma wydatków", f"{total:.2f} zł")
            with col2:
                avg = df['amount'].mean()
                st.metric("Średnia transakcja", f"{avg:.2f} zł")
            with col3:
                count = len(df)
                st.metric("Liczba transakcji", count)
            
            # Wykresy
            st.subheader("Wydatki według kategorii")
            category_sum = df.groupby('category')['amount'].sum()
            st.bar_chart(category_sum)
            
            st.subheader("Wydatki w czasie")
            df['date'] = pd.to_datetime(df['date'])
            df_sorted = df.sort_values('date')
            st.line_chart(df_sorted.set_index('date')['amount'])
    
    # Dodaj transakcję
    elif page == "➕ Dodaj transakcję":
        st.header("Dodaj nową transakcję")
        
        description = st.text_input("Opis transakcji")
        amount = st.number_input("Kwota (zł)", min_value=0.0, step=0.01)
        date = st.date_input("Data", value=datetime.now())
        
        col1, col2 = st.columns(2)
        with col1:
            auto_categorize = st.checkbox("Automatyczna kategoryzacja AI", value=True)
        
        category = None
        if not auto_categorize:
            with col2:
                category = st.selectbox("Kategoria", ["Jedzenie", "Transport", "Rozrywka", "Dom", "Zdrowie", "Inne"])
        
        if st.button("💾 Zapisz transakcję"):
            if description and amount > 0:
                if auto_categorize:
                    with st.spinner("AI kategoryzuje..."):
                        category = categorize_with_ai(description)
                
                transaction = {
                    'id': st.session_state.next_id,
                    'date': str(date),
                    'description': description,
                    'amount': amount,
                    'category': category
                }
                
                st.session_state.transactions.append(transaction)
                st.session_state.next_id += 1
                
                st.success(f"✅ Dodano transakcję: {description} - {amount} zł (Kategoria: {category})")
            else:
                st.error("Wypełnij wszystkie pola!")
    
    # Import CSV
    elif page == "📁 Import CSV":
        st.header("Import transakcji z CSV")
        
        st.info("Format CSV: data,opis,kwota (bez nagłówka)")
        st.code("2024-11-13,Biedronka,150.50\n2024-11-12,Orlen,200.00")
        
        uploaded_file = st.file_uploader("Wybierz plik CSV", type=['csv'])
        
        if uploaded_file:
            try:
                df = pd.read_csv(uploaded_file, names=['date', 'description', 'amount'])
                
                st.dataframe(df)
                
                if st.button("🤖 Importuj z AI kategoryzacją"):
                    with st.spinner("Importuję i kategoryzuję..."):
                        for _, row in df.iterrows():
                            category = categorize_with_ai(row['description'])
                            
                            transaction = {
                                'id': st.session_state.next_id,
                                'date': str(row['date']),
                                'description': row['description'],
                                'amount': float(row['amount']),
                                'category': category
                            }
                            
                            st.session_state.transactions.append(transaction)
                            st.session_state.next_id += 1
                        
                        st.success(f"✅ Zaimportowano {len(df)} transakcji!")
                        st.rerun()
            except Exception as e:
                st.error(f"Błąd importu: {e}")
    
    # Historia
    elif page == "📋 Historia":
        st.header("Historia transakcji")
        
        if len(st.session_state.transactions) == 0:
            st.info("Brak transakcji")
        else:
            df = pd.DataFrame(st.session_state.transactions)
            
            # Filtr
            categories = ["Wszystkie"] + list(df['category'].unique())
            selected_category = st.selectbox("Filtruj kategorię", categories)
            
            if selected_category != "Wszystkie":
                df = df[df['category'] == selected_category]
            
            # Wyświetl tabelę
            st.dataframe(df, use_container_width=True)
            
            # Edycja/Usuwanie
            st.subheader("Zarządzaj transakcjami")
            
            transaction_ids = df['id'].tolist()
            selected_id = st.selectbox("Wybierz transakcję", transaction_ids)
            
            col1, col2 = st.columns(2)
            
            # UPDATE
            with col1:
                if st.button("✏️ Edytuj"):
                    transaction = next(t for t in st.session_state.transactions if t['id'] == selected_id)
                    st.session_state['editing'] = selected_id
            
            # DELETE
            with col2:
                if st.button("🗑️ Usuń"):
                    st.session_state.transactions = [t for t in st.session_state.transactions if t['id'] != selected_id]
                    st.success("Usunięto transakcję!")
                    st.rerun()
            
            # Formularz edycji
            if 'editing' in st.session_state and st.session_state['editing'] == selected_id:
                st.divider()
                st.subheader("Edytuj transakcję")
                
                transaction = next(t for t in st.session_state.transactions if t['id'] == selected_id)
                
                new_desc = st.text_input("Opis", value=transaction['description'])
                new_amount = st.number_input("Kwota", value=transaction['amount'])
                new_category = st.selectbox("Kategoria", 
                    ["Jedzenie", "Transport", "Rozrywka", "Dom", "Zdrowie", "Inne"],
                    index=["Jedzenie", "Transport", "Rozrywka", "Dom", "Zdrowie", "Inne"].index(transaction['category']))
                
                if st.button("💾 Zapisz zmiany"):
                    for t in st.session_state.transactions:
                        if t['id'] == selected_id:
                            t['description'] = new_desc
                            t['amount'] = new_amount
                            t['category'] = new_category
                    
                    del st.session_state['editing']
                    st.success("Zaktualizowano!")
                    st.rerun()
    
    # Wyloguj
    elif page == "🚪 Wyloguj":
        st.session_state.logged_in = False
        st.rerun()


# Main
if st.session_state.logged_in:
    main_app()
else:
    login_page()
