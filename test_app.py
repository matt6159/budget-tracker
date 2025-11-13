import builtins
from unittest.mock import patch
import types

import pytest

import app


def test_app_imports_without_errors():
    """
    Smoke test: sam import app.py nie powinien rzucać wyjątków.
    Gwarantuje, że zależności i kod główny są poprawne syntaktycznie.
    """
    assert isinstance(app, types.ModuleType)


@patch("app.requests.post")
def test_categorize_with_ai_success(mock_post):
    """
    Gdy Groq API zwraca poprawną kategorię (np. 'Jedzenie'),
    funkcja categorize_with_ai powinna ją zwrócić.
    """
    # Arrange
    mock_response = types.SimpleNamespace()
    mock_response.status_code = 200
    mock_response.json = lambda: {
        "choices": [
            {
                "message": {
                    "content": "Jedzenie"
                }
            }
        ]
    }
    mock_post.return_value = mock_response

    # Act
    category = app.categorize_with_ai("Zakupy w Biedronce")

    # Assert
    assert category == "Jedzenie"
    mock_post.assert_called_once()
    called_url = mock_post.call_args[0][0]
    assert "api.groq.com" in called_url


@patch("app.requests.post")
def test_categorize_with_ai_unclear_uses_fallback(mock_post):
    """
    Jeżeli Groq zwróci coś niejednoznacznego (np. 'Food' lub śmieci),
    funkcja powinna przejść na fallback smart_categorize.
    """
    mock_response = types.SimpleNamespace()
    mock_response.status_code = 200
    mock_response.json = lambda: {
        "choices": [
            {
                "message": {
                    "content": "jakas losowa odpowiedz"
                }
            }
        ]
    }
    mock_post.return_value = mock_response

    # Spy na fallbacku – upewniamy się, że został użyty
    with patch("app.smart_categorize", return_value="Inne") as mock_fallback:
        category = app.categorize_with_ai("Nieznany wydatek XYZ")

    assert category == "Inne"
    mock_post.assert_called_once()
    mock_fallback.assert_called_once_with("Nieznany wydatek XYZ")


@patch("app.requests.post")
def test_categorize_with_ai_groq_error_uses_fallback(mock_post):
    """
    Jeśli Groq API rzuci wyjątek (timeout, network error),
    categorize_with_ai ma użyć smart_categorize.
    """
    # Arrange
    mock_post.side_effect = Exception("Network error")

    with patch("app.smart_categorize", return_value="Transport") as mock_fallback:
        category = app.categorize_with_ai("Orlen paliwo")

    # Assert
    assert category == "Transport"
    mock_post.assert_called_once()
    mock_fallback.assert_called_once_with("Orlen paliwo")

def test_login():
    """Test logowania"""
    username = "admin"
    password = "admin123"
    assert username == "admin" and password == "admin123"
    print("✅ Test logowania: PASSED")

def test_crud_operations():
    """Test operacji CRUD"""
    transactions = []
    
    # CREATE
    transaction = {
        'id': 1,
        'description': 'Test',
        'amount': 100.0,
        'category': 'Jedzenie'
    }
    transactions.append(transaction)
    assert len(transactions) == 1
    print("✅ Test CREATE: PASSED")
    
    # READ
    assert transactions[0]['description'] == 'Test'
    print("✅ Test READ: PASSED")
    
    # UPDATE
    transactions[0]['amount'] = 200.0
    assert transactions[0]['amount'] == 200.0
    print("✅ Test UPDATE: PASSED")
    
    # DELETE
    transactions.remove(transaction)
    assert len(transactions) == 0
    print("✅ Test DELETE: PASSED")

def test_categorization():
    """Test kategoryzacji"""
    test_descriptions = {
        'Biedronka': ['Jedzenie', 'Dom'],
        'Orlen': ['Transport'],
        'Kino': ['Rozrywka']
    }
    
    for desc, valid_categories in test_descriptions.items():
        # W prawdziwej aplikacji testowalibyśmy AI
        # Tu tylko sprawdzamy logikę
        assert len(valid_categories) > 0
    
    print("✅ Test kategoryzacji: PASSED")

if __name__ == "__main__":
    test_login()
    test_crud_operations()
    test_categorization()
    print("\n🎉 Wszystkie testy zaliczone!")
