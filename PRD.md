Product Requirements Document (PRD)
Projekt: Budget Tracker
1. Wizja produktu
Budget Tracker to webowa aplikacja działająca w przeglądarce (Streamlit), która pozwala użytkownikowi ręcznie dodawać wydatki, wizualizować je na dashboardzie oraz automatycznie kategoryzować transakcje przy użyciu modelu Llama 3.3 70B udostępnianego przez Groq API.​
Produkt ma pomagać w szybkim ogarnianiu domowych finansów z minimalnym tarciem: użytkownik wpisuje opis typu „Biedronka zakupy na obiad” albo „Orlen paliwo”, a system sam wybiera kategorię z zamkniętej listy.​

2. Zakres i użytkownicy
Główny użytkownik: osoba prywatna chcąca śledzić swoje miesięczne wydatki w prostym narzędziu bez logowania do banku.​

Środowisko uruchomienia:

Lokalnie: streamlit run app.py na Pythonie.​

Chmura: Streamlit Community Cloud, z repozytorium na GitHub i sekretem GROQ_API_KEY ustawionym w „Secrets”.​

Zakres obejmuje:

Dodawanie, przeglądanie, filtrowanie, edycję i usuwanie transakcji w sesji użytkownika.​

Automatyczną kategoryzację opartą o Groq + fallback logiczny.​

3. Funkcje biznesowe
3.1. Logowanie (proste, demo)
Ekran logowania z prostym loginem/hasłem (admin / admin123), bez rejestracji i bez trwałej bazy użytkowników.​

Po zalogowaniu cała logika działa w st.session_state, bez zapisywania do DB czy plików.​

3.2. Dodawanie transakcji
Każda transakcja ma pola:​

date – data (DateInput).

description – tekstowy opis wydatku (np. „Biedronka zakupy”, „Orlen paliwo”).

amount – kwota typu float (PLN).

category – jedna z wartości: Jedzenie, Transport, Rozrywka, Dom, Zdrowie, Inne.​

Tryby dodawania:

Z automatyczną kategoryzacją AI (checkbox zaznaczony):

Aplikacja wywołuje funkcję categorize_with_ai(description), która korzysta z Groq API i modelu llama-3.3-70b-versatile.​

Bez AI (checkbox odznaczony):

Użytkownik ręcznie wybiera kategorię z selectbox.​

Transakcje są przetrzymywane w st.session_state.transactions jako lista słowników z polami id, date, description, amount, category.​

4. Integracja AI (Groq, nie OpenAI)
4.1. Architektura integracji
Brak lokalnego serwera modelu ani OpenAI.​

Bezpośrednie wywołanie HTTPS do Groq API z poziomu app.py (biblioteka requests).​

Klucz API Groq jest ładowany z GROQ_API_KEY (zmienna środowiskowa), a lokalnie z pliku .env poprzez python-dotenv.​

4.2. Wywołanie Groq w categorize_with_ai
Endpoint: https://api.groq.com/openai/v1/chat/completions.​

Model: llama-3.3-70b-versatile (multilingual, wysoka jakość, szybki inference na Groq).​

Prompt:

System:

„Jesteś ekspertem kategoryzacji wydatków domowych. Odpowiadasz TYLKO jednym słowem z listy: Jedzenie, Transport, Rozrywka, Dom, Zdrowie lub Inne. Rozumiesz kontekst i polskie nazwy produktów.”​

User:

Skategoryzuj wydatek: "{description}".​

Parametry:

temperature: około 0.3 (stabilne odpowiedzi).​

max_tokens: 10 (wystarczy na jedną kategorię).​

4.3. Walidacja odpowiedzi AI
Odpowiedź tekstowa z Groq jest przycinana i sprawdzana pod kątem zawartości którejś z kategorii: ["Jedzenie", "Transport", "Rozrywka", "Dom", "Zdrowie", "Inne"].​

Jeśli odpowiedź nie zawiera żadnej z tych etykiet, aplikacja używa fallbacku smart_categorize(description).​

4.4. Fallback smart_categorize
Prostą logika rules‑based opartą o listy słów kluczowych dla marek, sklepów, usług (Biedronka, Lidl, Orlen, Netflix, Ikea itd.).​

Fallback jest:

używany gdy:

Groq zwraca błąd (timeout, 401/403, brak klucza itp.),

lub odpowiedź AI nie pasuje do żadnej kategorii.​

5. UI i funkcje aplikacji
5.1. Struktura nawigacji w Streamlit
Sidebar z radio:

