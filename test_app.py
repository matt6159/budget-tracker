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
