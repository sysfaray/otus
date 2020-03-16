#!/usr/bin/env python
# -*- coding: utf-8 -*-
import itertools


# -----------------
# Реализуйте функцию best_hand, которая принимает на вход
# покерную "руку" (hand) из 7ми карт и возвращает лучшую
# (относительно значения, возвращаемого hand_rank)
# "руку" из 5ти карт. У каждой карты есть масть(suit) и
# ранг(rank)
# Масти: трефы(clubs, C), пики(spades, S), червы(hearts, H), бубны(diamonds, D)
# Ранги: 2, 3, 4, 5, 6, 7, 8, 9, 10 (ten, T), валет (jack, J), дама (queen, Q), король (king, K), туз (ace, A)
# Например: AS - туз пик (ace of spades), TH - дестяка черв (ten of hearts), 3C - тройка треф (three of clubs)

# Задание со *
# Реализуйте функцию best_wild_hand, которая принимает на вход
# покерную "руку" (hand) из 7ми карт и возвращает лучшую
# (относительно значения, возвращаемого hand_rank)
# "руку" из 5ти карт. Кроме прочего в данном варианте "рука"
# может включать джокера. Джокеры могут заменить карту любой
# масти и ранга того же цвета, в колоде два джокерва.
# Черный джокер '?B' может быть использован в качестве треф
# или пик любого ранга, красный джокер '?R' - в качестве черв и бубен
# любого ранга.

# Одна функция уже реализована, сигнатуры и описания других даны.
# Вам наверняка пригодится itertools.
# Можно свободно определять свои функции и т.п.
# -----------------


def hand_rank(hand):
    """Возвращает значение определяющее ранг 'руки'"""
    ranks = card_ranks(hand)
    if straight(ranks) and flush(hand):
        return (8, max(ranks))
    elif kind(4, ranks):
        return (7, kind(4, ranks), kind(1, ranks))
    elif kind(3, ranks) and kind(2, ranks):
        return (6, kind(3, ranks), kind(2, ranks))
    elif flush(hand):
        return (5, ranks)
    elif straight(ranks):
        return (4, max(ranks))
    elif kind(3, ranks):
        return (3, kind(3, ranks), ranks)
    elif two_pair(ranks):
        return (2, two_pair(ranks), ranks)
    elif kind(2, ranks):
        return (1, kind(2, ranks), ranks)
    else:
        return (0, ranks)


def card_ranks(hand):
    """Возвращает список рангов (его числовой эквивалент),
    отсортированный от большего к меньшему"""
    ranks_list = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A', '?']
    ranks = []
    f_hand = []
    if flush(hand):
        res = [card[1] for card in hand]
        for f in set(res):
            if res.count(f) < 5:
                continue
            for h in hand:
                if f in h:
                    f_hand.append(h)
    if f_hand:
        hand = f_hand
    for x in hand:
        ranks.append(ranks_list.index(x[0]))
    return sorted(ranks, reverse=True)


def flush(hand):
    """Возвращает True, если все карты одной масти"""
    res = [card[1] for card in hand]
    for r in set(res):
        return res.count(r) >= 5


def straight(ranks):
    """Возвращает True, если отсортированные ранги формируют последовательность 5ти,
    где у 5ти карт ранги идут по порядку (стрит)"""
    ranks_set = list(set(ranks))
    res = []
    if len(ranks_set) < 5:
        return False
    for r in sorted(ranks_set):
        if res:
            if (res[-1] + 1) == r:
                res.append(r)
            else:
                if len(ranks_set) == 5:
                    return False
                res = [r]
        else:
            res.append(r)
    return len(res) >= 5



def kind(n, ranks):
    """Возвращает первый ранг, который n раз встречается в данной руке.
    Возвращает None, если ничего не найдено"""
    s_ranks = list(set(ranks))
    if len(s_ranks) == 3 and n != 4:
        s_ranks.remove(min(s_ranks))
    for rank in s_ranks:
        if ranks.count(rank) == n:
            return rank
    else:
        return None


