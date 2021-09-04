from peewee import *
from models import Person, Pet
from datetime import date


# uncle_bob = Person(name='Bob', birthday=date(1960, 1, 15))
# uncle_bob.save()
# # Returns: 1

# grandma = Person.create(name='Grandma', birthday=date(1935, 3, 1))
# herb = Person.create(name='Herb', birthday=date(1950, 5, 5))
# grandma.save()
# herb.save()

# bob_kitty = Pet.create(owner=uncle_bob, name='Kitty', animal_type='cat')
# herb_fido = Pet.create(owner=herb, name='Fido', animal_type='dog')
# herb_mittens = Pet.create(owner=herb, name='Mittens', animal_type='cat')
# herb_mittens_jr = Pet.create(owner=herb, name='Mittens Jr', animal_type='cat')

# row = herb_mittens.delete_instance()
# print(row)

# grandma = Person.select().where(Person.name == 'Grandma').get()
# grandma = Person.get(Person.name == "Grandma")
# print(grandma.name)

# for p in Person.select():
#     print(p.name)

# query = Pet.select().where(Pet.animal_type == 'cat')
# for pet in query:
#     print(pet.name, pet.owner.name)


# query = Pet.select(Pet, Person).join(Person).where(Pet.animal_type == 'cat')
#
# for pet in query:
#     print(pet.name, pet.owner.name)

#
# for pet in Pet.select().join(Person).where(Person.name == 'Herb'):
#     print(pet.name)

# uncle_bob = Person.select().where(Person.name == "Bob")
# for pet in Pet.select().where(Pet.owner == uncle_bob):
#     print(pet.name)

# uncle_bob = Person.select().where(Person.name == "Bob")
# for pet in Pet.select().where(Pet.owner == uncle_bob).order_by(Pet.name):
#     print(pet.name)


# 组合筛选器表达式
# d1940 = date(1940, 1, 1)
# d1960 = date(1960, 1, 1)
# # query = Person.select().where(Person.birthday > d1960 | Person.birthday < d1940)
# query = Person.select().where(Person.birthday.between(d1940, d1960))
# for person in query:
#     print(person.name , person.birthday)


# 聚合和预取
#列出所有人 and 他们有多少宠物：
# for person in Person.select():
#     print(person.name, person.pets.count(), 'pets')

# query = Person.select(Person, fn.COUNT(Pet.id).alias('pet_count')) \
#     .join(Pet, JOIN.LEFT_OUTER) \
#     .group_by(Person) \
#     .order_by(Person.name)
# for person in query:
#     print(person.name, person.pet_count, 'pets')

# query = (Person
#          .select(Person, Pet)
#          .join(Pet, JOIN.LEFT_OUTER)
#          .order_by(Person.name, Pet.name))
# for person in query:
#     if hasattr(person, 'pet'):
#         print(person.name, person.pet.name)
#     else:
#         print(person.name, 'no pets')

# query = Person.select().order_by(Person.name).prefetch(Pet)
# for person in query:
#     print(person.name)
#     print(person.pets)
#     for pet in person.pets:
#         print("  *", pet.name)


# SQL函数
exp = fn.Lower(fn.Substr(Person.name, 1, 1)) == 'g'
for person in Person.select().where(exp):
    print(person.name)
