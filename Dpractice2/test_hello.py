# Dpractice/test_hello.py

# def test_add():
#     assert 1 + 1 == 2
#
# def normal_function():
#     assert 1 == 2
#
# # def test_fail():
# #     assert 2 + 2 == 5
#
# def test_another():
#     assert True

def test_string():
    name = "hello"
    assert name.upper() == "HELLO"

def test_list():
    numbers = [1, 2, 3]
    assert 2 in numbers
    assert len(numbers) == 3

def test_dict():
    user = {"name": "Alice", "age": 25}
    assert user["name"] == "Alice"
    assert "email" not in user