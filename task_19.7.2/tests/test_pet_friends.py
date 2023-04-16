import os
import sys
sys.path.insert(0, os.getcwd())

from api import PetFriends
from settings import valid_email, valid_password, invalid_email, invalid_password, whitespace

pf = PetFriends()


def test_get_api_key_for_valid_user(email=valid_email, password=valid_password):
    """ Проверяем что запрос api ключа возвращает статус 200 и в тезультате содержится слово key"""

    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
    status, result = pf.get_api_key(email, password)

    # Сверяем полученные данные с нашими ожиданиями
    assert status == 200
    assert 'key' in result





def test_get_all_pets_with_valid_key(filter=''):
    """ Проверяем что запрос всех питомцев возвращает не пустой список.
    Для этого сначала получаем api ключ и сохраняем в переменную auth_key. Далее используя этого ключ
    запрашиваем список всех питомцев и проверяем что список не пустой.
    Доступное значение параметра filter - 'my_pets' либо '' """

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)

    assert status == 200
    assert len(result['pets']) > 0


def test_add_new_pet_with_valid_data(name='Барбоскин', animal_type='двортерьер',
                                     age='4', pet_photo='images/cat1.jpg'):
    """Проверяем что можно добавить питомца с корректными данными"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name


def test_successful_delete_self_pet():
    """Проверяем возможность удаления питомца"""

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "Суперкот", "кот", "3", "images/cat1.jpg")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Берём id первого питомца из списка и отправляем запрос на удаление
    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.delete_pet(auth_key, pet_id)

    # Ещё раз запрашиваем список своих питомцев
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем что статус ответа равен 200 и в списке питомцев нет id удалённого питомца
    assert status == 200
    assert pet_id not in my_pets.values()


def test_successful_update_self_pet_info(name='Мурзик', animal_type='Котэ', age=5):
    """Проверяем возможность обновления информации о питомце"""

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Еслди список не пустой, то пробуем обновить его имя, тип и возраст
    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

        # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
        assert status == 200
        assert result['name'] == name
    else:
        # если спиок питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("There is no my pets")

def test_fails_always():
    assert False
# МОИ ТЕСТЫ
def test_add_and_read(capsys, name= 'Гриша', animal_type= 'поросенок', age = '5', pet_photo = 'images/P1040103.jpg'):
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)
    new_id = result['id']
    stat, res = pf.get_list_of_pets(auth_key)
    all_pets = res['pets']
    new_pets = list(filter(lambda p: p['id']== new_id, all_pets))
    assert len(new_pets) == 1 
    assert new_pets[0]['age'] == age
    assert new_pets[0]['name'] == name
    assert new_pets[0]['animal_type'] == animal_type

def test_delete_pet_with_nonexisting_id(id = '88888888888'):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    stat, res = pf.get_list_of_pets(auth_key)
    all_pets = res['pets']
    nonexisting_pets = list(filter(lambda p: p['id']== id, all_pets))
    assert len(nonexisting_pets)== 0
    status, _ = pf.delete_pet(auth_key, id)
    stat2, res2 = pf.get_list_of_pets(auth_key)
    all_pets2 = res2['pets']
    assert all_pets == all_pets2
    assert stat2 != 200
    assert stat2 != 403
    assert stat2 == 444 # TODO узнать код для неудаления

def test_delete_pet_with_empty_id():
    test_delete_pet_with_nonexisting_id('')

def test_delete_pet_with_bad_auth(capsys, name='Batman', animal_type = 'mouse', age = '20', pet_photo = 'images/cat1.jpg'):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)
    new_id = result['id']
    _, res = pf.get_list_of_pets(auth_key)
    all_pets = res['pets']
    with capsys.disabled():
        print('auth_key')
        print(auth_key)
    bad_auth = { 'key' : auth_key['key']+'a'}
    status1, _ = pf.delete_pet(bad_auth, new_id)
    _, res2 = pf.get_list_of_pets(auth_key)
    all_pets2 = res2['pets']
    status2, _ = pf.delete_pet(auth_key, new_id)
    assert all_pets == all_pets2
    assert status1 == 403
    assert status2 == 200


def test_add_same_animal_twice(name = 'Gena', animal_type='crocodile', age='8', pet_photo= 'images/cat1.jpg'): 
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    status1, result1 = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)
    new_id1 = result1['id']
    _, res = pf.get_list_of_pets(auth_key)
    all_pets1 = res['pets']
    status2, result2 = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)
    new_id2 = result2['id']
    _, res = pf.get_list_of_pets(auth_key)
    all_pets2 = res ['pets']
    new_pet1 = list(filter(lambda p: p['id']== new_id1, all_pets1))
    new_pet2 = list(filter(lambda p: p['id']== new_id2, all_pets2))

    _, _ = pf.delete_pet(auth_key, new_id1)
    _, _ = pf.delete_pet(auth_key, new_id2)

    assert status1 == 200
    assert status2 == 200
    assert len(new_pet1) == 1
    assert len(new_pet2) == 1
    assert new_pet1[0]['id'] != new_pet2[0]['id']
    assert new_pet1[0]['created_at'] != new_pet2[0]['created_at']

    del new_pet1[0]['id']
    del new_pet2[0]['id']
    del new_pet1[0]['created_at']
    del new_pet2[0]['created_at']
    assert new_pet1 == new_pet2

#def test_get_auth_key_with_incorrect_account():
def test_add_new_pet_with_bad_auth_key(name = 'Gena', animal_type='crocodile', age='8', pet_photo= 'images/cat1.jpg'):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    bad_auth = { 'key' : auth_key['key']+'a'}
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    status, result = pf.add_new_pet(bad_auth, name, animal_type, age, pet_photo)
    assert status == 403

def test_get_all_pets_with_invalid_key(capsys, filter = ''):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    bad_auth = { 'key' : auth_key['key']+'a'}
    status, result = pf.get_list_of_pets(bad_auth, filter)
    with capsys.disabled():
        print('res')
        print(result)

    assert status == 403 
    assert type(result) is str
#    assert len(result['pets']) == 0
    
def test_valid_user_with_whitespace(email = valid_email + whitespace, password = valid_password):
    #_, auth_key = pf.get_api_key(valid_email, password)
    test_get_api_key_for_valid_user(email, password)   

def test_get_api_key_for_invalid_user(email=invalid_email, password=invalid_password):
    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
    status, result = pf.get_api_key(email, password)

    # Сверяем полученные данные с нашими ожиданиями
    assert status == 403
    assert not('key' in result)

def test_get_api_key_for_valid_user_empty_password(email=valid_email, password=''):
    test_get_api_key_for_invalid_user(email, password)

def test_get_api_key_for_valid_user_invalid_password(email=valid_email, password=invalid_password):
    test_get_api_key_for_invalid_user(email, password)

def test_get_api_key_for_invalid_user_valid_password(email=invalid_email, password=valid_password):
    test_get_api_key_for_invalid_user(email, password)

def test_add_pet_simple_and_add_photo(capsys, name = 'Gena', animal_type='crocodile', age='8',pet_photo= 'images/cat1.jpg'):
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    status, result = pf.add_pet_simple(auth_key, name, animal_type, age)
    assert status == 200 and str(result).startswith("{")
    new_id = result['id']
    # если тест упал, животное остается в базе, это специально
    assert result['name'] == name
    assert result['animal_type'] == animal_type
    assert result['age'] == age

    _, res = pf.get_list_of_pets(auth_key)
    all_pets = res['pets']
    new_pet = list(filter(lambda p: p['id']== new_id, all_pets))

    assert len(new_pet) == 1
    assert new_pet[0]['name'] == name
    assert new_pet[0]['animal_type'] == animal_type
    assert new_pet[0]['pet_photo'] == ''
    
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    status2, result2 = pf.add_pet_photo(auth_key, new_id, pet_photo)
    assert status2 == 200
    
    _, res2 = pf.get_list_of_pets(auth_key)
    all_pets2 = res2['pets']
    new_pet = list(filter(lambda p: p['id']== new_id, all_pets2))

    assert len(new_pet) == 1
    assert new_pet[0]['name'] == name
    assert new_pet[0]['animal_type'] == animal_type
    assert new_pet[0]['age'] == age
    assert len(str(new_pet[0]['pet_photo'])) > 10
    
    status, _ = pf.delete_pet(auth_key, new_id)
    assert status == 200