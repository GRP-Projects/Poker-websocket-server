def valuate(hand):
    

def _royal_flush(hand):
    hand = set(hand)
    for suit in range(0, 4):
        ranges = set(range(8 + (13 * suit), 13 + (13 * suit)))
        if hand.issubset(ranges):
            return (10, suit)
    return None

def _straight_flush(hand)
    hand = sorted(list(hand))

    count = 1
    final_card = hand[0]

    for i in range(1, hand):
        if (i % 13 != 0) and (hand[i-1] == hand[i] - 1):
            count += 1
            final_card = hand[i]
        else:
            count = 1
    if count>=5:
        return (9, final_card)
    return None

def _four_of_a_kind(hand):
    