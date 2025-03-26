import random
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol

import numpy
from scipy.stats import pearsonr
from tqdm import tqdm


@dataclass
class Card:
    features: dict[str, str | int]

    @property
    def content_id(self) -> int:
        return hash(str(self.features))


class Deck(Protocol):
    name: str

    def features(self) -> list[str]: ...

    def cards(self) -> list[Card]: ...


def measure_uniformity(cards: list[Card], features: list[str], verbose: bool = False) -> dict[str, float]:
    feature_uniformity = {}
    for feature in features:
        if verbose:
            print(feature)
        last_seen = defaultdict(int)
        distances = defaultdict(list)
        counts = defaultdict(int)
        for i, c in enumerate(cards):
            feature_value = c.features[feature]
            counts[feature_value] += 1
            if feature_value in last_seen:
                distance = i - last_seen[feature_value]
                distances[feature_value].append(distance)
            last_seen[feature_value] = i
        for f in distances:
            if verbose:
                print(f, distances[f], len(cards) / counts[f])
            distances[f] = [float(x) * counts[f] / len(cards) for x in distances[f]]
        max_ave = float("-inf")
        min_ave = float("inf")
        averaged_ave = 0
        weighted_average = 0
        for f in distances:
            ave_distance = sum(distances[f]) / len(distances[f])
            if ave_distance > max_ave:
                max_ave = ave_distance
            if ave_distance < min_ave:
                min_ave = ave_distance
            averaged_ave += ave_distance
            weighted_average += ave_distance * counts[f]
        averaged_ave /= len(distances)
        weighted_average /= len(cards)
        if verbose:
            print("Weighted average distance:", weighted_average)
            print("Feature-value averaged distance:", averaged_ave)
            print("Max distance:", max_ave)
            print("Min distance:", min_ave)
        feature_uniformity[feature] = weighted_average
    return feature_uniformity


def pairwise_distances(cards: list[Card]) -> dict[tuple[int, int], int]:
    distances = {}
    for i, card1 in enumerate(cards):
        for j, card2 in enumerate(cards):
            card1_id = id(card1)
            card2_id = id(card2)
            distance = i - j
            if card1_id > card2_id:
                card1_id, card2_id = card2_id, card1_id
                distance *= -1
            distances[card1_id, card2_id] = distance
    return distances


class BohnanzaDeck(Deck):
    def __init__(self) -> None:
        self.name = "Bohnanza Deck"
        self._cards: list[Card] = []
        for _ in range(24):
            self._cards.append(Card({"Name": "Coffee Bean"}))
        for _ in range(22):
            self._cards.append(Card({"Name": "Wax Bean"}))
        for _ in range(20):
            self._cards.append(Card({"Name": "Blue Bean"}))
        for _ in range(18):
            self._cards.append(Card({"Name": "Chili Bean"}))
        for _ in range(16):
            self._cards.append(Card({"Name": "Stink Bean"}))
        for _ in range(14):
            self._cards.append(Card({"Name": "Green Bean"}))
        for _ in range(12):
            self._cards.append(Card({"Name": "Soy Bean"}))
        for _ in range(10):
            self._cards.append(Card({"Name": "Black Eyed Bean"}))
        for _ in range(8):
            self._cards.append(Card({"Name": "Red Bean"}))

    def cards(self) -> list[Card]:
        return self._cards

    def features(self) -> list[str]:
        return ["Name"]


class PockerDeck(Deck):
    def __init__(self) -> None:
        self.name = "Pocker Deck"
        self._cards = []
        for i in range(1, 14):
            self._cards.append(Card({"Suit": "Spades", "Color": "Black", "Number": i}))
        for i in range(1, 14):
            self._cards.append(Card({"Suit": "Hearts", "Color": "Red", "Number": i}))
        for i in range(1, 14):
            self._cards.append(Card({"Suit": "Clubs", "Color": "Black", "Number": i}))
        for i in range(1, 14):
            self._cards.append(Card({"Suit": "Diamonds", "Color": "Red", "Number": i}))

    def cards(self) -> list[Card]:
        return self._cards

    def features(self) -> list[str]:
        return ["Suit", "Color", "Number"]


def base_shuffle(cards: list[Card]) -> list[Card]:
    cards = list(cards)
    random.shuffle(cards)
    return cards


def perfect_shuffle(cards: list[Card]) -> list[Card]:
    midpoint = len(cards) // 2
    first_half = cards[:midpoint]
    second_half = cards[midpoint:]
    new_cards = []
    for first_card, second_card in zip(first_half, second_half, strict=False):
        if first_card:
            new_cards.append(first_card)
        if second_card:
            new_cards.append(second_card)
    return new_cards


def imperfect_shuffle(cards: list[Card]) -> list[Card]:
    midpoint_percent = random.randint(40, 60) / 100  # PARAMETER!
    midpoint = int(len(cards) * midpoint_percent)
    first_half = cards[:midpoint]
    second_half = cards[midpoint:]
    i = 0
    j = 0
    new_cards = []
    while i < len(first_half) or j < len(second_half):
        if i < len(first_half):
            num_cards = random.randint(1, 4)  # PARAMETER!
            new_cards.extend(first_half[i : min(len(first_half), i + num_cards)])
            i = i + num_cards
        if j < len(second_half):
            num_cards = random.randint(1, 4)  # PARAMETER!
            new_cards.extend(second_half[j : min(len(second_half), j + num_cards)])
            j = j + num_cards
    return new_cards


