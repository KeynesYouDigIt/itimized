from tastr import db
from tastr.models import *

'''add user examples king arthur and sir lancelot'''
Lance = User(username='Sir Lancelot',
             email='HolyHandGrenade15@camelot.org',
             password='camelot')
db.session.add(Lance)

Arthr = User(username='King Arthur',
             email='KingA@camelot.org',
             password='camelot')
db.session.add(Arthr)

db.session.commit()

'''add ingredients'''
spam = Ingredient(name="spam")
db.session.add(spam)
eggs = Ingredient(name="eggs")
db.session.add(eggs)
print spam
print eggs
db.session.commit()

'''add bookmarks'''

'author', 'id', 'instructions', 'name', 'nutrtion_facts', 'query', 'query_class', 'url'



spam_n_eggs = Recipe(author=Arthr.id,
                     instructions="mixem up gewd.",
                     name='spam n eggs',
                    _ingredients=[spam, eggs])

db.session.add(spam_n_eggs)

print spam_n_eggs

omlete = Recipe(author=Arthr.id,
                     instructions="i dont want ANY spam!",
                     name='omlete',
                    _ingredients=[eggs])
db.session.add(eggs)

print eggs

db.session.commit()


'''
Recipe.query.first()._ingredients[0]
'''