def two_pair(ranks):
    """Если есть две пары, то возврщает два соответствующих ранга,
    иначе возвращает None"""
    result = []
    for rank in set(ranks):
        if ranks.count(rank) == 2:
            result.append(rank)
    if len(result) > 1:
        return result
    else:
        return None


def best_hand(hand):
    """Из "руки" в 7 карт возвращает лучшую "руку" в 5 карт """
    hands = hand_rank(hand)
    for el in itertools.combinations(hand, 5):
        if (hand_rank(el)) == hands:
            return list(el)


def joker_best_rank(hand, joker_dict):
    j_rank = []
    j_card = []
    if '?B' in hand and '?R' in hand:
        for j in joker_dict['B']:
            hand_b_new = hand[:]
            if j not in hand_b_new:
                hand_b_new[hand_b_new.index('?B')] = j
            for j in joker_dict['R']:
                hand_r_new = hand_b_new[:]
                if j not in hand_r_new:
                    hand_r_new[hand_r_new.index('?R')] = j
                j_card.append(hand_r_new)
                j_rank.append(hand_rank(hand_r_new))
    elif '?B' in hand:
        for j in joker_dict['B']:
            hand_b_new = hand[:]
            if j not in hand_b_new:
                hand_b_new[hand_b_new.index('?B')] = j
            j_rank.append(hand_rank(hand_b_new))
            j_card.append(hand_b_new)
    elif '?R' in hand:
        for j in joker_dict['R']:
            hand_r_new = hand[:]
            if j not in hand_r_new:
                hand_r_new[hand_r_new.index('?R')] = j
            j_rank.append(hand_rank(hand_r_new))
            j_card.append(hand_r_new)
    else:
        return j_rank, hand_rank(hand)
    return j_rank, j_card


def best_wild_joker_hand(j_rank, j_card):
    for card in j_card:
        for el in itertools.combinations(card, 5):
            if (hand_rank(el)) == j_rank:
                return list(el)


def best_wild_hand(hand):
    """best_hand но с джокерами"""
    suits = {'B': ['S', 'C'], 'R': ['H', 'D']}
    ranks_list = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
    joker_dict = {}
    for color in suits:
        cards = []
        for v in suits[color]:
            for rl in ranks_list:
                cards.append("%s%s" % (rl, v))
        joker_dict[color] = cards
    j_rank, j_card = joker_best_rank(hand, joker_dict)
    if j_rank:
        res = best_wild_joker_hand(max(j_rank), j_card)
    else:
        res = best_hand(hand)
    return res


def test_best_hand():
    print "test_best_hand..."
    assert (sorted(best_hand("6C 7C 8C 9C TC 5C JS".split()))
            == ['6C', '7C', '8C', '9C', 'TC'])
    assert (sorted(best_hand("TD TC TH 7C 7D 8C 8S".split()))
            == ['8C', '8S', 'TC', 'TD', 'TH'])
    assert (sorted(best_hand("JD TC TH 7C 7D 7S 7H".split()))
            == ['7C', '7D', '7H', '7S', 'JD'])
    print 'OK'


def test_best_wild_hand():
    print "test_best_wild_hand..."
    assert (sorted(best_wild_hand("6C 7C 8C 9C TC 5C ?B".split()))
            == ['7C', '8C', '9C', 'JC', 'TC'])
    assert (sorted(best_wild_hand("6H 7H 8H 9H TH 5H ?R".split()))
            == ['7H', '8H', '9H', 'JH', 'TH'])
    assert (sorted(best_wild_hand("TD TC 5H 5C 7C ?R ?B".split()))
            == ['7C', 'TC', 'TD', 'TH', 'TS'])
    assert (sorted(best_wild_hand("JD TC TH 7C 7D 7S 7H".split()))
            == ['7C', '7D', '7H', '7S', 'JD'])
    print 'OK'


if __name__ == '__main__':
    test_best_hand()
    test_best_wild_hand()