def cut(cards: list[Card]) -> list[Card]:
    midpoint_percent = random.randint(10, 40) / 100  # PARAMETER!
    midpoint = int(len(cards) * midpoint_percent)
    first_half = cards[:midpoint]
    second_half = cards[midpoint:]
    return second_half + first_half


def multiple_shuffles(
    shuffle_fn: Callable[[list[Card]], list[Card]],
    num_shuffles: int,
) -> Callable[[list[Card]], list[Card]]:
    def composed_shuffle(cards: list[Card]) -> list[Card]:
        for _ in range(num_shuffles):
            cards = shuffle_fn(cards)
        return cards

    return composed_shuffle


def compose_shuffles(
    shuffle_fn1: Callable[[list[Card]], list[Card]],
    shuffle_fn2: Callable[[list[Card]], list[Card]],
) -> Callable[[list[Card]], list[Card]]:
    def composed_shuffle(cards: list[Card]) -> list[Card]:
        return shuffle_fn2(shuffle_fn1(cards))

    return composed_shuffle


def test_randomness(
    deck_cls: type[Deck],
    shuffle_fn: Callable[[list[Card]], list[Card]],
    name: str,
    num_runs: int = 1000,
) -> None:
    print(f"Testing {deck_cls.__name__} with shuffle_fn {name}")
    deck = deck_cls()
    cards = deck.cards()
    initial_distances = pairwise_distances(cards)
    correlations = []
    for _ in tqdm(range(num_runs)):
        shuffled_cards = shuffle_fn(cards)
        shuffled_distances = pairwise_distances(shuffled_cards)
        assert initial_distances.keys() == shuffled_distances.keys()
        before = []
        after = []
        for key in initial_distances:
            before.append(initial_distances[key])
            after.append(shuffled_distances[key])
        correlations.append(pearsonr(numpy.array(before), numpy.array(after)))
    average_correlation = sum(x.statistic for x in correlations) / len(correlations)
    average_pvalue = sum(x.pvalue for x in correlations) / len(correlations)
    print(average_correlation, average_pvalue)


def main() -> None:
    test_randomness(PockerDeck, base_shuffle, "python shuffle")
    print("\n\n")
    test_randomness(PockerDeck, perfect_shuffle, "perfect shuffle")
    test_randomness(PockerDeck, multiple_shuffles(perfect_shuffle, 2), "2 perfect shuffles")
    test_randomness(PockerDeck, multiple_shuffles(perfect_shuffle, 3), "3 perfect shuffles")
    test_randomness(PockerDeck, multiple_shuffles(perfect_shuffle, 4), "4 perfect shuffles")
    test_randomness(PockerDeck, multiple_shuffles(perfect_shuffle, 5), "5 perfect shuffles")
    test_randomness(PockerDeck, multiple_shuffles(perfect_shuffle, 6), "6 perfect shuffles")
    test_randomness(PockerDeck, multiple_shuffles(perfect_shuffle, 7), "7 perfect shuffles")
    test_randomness(PockerDeck, multiple_shuffles(perfect_shuffle, 8), "8 perfect shuffles")
    print("\n\n")
    test_randomness(PockerDeck, imperfect_shuffle, "imperfect shuffle")
    test_randomness(PockerDeck, multiple_shuffles(imperfect_shuffle, 2), "2 imperfect shuffles")
    test_randomness(PockerDeck, multiple_shuffles(imperfect_shuffle, 3), "3 imperfect shuffles")
    test_randomness(PockerDeck, multiple_shuffles(imperfect_shuffle, 4), "4 imperfect shuffles")
    test_randomness(PockerDeck, multiple_shuffles(imperfect_shuffle, 5), "5 imperfect shuffles")
    test_randomness(PockerDeck, multiple_shuffles(imperfect_shuffle, 6), "6 imperfect shuffles")
    test_randomness(PockerDeck, multiple_shuffles(imperfect_shuffle, 7), "7 imperfect shuffles")
    test_randomness(PockerDeck, multiple_shuffles(imperfect_shuffle, 8), "8 imperfect shuffles")
    print("\n\n")
    cut_then_shuffle = compose_shuffles(cut, imperfect_shuffle)
    test_randomness(PockerDeck, cut_then_shuffle, "cut then imperfect shuffle")
    test_randomness(PockerDeck, multiple_shuffles(cut_then_shuffle, 2), "cut then imperfect shuffle (2)")
    test_randomness(PockerDeck, multiple_shuffles(cut_then_shuffle, 3), "cut then imperfect shuffle (3)")
    test_randomness(PockerDeck, multiple_shuffles(cut_then_shuffle, 4), "cut then imperfect shuffle (4)")
    test_randomness(PockerDeck, multiple_shuffles(cut_then_shuffle, 5), "cut then imperfect shuffle (5)")
    test_randomness(PockerDeck, multiple_shuffles(cut_then_shuffle, 6), "cut then imperfect shuffle (6)")
    test_randomness(PockerDeck, multiple_shuffles(cut_then_shuffle, 7), "cut then imperfect shuffle (7)")
    test_randomness(PockerDeck, multiple_shuffles(cut_then_shuffle, 8), "cut then imperfect shuffle (8)")


if __name__ == "__main__":
    main()

# vim: et sw=4 sts=4
