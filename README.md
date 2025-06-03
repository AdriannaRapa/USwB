# 💻 CommitBoard – Personal Coding Task Manager

Projekt tworzony w ramach przedmiotu "Usługi sieciowe w biznesie".

## 📖 O Projekcie

CommitBoard to lekkie, spersonalizowane narzędzie umożliwiające automatyczne zarządzanie zadaniami programistycznymi w Notion, poprzez integrację z GitHubem. Projekt został stworzony z myślą o programistach pracujących indywidualnie – studentach, freelancerach oraz osobach realizujących własne projekty kodowe.

Początkowo zakładałam integrację Jiry z GitHubem 🔄, jednak Jira okazała się zbyt rozbudowana i nieintuicyjna w pracy solo 🙅‍♀️. Dlatego wybrałam Notion – elastyczne i nowoczesne środowisko no-code do zarządzania wiedzą i zadaniami 📝.

## 🎯 Cel Projektu

Ułatwienie zarządzania zadaniami osobom pracującym indywidualnie

Automatyzacja aktualizacji statusów zadań w Notion na podstawie commitów z GitHub

Ograniczenie konieczności ręcznego przełączania się między narzędziami

Lekka alternatywa dla rozbudowanych aplikacji webowych

## 🛠️ Technologie
🛰️ GitHub Webhooks – przesyłanie informacji o commitach

🗂️ Notion API – aktualizacja i tworzenie zadań w Notion

🌐 Replit – środowisko uruchomieniowe aplikacji

🐍 Python + Flask – backend obsługujący webhooki i API

## 📝 Własny Szablon w Notion
Stworzyłam własny szablon bazy zadań w Notion, który zawiera:

✅ Nazwa zadania, status, opis, autor, link do commita
📅 Deadline i czas aktualizacji
🏷️ Tagi, priorytet, typ zadania
📊 Widoki: tablica Kanban, kalendarz, oś czasu, tabela, wykresy statystyk

## 🚀 Funkcjonalność
🔄 Automatyczne przetwarzanie commitów z GitHuba

🔍 Wyszukiwanie lub tworzenie zadań w Notion na podstawie commitów

✅ Automatyczna zmiana statusu zadania na "Zrobione"

🔗 Dodawanie linku do commita, autora i opisu jako metadanych w zadaniu

## 🔧 Architektura i Działanie
Użytkownik wykonuje commit w GitHub z nazwą zadania w tytule.

GitHub wysyła webhook do aplikacji Flask na Replit.

Aplikacja:

znajduje zadanie po nazwie i aktualizuje je, lub

tworzy nowe zadanie w Notion na podstawie commita.

Wszystko odbywa się automatycznie – wystarczy commit!

## 💡 Przykładowe Rozszerzenia (planowane)
🔔 Powiadomienia przez Discord/Slack

📈 Raporty aktywności i statystyki commitów

📌 Nowe statusy zadań: "W trakcie", "Zablokowane", "Do sprawdzenia"

📆 Integracja z kalendarzem Google

## 🤔 Dlaczego Notion?
🎯 Proste, intuicyjne i konfigurowalne
📋 Idealne do tworzenia własnych workflowów
🧑‍💻 Świetne wsparcie API
🆓 Dostępne w wersji darmowej
🌐 Elastyczne rozwiązanie typu no-code dla każdego