📊 Dashboard – widok podsumowania.​

➕ Dodaj transakcję – formularz dodawania.​

📁 Import CSV – wsadowe ładowanie transakcji.​

📋 Historia – przegląd, filtrowanie, edycja, usuwanie.​

🚪 Wyloguj – reset session_state.logged_in.​

5.2. Dashboard
Metryki KPI:

Suma wydatków: suma amount.​

Średnia wartość transakcji: mean(amount).​

Liczba transakcji.​

Wykresy:

Bar chart: suma kwot per category.​

Line chart: wydatki w czasie (index po date).​

5.3. Import CSV
Uploader akceptuje plik .csv w formacie bez nagłówka: data,opis,kwota.​

Dla każdej linii:

czytany jest wiersz do tabeli Pandas,

dla kolumny description wołane jest categorize_with_ai,

wpis trafia do transactions z nadanym id.​

5.4. Historia transakcji (CRUD)
Widok tabeli (DataFrame) z wszystkimi polami.​

Filtr po kategorii (selectbox z Wszystkie + unikaty z df['category']).​

Wybór transakcji po id i operacje:

Edytuj – formularz pozwala zmienić opis, kwotę, kategorię, zapisuje w session_state.transactions.​

Usuń – filtruje listę transakcji po id.​

6. Wymagania niefunkcjonalne
6.1. Wydajność i UX
Odpowiedź AI (Groq) powinna mieścić się w ok. 1–2 sekundach przy pojedynczym wywołaniu.​

Przy imporcie wielu transakcji aplikacja woła Groq sekwencyjnie; nie ma twardego SLA, ale UI używa st.spinner, żeby użytkownik widział postęp.​

6.2. Bezpieczeństwo
Żadnych kluczy API w kodzie ani w historii Git:

GROQ_API_KEY tylko w .env lokalnie i w Streamlit Secrets w chmurze.​

.env jest w .gitignore, więc nie trafia do repo.​

GitHub Secret Scanning / Push Protection musi przechodzić bez błędów (klucze nie mogą być wykrywane w commitach).​

6.3. Jakość i testy
test_app.py zawiera przynajmniej smoke‑testy:

Import modułu app.py bez wyjątku.​

Test prostych funkcji pomocniczych (np. smart_categorize()).​

CI/CD:

GitHub Actions workflow .github/workflows/test.yml:

checkout,

setup Python 3.11,

pip install -r requirements.txt,

pytest test_app.py -v.​

7. Technologia i zależności
Frontend / backend: Python + Streamlit.​

ML / AI: Groq API (Llama 3.3 70B Versatile) – wywołanie w stylu OpenAI Chat Completions.​

Biblioteki kluczowe:

streamlit – UI.​

pandas – tabela transakcji, agregacje.​

requests – HTTP do Groq.​

python-dotenv – ładowanie .env lokalnie.​

8. Deployment
8.1. GitHub
Repo: github.com/matt6159/budget-tracker.​

Branch produkcyjny: main.​

Pliki istotne:

app.py – główna aplikacja Streamlit.​

requirements.txt – zależności Pythona.​

test_app.py – testy.​

.github/workflows/test.yml – CI z pytest.​

.gitignore – wyklucza .env, __pycache__, itp.​

8.2. Streamlit Community Cloud
Konfiguracja aplikacji:

Repo: matt6159/budget-tracker.​

Branch: main.​

Main file: app.py.​

Sekrety (Settings → Secrets):

text
GROQ_API_KEY = "gsk_..."
Po każdym git push na main Streamlit automatycznie redeployuje aplikację.​

9. Kryteria akceptacji
Produkt można uznać za „done”, jeśli:​

Aplikacja działa lokalnie (streamlit run app.py) i w chmurze (Streamlit Cloud), w obu przypadkach z działającą kategoryzacją AI + fallback.​

Dodanie transakcji „Biedronka zakupy”, „bułka świeża”, „Orlen paliwo”, „Netflix abonament”, „IKEA meble” skutkuje logicznymi kategoriami przy automatycznej kategoryzacji.​

Import CSV wczytuje co najmniej 10 transakcji, wszystkie zostają skategoryzowane (AI lub fallback) i są widoczne w historii i dashboardzie.​

GitHub Actions workflow przechodzi zielono przy każdym pushu.​

GitHub nie blokuje pushów z powodu wykrycia sekretów; historia repo nie zawiera GROQ_API_KEY ani innych kluczy.​