# @Time    : 2021/5/29 20:00
# @Author  : wangyuchen
# @FileName: reason.py

from kanren import run, var
from kanren import Relation, facts


# 爷爷
def grandfather(grandson):
    someone = var()
    someone_son = var()
    return run(0, someone, father(someone, someone_son), father(someone_son, grandson))


# 奶奶
def grandmather(grandson):
    someone = var()
    someone_son = var()
    return run(0, someone, mather(someone, someone_son), mather(someone_son, grandson))


# 兄弟
def brother(one_person):
    one_father = var()
    one_mather = var()
    one_brother = var()
    return run(0, (one_person, one_brother), father(one_father, one_person), father(one_father, one_brother),)


if __name__ == '__main__':
    parent = Relation()
    facts(parent, ("Homer", "bart"), ("lmk", "Bart"), ("Homer", "Lisa"), ("Abe", "Homer"))
    x = var()

    res1 = run(0, x, parent(x, "Bart"))

    print(res1)

    father = Relation()
    mather = Relation()
    facts(father, ("f1", "f2"), ("f2", "f3"), ("f2", "f31"), ("f3", "f4"), ("f4", "f5"))

    facts(mather, ("m1", "m2"), ("m2", "m3"), ("m3", "m4"))

    one_grandson = input("你要找谁的爷爷？")
    grandfather1 = grandfather(one_grandson)
    print(grandfather1)

    one_person = input("你要找谁的兄弟？")
    borther1 = brother(one_person)
    print(borther1)

